"""Data models for the LeetCode Tracker Agent.

These dataclasses encapsulate LeetCode problem metadata and summarisation
results. Using structured types makes it easier to interact with the other
components of the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LeetCodeProblem:
    """Represents a LeetCode problem.

    Attributes
    ----------
    title: str
        The human‑readable problem title (e.g. "Two Sum").
    slug: str
        The URL slug used to identify the problem (e.g. "two-sum").
    difficulty: str
        Problem difficulty such as "Easy", "Medium" or "Hard".
    tags: List[str]
        A list of topic tags associated with the problem.
    url: str
        Full URL to the problem on leetcode.com.
    """

    title: str
    slug: str
    difficulty: str
    tags: List[str]
    url: str


@dataclass
class ProblemSummary:
    """Stores a summary of a LeetCode problem.

    Attributes
    ----------
    problem: LeetCodeProblem
        The underlying LeetCode problem.
    summary: str
        A concise description of the problem and key solution insights.
    solution_notes: Optional[str]
        Additional notes or explanation of the solution (optional).
    """

    problem: LeetCodeProblem
    summary: str
    solution_notes: Optional[str] = None