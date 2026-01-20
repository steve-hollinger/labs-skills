"""Context building utilities."""

from dataclasses import dataclass, field
from typing import Callable

from episode_history.episode import Episode


@dataclass
class ContextConfig:
    """Configuration for context building.

    Attributes:
        max_tokens: Maximum tokens in context.
        use_summaries: Use summaries for closed episodes.
        include_current_full: Always include full current episode.
        max_episodes: Maximum number of episodes to include.
        separator: Separator between episodes.
    """

    max_tokens: int = 4000
    use_summaries: bool = True
    include_current_full: bool = True
    max_episodes: int = 10
    separator: str = "\n\n---\n\n"


TokenCounter = Callable[[str], int]
RelevanceScorer = Callable[[str, Episode], float]


def default_token_counter(text: str) -> int:
    """Default token counter (character-based estimate).

    Args:
        text: Text to count.

    Returns:
        Estimated token count.
    """
    return len(text) // 4


class ContextBuilder:
    """Builds context from episodes within token limits."""

    def __init__(
        self,
        config: ContextConfig | None = None,
        token_counter: TokenCounter | None = None,
        relevance_scorer: RelevanceScorer | None = None,
    ) -> None:
        """Initialize context builder.

        Args:
            config: Context configuration.
            token_counter: Function to count tokens.
            relevance_scorer: Function to score episode relevance.
        """
        self.config = config or ContextConfig()
        self.count_tokens = token_counter or default_token_counter
        self.score_relevance = relevance_scorer

    def build(
        self,
        episodes: list[Episode],
        current_query: str | None = None,
    ) -> str:
        """Build context from episodes.

        Args:
            episodes: Episodes to build context from.
            current_query: Optional current query for relevance scoring.

        Returns:
            Context string within token limits.
        """
        if not episodes:
            return ""

        # Limit episodes
        episodes = episodes[-self.config.max_episodes:]

        # Score and sort if relevance scorer available
        if self.score_relevance and current_query:
            episodes = self._sort_by_relevance(episodes, current_query)

        # Build context
        parts = []
        remaining_tokens = self.config.max_tokens

        # Process from newest to oldest (reverse order)
        for i, episode in enumerate(reversed(episodes)):
            is_current = i == 0 and episode.is_active

            # Get episode content
            content = self._format_episode(episode, is_current)
            tokens = self.count_tokens(content)

            # Check if fits
            if tokens > remaining_tokens:
                # Try to fit partial content
                truncated = self._truncate_to_fit(content, remaining_tokens)
                if truncated:
                    parts.insert(0, truncated)
                break

            parts.insert(0, content)
            remaining_tokens -= tokens

        return self.config.separator.join(parts)

    def build_with_system(
        self,
        episodes: list[Episode],
        system_message: str,
        current_query: str | None = None,
    ) -> list[dict[str, str]]:
        """Build context as message list with system message.

        Args:
            episodes: Episodes to include.
            system_message: System message to prepend.
            current_query: Optional current query.

        Returns:
            List of message dicts for LLM API.
        """
        messages = [{"role": "system", "content": system_message}]

        # Reserve tokens for system
        system_tokens = self.count_tokens(system_message)
        available = self.config.max_tokens - system_tokens

        # Build context with reduced budget
        original_max = self.config.max_tokens
        self.config.max_tokens = available

        context = self.build(episodes, current_query)

        self.config.max_tokens = original_max

        if context:
            messages.append({"role": "user", "content": f"Context:\n{context}"})

        return messages

    def _format_episode(self, episode: Episode, include_full: bool) -> str:
        """Format episode for context.

        Args:
            episode: Episode to format.
            include_full: Whether to include full messages.

        Returns:
            Formatted episode string.
        """
        if self.config.use_summaries and episode.is_closed and episode.summary:
            return f"[Previous: {episode.topic}]\n{episode.summary}"

        if include_full or not episode.summary:
            lines = [f"[{episode.topic}]"]
            for msg in episode.messages:
                lines.append(f"{msg.role}: {msg.content}")
            return "\n".join(lines)

        return f"[{episode.topic}]\n{episode.summary}"

    def _sort_by_relevance(
        self,
        episodes: list[Episode],
        query: str,
    ) -> list[Episode]:
        """Sort episodes by relevance to query.

        Args:
            episodes: Episodes to sort.
            query: Query for relevance scoring.

        Returns:
            Sorted episodes (most relevant first).
        """
        if not self.score_relevance:
            return episodes

        scored = [(e, self.score_relevance(query, e)) for e in episodes]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in scored]

    def _truncate_to_fit(self, content: str, max_tokens: int) -> str | None:
        """Truncate content to fit within token limit.

        Args:
            content: Content to truncate.
            max_tokens: Maximum tokens.

        Returns:
            Truncated content, or None if too small to be useful.
        """
        if max_tokens < 20:  # Too small to be useful
            return None

        # Binary search for right length
        low, high = 0, len(content)

        while low < high:
            mid = (low + high + 1) // 2
            if self.count_tokens(content[:mid]) <= max_tokens:
                low = mid
            else:
                high = mid - 1

        if low < 50:  # Too short
            return None

        return content[:low] + "..."


class RollingContextBuilder:
    """Builds context with rolling compression of old content."""

    def __init__(
        self,
        max_recent: int = 5,
        max_summaries: int = 10,
        token_counter: TokenCounter | None = None,
    ) -> None:
        """Initialize rolling context builder.

        Args:
            max_recent: Maximum recent messages to include full.
            max_summaries: Maximum episode summaries to include.
            token_counter: Function to count tokens.
        """
        self.max_recent = max_recent
        self.max_summaries = max_summaries
        self.count_tokens = token_counter or default_token_counter

    def build(
        self,
        episodes: list[Episode],
        max_tokens: int,
    ) -> str:
        """Build context with rolling compression.

        Args:
            episodes: All episodes.
            max_tokens: Maximum tokens.

        Returns:
            Context string.
        """
        if not episodes:
            return ""

        parts = []
        remaining = max_tokens

        # Active episode gets full messages
        active = [e for e in episodes if e.is_active]
        if active:
            current = active[0]
            recent_msgs = current.messages[-self.max_recent:]
            content = self._format_messages(recent_msgs)
            tokens = self.count_tokens(content)

            if tokens <= remaining:
                parts.append(content)
                remaining -= tokens

        # Closed episodes get summaries
        closed = [e for e in episodes if e.is_closed][-self.max_summaries:]

        for episode in reversed(closed):
            if episode.summary:
                content = f"[Earlier: {episode.topic}] {episode.summary}"
                tokens = self.count_tokens(content)

                if tokens > remaining:
                    break

                parts.insert(0, content)
                remaining -= tokens

        return "\n\n".join(parts)

    def _format_messages(self, messages: list) -> str:
        """Format messages for context.

        Args:
            messages: Messages to format.

        Returns:
            Formatted string.
        """
        return "\n".join(f"{m.role}: {m.content}" for m in messages)
