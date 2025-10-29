"""Interact with LeetCode to fetch problem and submission data.

This module uses LeetCode's public GraphQL API to retrieve information
about recent submissions and detailed problem metadata. Note that this API
is not officially supported and may change; consider caching results or
handling errors gracefully.
"""

from __future__ import annotations

import json
import time
from typing import List, Optional

import requests

from .types import LeetCodeProblem

_LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"


def _graphql_request(query: str, variables: dict) -> dict:
    """Send a GraphQL request to LeetCode and return the JSON response.

    Parameters
    ----------
    query: str
        The GraphQL query string.
    variables: dict
        Variables to send along with the query.

    Returns
    -------
    dict
        The decoded JSON data from the response.

    Raises
    ------
    RuntimeError
        If the request fails or returns an error.
    """
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "User-Agent": "LeetCodeTrackerAgent/1.0",
    }
    payload = {"query": query, "variables": variables}
    try:
        resp = requests.post(_LEETCODE_GRAPHQL_URL, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Failed to execute GraphQL request: {exc}") from exc
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data.get("data", {})


def get_recent_solved_problems(username: str, limit: int = 5) -> List[LeetCodeProblem]:
    """Retrieve recently solved problems for a given user.

    This function queries LeetCode's `recentSubmissionList` endpoint and
    filters for accepted submissions. It returns a list of unique problems
    represented as :class:`LeetCodeProblem` objects.

    Parameters
    ----------
    username: str
        The LeetCode username to query.
    limit: int, optional
        Maximum number of recent submissions to inspect. Defaults to 5.

    Returns
    -------
    List[LeetCodeProblem]
        A list of problems the user recently solved, each with basic
        metadata. Additional details can be fetched via
        :func:`get_problem_details`.
    """
    query = """
    query recentSubmissionList($username: String!, $limit: Int!) {
      recentSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
        statusDisplay
        lang
      }
    }
    """
    variables = {"username": username, "limit": limit}
    data = _graphql_request(query, variables)
    submissions = data.get("recentSubmissionList", [])
    problems: List[LeetCodeProblem] = []
    seen = set()
    for sub in submissions:
        # Only consider accepted submissions
        status = sub.get("statusDisplay", "").lower()
        if "accept" not in status:
            continue
        slug = sub.get("titleSlug")
        title = sub.get("title")
        if not slug or not title or slug in seen:
            continue
        seen.add(slug)
        # Create problem object with minimal info; details will be filled later
        problems.append(
            LeetCodeProblem(
                title=title,
                slug=slug,
                difficulty="",  # filled by get_problem_details
                tags=[],  # filled by get_problem_details
                url=f"https://leetcode.com/problems/{slug}/",
            )
        )
    return problems


def get_problem_details(slug: str) -> Optional[tuple[LeetCodeProblem, str]]:
    """Fetch detailed information and description about a LeetCode problem.

    Parameters
    ----------
    slug: str
        The LeetCode problem slug (e.g. "two-sum").

    Returns
    -------
    Optional[tuple[LeetCodeProblem, str]]
        A tuple containing a populated :class:`LeetCodeProblem` instance
        and the HTML description of the problem. Returns ``None`` if the
        problem could not be retrieved.
    """
    query = """
    query question($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        titleSlug
        difficulty
        content
        topicTags {
          name
        }
      }
    }
    """
    variables = {"titleSlug": slug}
    data = _graphql_request(query, variables)
    q = data.get("question")
    if not q:
        return None
    tags = [tag.get("name") for tag in (q.get("topicTags") or [])]
    problem = LeetCodeProblem(
        title=q.get("title"),
        slug=q.get("titleSlug"),
        difficulty=q.get("difficulty"),
        tags=tags,
        url=f"https://leetcode.com/problems/{q.get('titleSlug')}/",
    )
    description_html = q.get("content", "")
    return (problem, description_html)