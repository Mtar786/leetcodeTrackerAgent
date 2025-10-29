"""Utilities for interacting with Google Docs.

This module provides functions to append text to an existing Google Doc.
It relies on the ``google-api-python-client`` and ``google-auth`` libraries
to authenticate and send requests. You need to configure your Google Cloud
project, enable the Docs API, and create credentials (either OAuth client
credentials for user consent or a service account) before using this module.

For more information, see the official documentation:
https://developers.google.com/docs/api
"""

from __future__ import annotations

from typing import Any

try:
    from googleapiclient.discovery import build  # type: ignore
except Exception:
    build = None  # type: ignore[assignment]


def append_to_doc(doc_id: str, text: str, credentials: Any) -> None:
    """Append text to the end of an existing Google Doc.

    Parameters
    ----------
    doc_id: str
        The ID of the Google Document (found in its URL).
    text: str
        The text to append. Line breaks and formatting will be preserved.
    credentials: Any
        A Google auth credentials object. This can be obtained via
        ``google.oauth2.service_account.Credentials.from_service_account_file``
        for service accounts or via OAuth flows.

    Raises
    ------
    RuntimeError
        If the Google client library is not installed.
    """
    if build is None:
        raise RuntimeError(
            "The google-api-python-client library is required for Google Docs support. "
            "Install it with 'pip install google-api-python-client google-auth'."
        )
    # Build the Docs API service
    service = build("docs", "v1", credentials=credentials, cache_discovery=False)
    # Requests payload: use endOfSegmentLocation to append at end of the document
    requests = [
        {
            "insertText": {
                "text": text,
                "endOfSegmentLocation": {},
            }
        }
    ]
    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()