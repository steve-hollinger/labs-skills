"""Episode summarization strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Awaitable

from episode_history.episode import Episode, Message


class Summarizer(ABC):
    """Abstract base for episode summarizers."""

    @abstractmethod
    async def summarize(self, episode: Episode) -> str:
        """Generate a summary for an episode.

        Args:
            episode: The episode to summarize.

        Returns:
            Summary string.
        """
        pass


class SimpleSummarizer(Summarizer):
    """Simple extractive summarizer without LLM.

    Uses first and last messages to create summary.
    """

    def __init__(self, max_length: int = 200) -> None:
        """Initialize the summarizer.

        Args:
            max_length: Maximum summary length in characters.
        """
        self.max_length = max_length

    async def summarize(self, episode: Episode) -> str:
        """Generate summary from key messages.

        Args:
            episode: The episode to summarize.

        Returns:
            Extractive summary.
        """
        if not episode.messages:
            return "Empty conversation."

        if len(episode.messages) == 1:
            return self._truncate(episode.messages[0].content)

        # Get first user message and last assistant message
        first_user = None
        last_assistant = None

        for msg in episode.messages:
            if msg.role == "user" and not first_user:
                first_user = msg
            if msg.role == "assistant":
                last_assistant = msg

        parts = []
        if first_user:
            parts.append(f"User asked about: {self._truncate(first_user.content, 80)}")
        if last_assistant:
            parts.append(f"Concluded with: {self._truncate(last_assistant.content, 80)}")

        summary = " ".join(parts) if parts else "General conversation."
        return self._truncate(summary)

    def _truncate(self, text: str, max_len: int | None = None) -> str:
        """Truncate text to maximum length.

        Args:
            text: Text to truncate.
            max_len: Maximum length (defaults to self.max_length).

        Returns:
            Truncated text.
        """
        limit = max_len or self.max_length
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."


LLMFunction = Callable[[str], Awaitable[str]]


@dataclass
class LLMSummarizerConfig:
    """Configuration for LLM-based summarization.

    Attributes:
        style: Summary style (concise, detailed, bullet).
        max_tokens: Maximum tokens in summary.
        include_topic: Whether to include topic in prompt.
    """

    style: str = "concise"
    max_tokens: int = 100
    include_topic: bool = True


class LLMSummarizer(Summarizer):
    """LLM-based episode summarizer."""

    def __init__(
        self,
        llm_function: LLMFunction,
        config: LLMSummarizerConfig | None = None,
    ) -> None:
        """Initialize with LLM function.

        Args:
            llm_function: Async function to call LLM.
            config: Summarization configuration.
        """
        self.llm = llm_function
        self.config = config or LLMSummarizerConfig()

    async def summarize(self, episode: Episode) -> str:
        """Generate summary using LLM.

        Args:
            episode: The episode to summarize.

        Returns:
            LLM-generated summary.
        """
        if not episode.messages:
            return "Empty conversation."

        if len(episode.messages) <= 2:
            # Short episodes don't need LLM
            return self._format_short(episode)

        prompt = self._build_prompt(episode)
        return await self.llm(prompt)

    def _format_short(self, episode: Episode) -> str:
        """Format short episodes without LLM.

        Args:
            episode: Short episode.

        Returns:
            Simple formatted summary.
        """
        parts = []
        for msg in episode.messages:
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            parts.append(f"{msg.role}: {content}")
        return " | ".join(parts)

    def _build_prompt(self, episode: Episode) -> str:
        """Build summarization prompt.

        Args:
            episode: Episode to summarize.

        Returns:
            Prompt string for LLM.
        """
        messages_text = "\n".join(
            f"{m.role}: {m.content}" for m in episode.messages
        )

        topic_line = f"Topic: {episode.topic}\n" if self.config.include_topic else ""

        style_instruction = {
            "concise": "Create a brief 2-3 sentence summary.",
            "detailed": "Create a comprehensive summary covering all key points.",
            "bullet": "Create a bullet-point summary of key information.",
        }.get(self.config.style, "Create a summary.")

        return f"""Summarize this conversation:
{topic_line}
{messages_text}

{style_instruction}

Include:
- Main topic or question
- Key decisions or conclusions
- Any action items or next steps

Maximum {self.config.max_tokens} tokens."""


class HierarchicalSummarizer(Summarizer):
    """Summarizer that creates hierarchical summaries.

    Creates progressively compressed summaries for different age tiers.
    """

    def __init__(
        self,
        base_summarizer: Summarizer,
        compression_levels: int = 3,
    ) -> None:
        """Initialize hierarchical summarizer.

        Args:
            base_summarizer: Underlying summarizer to use.
            compression_levels: Number of compression levels.
        """
        self.base = base_summarizer
        self.levels = compression_levels

    async def summarize(self, episode: Episode) -> str:
        """Generate standard summary.

        Args:
            episode: Episode to summarize.

        Returns:
            Base-level summary.
        """
        return await self.base.summarize(episode)

    async def summarize_multiple(
        self,
        episodes: list[Episode],
        level: int = 1,
    ) -> str:
        """Summarize multiple episodes together.

        Args:
            episodes: Episodes to summarize.
            level: Compression level (higher = more compressed).

        Returns:
            Combined summary.
        """
        if not episodes:
            return ""

        if len(episodes) == 1:
            return await self.summarize(episodes[0])

        # Collect summaries
        summaries = []
        for ep in episodes:
            if ep.summary:
                summaries.append(f"[{ep.topic}]: {ep.summary}")
            else:
                summary = await self.summarize(ep)
                summaries.append(f"[{ep.topic}]: {summary}")

        # For now, just join them
        # A real implementation would use LLM to compress further
        return " | ".join(summaries)


class BatchSummarizer:
    """Processes multiple episodes for summarization."""

    def __init__(self, summarizer: Summarizer) -> None:
        """Initialize batch summarizer.

        Args:
            summarizer: Summarizer to use for each episode.
        """
        self.summarizer = summarizer

    async def summarize_batch(
        self,
        episodes: list[Episode],
        skip_with_summary: bool = True,
    ) -> dict[str, str]:
        """Summarize multiple episodes.

        Args:
            episodes: Episodes to summarize.
            skip_with_summary: Skip episodes that already have summaries.

        Returns:
            Dictionary mapping episode ID to summary.
        """
        results: dict[str, str] = {}

        for episode in episodes:
            if skip_with_summary and episode.summary:
                results[episode.id] = episode.summary
                continue

            summary = await self.summarizer.summarize(episode)
            results[episode.id] = summary

        return results

    async def summarize_and_update(
        self,
        episodes: list[Episode],
    ) -> int:
        """Summarize episodes and update them in place.

        Args:
            episodes: Episodes to summarize.

        Returns:
            Number of episodes updated.
        """
        updated = 0

        for episode in episodes:
            if episode.summary:
                continue

            summary = await self.summarizer.summarize(episode)
            episode.summary = summary
            updated += 1

        return updated
