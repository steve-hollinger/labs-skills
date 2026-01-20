"""Exercise 2: Create a Leaderboard System.

In this exercise, you will build a leaderboard system using sorted sets
for game rankings with real-time updates.

Requirements:
1. Create a Leaderboard class with:
   - add_score(player_id, score) - add or update score
   - increment_score(player_id, amount) - increment existing score
   - get_rank(player_id) -> int | None - get player's rank (1-indexed)
   - get_score(player_id) -> float | None - get player's score
   - get_top(n) -> list of (player_id, score) tuples
   - get_around(player_id, n) -> list of nearby players
   - remove_player(player_id) -> bool
   - get_total_players() -> int

2. Support multiple leaderboards (daily, weekly, all-time)

3. Implement score decay (optional bonus)

Run with: python exercises/exercise_2.py
Test with: pytest tests/test_exercises.py -k exercise_2
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import redis


@dataclass
class LeaderboardEntry:
    """A single leaderboard entry."""

    rank: int
    player_id: str
    score: float


class Leaderboard:
    """Leaderboard using Redis sorted sets.

    TODO: Implement this class using ZADD, ZREVRANK, ZSCORE, etc.
    """

    def __init__(
        self,
        client: redis.Redis[str],
        name: str = "leaderboard",
    ) -> None:
        """Initialize leaderboard.

        TODO: Store client and leaderboard name
        """
        pass

    def add_score(self, player_id: str, score: float) -> None:
        """Add or update a player's score.

        TODO: Use ZADD to set the score
        """
        pass

    def increment_score(self, player_id: str, amount: float) -> float:
        """Increment a player's score.

        TODO: Use ZINCRBY and return new score
        """
        pass

    def get_rank(self, player_id: str) -> int | None:
        """Get player's rank (1-indexed, 1 = top).

        TODO: Use ZREVRANK and add 1 (since it's 0-indexed)
        """
        pass

    def get_score(self, player_id: str) -> float | None:
        """Get player's score.

        TODO: Use ZSCORE
        """
        pass

    def get_top(self, n: int = 10) -> List[LeaderboardEntry]:
        """Get top N players.

        TODO:
        1. Use ZREVRANGE with withscores=True
        2. Return list of LeaderboardEntry with correct ranks
        """
        pass

    def get_around(
        self,
        player_id: str,
        n: int = 2,
    ) -> List[LeaderboardEntry]:
        """Get N players above and below the given player.

        TODO:
        1. Get player's rank
        2. Calculate range (rank - n to rank + n)
        3. Use ZREVRANGE for that range
        4. Return list of LeaderboardEntry
        """
        pass

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the leaderboard.

        TODO: Use ZREM
        """
        pass

    def get_total_players(self) -> int:
        """Get total number of players.

        TODO: Use ZCARD
        """
        pass


def main() -> None:
    """Demonstrate the leaderboard system."""
    print("Exercise 2: Leaderboard System")
    print("=" * 40)

    # TODO: Implement the demonstration
    #
    # 1. Connect to Redis
    # 2. Create a Leaderboard
    # 3. Add some players with scores
    # 4. Display top 5 players
    # 5. Get a specific player's rank
    # 6. Show players around position #5
    # 7. Increment a player's score
    # 8. Show updated rankings
    #
    # Example players:
    # - alice: 1500
    # - bob: 2000
    # - charlie: 1800
    # - diana: 2200
    # - eve: 1600
    # - frank: 1900
    # - grace: 2100

    print("\nNot implemented yet. See TODO comments.")


if __name__ == "__main__":
    main()
