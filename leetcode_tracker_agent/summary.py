"""Summarisation utilities for LeetCode problems.

This module provides functions to generate concise summaries of problem
statements using OpenAI's language models. A summary aims to distil
the problem requirements, constraints, and key solution ideas into a
few sentences. It can optionally include high‑level solution notes.

The summariser assumes that you have registered for an OpenAI API key
and have installed the ``openai`` Python package. You can obtain an API
key at https://openai.com/api/ and install the library via
``pip install openai``.
"""

from __future__ import annotations

from typing import Optional

import importlib

from .types import LeetCodeProblem, ProblemSummary


def summarize_problem(
    problem: LeetCodeProblem,
    description: str,
    *,
    model: str = "gpt-4-turbo",
    temperature: float = 0.3,
    max_tokens: int = 400,
    openai_api_key: Optional[str] = None,
) -> ProblemSummary:
    """Generate a short summary for a LeetCode problem description.

    Parameters
    ----------
    problem: LeetCodeProblem
        The problem metadata used for context and to construct the summary.
    description: str
        The HTML content of the problem statement.
    model: str, optional
        OpenAI model identifier. Defaults to ``gpt-4-turbo``.
    temperature: float, optional
        Sampling temperature used for generation. Defaults to ``0.3``.
    max_tokens: int, optional
        Maximum tokens allowed in the summary response. Defaults to ``400``.
    openai_api_key: Optional[str], optional
        Explicit API key used to authenticate with OpenAI. If not provided,
        the ``OPENAI_API_KEY`` environment variable must be set.

    Returns
    -------
    ProblemSummary
        A dataclass containing the problem and its summary.

    Raises
    ------
    RuntimeError
        If the ``openai`` package is not installed or no API key is provided.
    """
    try:
        openai = importlib.import_module("openai")
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required to summarise problems. "
            "Install it with 'pip install openai'."
        ) from exc

    api_key = openai_api_key or openai.api_key or None
    if not api_key:
        raise RuntimeError(
            "No OpenAI API key provided. Set the OPENAI_API_KEY environment "
            "variable or pass 'openai_api_key' to summarize_problem()."
        )
    openai.api_key = api_key

    # Convert HTML description to plain text by removing tags. We'll use a
    # simple fallback if BeautifulSoup is not installed. This keeps the
    # summarisation input focused on the problem statement itself.
    try:
        bs4 = importlib.import_module("bs4")
        soup = bs4.BeautifulSoup(description, "html.parser")
        plain_text = soup.get_text(separator="\n")
    except ImportError:
        # naive fallback: strip tags by removing text inside angle brackets
        import re
        plain_text = re.sub(r"<[^>]+>", " ", description)

    system_prompt = (
        "You are an AI assistant that summarises programming challenges. "
        "Given the plain text of a LeetCode problem description, generate "
        "a succinct summary that captures the problem statement, key "
        "constraints, and overall goal. Do not include implementation code."
    )
    user_content = (
        f"Problem Title: {problem.title}\n"
        f"Difficulty: {problem.difficulty}\n"
        f"Tags: {', '.join(problem.tags)}\n\n"
        f"Description:\n{plain_text}\n\n"
        "Summarise the problem in a few sentences."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
    )
    summary_text = response.choices[0].message.content.strip()
    return ProblemSummary(problem=problem, summary=summary_text)