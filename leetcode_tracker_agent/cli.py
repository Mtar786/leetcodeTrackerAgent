"""Command‑line interface for the LeetCode Tracker Agent.

This CLI orchestrates the workflow of retrieving recently solved LeetCode
problems for a user, generating concise summaries via OpenAI, and updating
both a Google Doc and an Anki deck with the results.

Typical usage::

    python -m leetcode_tracker_agent.cli \
        --username your_leetcode_username \
        --limit 3 \
        --doc-id <google_doc_id> \
        --service-account-key path/to/service-account.json \
        --anki-deck "LeetCode" \
        --openai-key sk-... 

Run ``python -m leetcode_tracker_agent.cli --help`` for a full list of
options and their descriptions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .leetcode_api import get_recent_solved_problems, get_problem_details
from .summary import summarize_problem
from .google_docs import append_to_doc
from .anki_deck import ensure_deck_exists, add_note_to_anki
from .types import LeetCodeProblem


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Track your solved LeetCode problems, generate summaries, and update "
            "a Google Doc and Anki deck."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--username",
        required=True,
        help="LeetCode username to query",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of recent solved problems to process",
    )
    parser.add_argument(
        "--doc-id",
        help="Google Doc ID to append summaries to",
    )
    parser.add_argument(
        "--service-account-key",
        dest="service_account_key",
        help=(
            "Path to a Google service account JSON key file for authenticating "
            "with the Docs API. If omitted, the Docs step is skipped."
        ),
    )
    parser.add_argument(
        "--anki-deck",
        dest="anki_deck",
        help=(
            "Name of the Anki deck to add cards to. If omitted, no Anki cards "
            "will be created."
        ),
    )
    parser.add_argument(
        "--anki-model",
        dest="anki_model",
        default="Basic",
        help="Anki note model name to use for cards",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="Additional tags to add to Anki notes",
    )
    parser.add_argument(
        "--openai-key",
        dest="openai_key",
        help="OpenAI API key used for summarisation. Required for summary step.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=400,
        help="Maximum number of tokens for each summary",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature for summary generation",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # Retrieve recent solved problems
    try:
        problems = get_recent_solved_problems(args.username, args.limit)
    except Exception as exc:
        parser.error(f"Failed to retrieve recent problems: {exc}")

    if not problems:
        print("No recently solved problems found.")
        return 0

    # Prepare Google Docs credentials if provided
    docs_credentials = None
    if args.doc_id and args.service_account_key:
        try:
            from google.oauth2.service_account import Credentials  # type: ignore
        except Exception:
            parser.error(
                "google-auth and google-api-python-client must be installed to use Google Docs features."
            )
        scopes = ["https://www.googleapis.com/auth/documents"]
        try:
            docs_credentials = Credentials.from_service_account_file(args.service_account_key, scopes=scopes)
        except Exception as exc:
            parser.error(f"Failed to load service account credentials: {exc}")
    elif args.doc_id or args.service_account_key:
        parser.error("Both --doc-id and --service-account-key must be provided to enable Google Docs updates.")

    # Prepare Anki deck
    if args.anki_deck:
        try:
            ensure_deck_exists(args.anki_deck)
        except Exception as exc:
            parser.error(f"Failed to ensure Anki deck exists: {exc}")

    # Process each problem
    for problem in problems:
        # Fetch detailed metadata
        details = get_problem_details(problem.slug)
        if details is None:
            print(f"Warning: Could not fetch details for {problem.title}")
            detailed_problem = problem  # fallback to minimal info
            description_html = ""
        else:
            detailed_problem, description_html = details
        # At this point, summary_tags could be used to influence summarisation or tagging,
        # but the current implementation does not make use of it.
        # Summarise problem using OpenAI
        if args.openai_key:
            try:
                summary_result = summarize_problem(
                    detailed_problem,
                    description_html,
                    model="gpt-4-turbo",
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    openai_api_key=args.openai_key,
                )
            except Exception as exc:
                parser.error(f"Failed to summarise problem {problem.title}: {exc}")
        else:
            summary_result = None

        # If we don't have an OpenAI key, skip summary and just include the title
        summary_text = summary_result.summary if summary_result else problem.title

        # Append to Google Doc
        if docs_credentials and args.doc_id:
            try:
                # We use detailed_problem.difficulty if available; else fallback to problem.difficulty
                difficulty = detailed_problem.difficulty if isinstance(detailed_problem, LeetCodeProblem) else problem.difficulty
                text_to_append = f"\n### {problem.title} ({difficulty})\n"
                text_to_append += f"URL: {problem.url}\n\n"
                text_to_append += f"Summary:\n{summary_text}\n"
                append_to_doc(args.doc_id, text_to_append, docs_credentials)
                print(f"Appended summary for {problem.title} to Google Doc.")
            except Exception as exc:
                parser.error(f"Failed to append to Google Doc: {exc}")

        # Add to Anki deck
        if args.anki_deck:
            try:
                difficulty = detailed_problem.difficulty if isinstance(detailed_problem, LeetCodeProblem) else problem.difficulty
                front = f"{problem.title} ({difficulty})"
                back = f"{summary_text}\n\nURL: {problem.url}"
                add_note_to_anki(
                    args.anki_deck,
                    args.anki_model,
                    front,
                    back,
                    tags=args.tags,
                )
                print(f"Added {problem.title} to Anki deck '{args.anki_deck}'.")
            except Exception as exc:
                parser.error(f"Failed to add note to Anki: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())