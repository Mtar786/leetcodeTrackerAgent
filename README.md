<!--
  LeetCode Tracker Agent

  This project automates the process of tracking your progress on
  [LeetCode](https://leetcode.com/). It retrieves recently solved problems for
  a given user, summarises each problem with the help of a large language
  model, and updates both a Google Doc and an Anki deck with the results.
  With this agent you can maintain a living study log and flashcard deck
  without manual copying and pasting.
-->

# LeetCode Tracker Agent

The **LeetCode Tracker Agent** automatically records problems you've solved on
[LeetCode](https://leetcode.com/), generates concise summaries, and appends
them to a Google Doc while also adding flashcards to an Anki deck. It is a
command‑line tool that integrates several services: LeetCode’s (unofficial)
GraphQL API, the Google Docs API, OpenAI for summarisation, and
AnkiConnect. The agent is modular, so you can enable or disable individual
features (e.g. skip Google Docs or Anki updates) depending on your needs.

## ✨ Features

- **Recent problem tracking** – Queries LeetCode to find your most recent
  accepted submissions and extracts unique problems.
- **Automated summarisation** – Uses OpenAI’s language models to create a
  succinct description of each solved problem, including its difficulty and
  topic tags.
- **Google Docs integration** – Appends neatly formatted summaries to an
  existing Google Document, creating a running record of your progress.
- **Anki flashcards** – Automatically adds new notes to a specified Anki deck
  via AnkiConnect. Each card contains the problem title on the front and the
  summary with a link on the back. You can customise the note model and
  tags.
- **Customisable** – Choose how many problems to process, which models to use,
  how many tokens to allow in summaries, and whether to include optional tags
  on your flashcards.

## 🧰 Prerequisites

This project requires **Python 3.8+**. You’ll need the following external
services set up:

1. **LeetCode account** – The tracker uses your public submission data via
   LeetCode’s GraphQL endpoint. No login credentials are required.
2. **OpenAI API key** – Required for problem summarisation. Sign up at
   [OpenAI](https://openai.com/api/) and set the `OPENAI_API_KEY` environment
   variable or pass `--openai-key` to the CLI.
3. **Google Cloud credentials** (optional) – To update a Google Doc you must
   [enable the Docs API](https://developers.google.com/docs/api/quickstart/python)
   in a Google Cloud project and download a **service account key** JSON file
   with the `https://www.googleapis.com/auth/documents` scope.
4. **Anki with AnkiConnect** (optional) – Install the
   [AnkiConnect plugin](https://ankiweb.net/shared/info/2055492159) in your
   desktop Anki. Make sure Anki is running when you use the CLI.

Install the required Python libraries:

```bash
pip install requests openai google-api-python-client google-auth
```

If you plan to use the summariser or Google Docs integration, also install
`bs4` for HTML parsing and `google-auth-oauthlib` for OAuth flows:

```bash
pip install bs4 google-auth-oauthlib
```

## 🚀 Usage

```bash
python -m leetcode_tracker_agent.cli \
    --username your_leetcode_username \
    --limit 5 \
    --doc-id 1aBcDeFG2H3IjkLmNOPQ \
    --service-account-key path/to/service-account.json \
    --anki-deck "LeetCode" \
    --openai-key sk-... 
```

### Command‑line Options

| Option                   | Description                                                              |
|--------------------------|--------------------------------------------------------------------------|
| `--username`             | **Required.** Your LeetCode username.                                    |
| `--limit`                | Number of recent solved problems to process.                             |
| `--doc-id`               | Google Document ID to append summaries to.                               |
| `--service-account-key`  | Path to a Google service account JSON key file. Required with `--doc-id`. |
| `--anki-deck`            | Name of the Anki deck to add cards to.                                   |
| `--anki-model`           | Anki note model name (default: `Basic`).                                 |
| `--tags`                 | Tags to add to all Anki notes (space‑separated).                          |
| `--openai-key`           | Your OpenAI API key for summarisation.                                   |
| `--max-tokens`           | Maximum number of tokens for each summary (default: 400).                |
| `--temperature`          | Sampling temperature for summaries (default: 0.3).                      |

### Example Walkthrough

1. Enable the Google Docs API and create a service account key. Share your
   target document with the service account email address.
2. Start Anki on your machine and ensure the AnkiConnect plugin is installed.
3. Execute the CLI command above with appropriate arguments. The agent will:
   - Query your last `limit` accepted submissions on LeetCode.
   - Fetch each problem’s description via GraphQL.
   - Generate a summary using OpenAI.
   - Append the summary to the Google Doc (if configured).
   - Add a flashcard to the Anki deck (if configured).

### Notes

- **Data privacy:** The tool sends your problem statements to the OpenAI API
  for summarisation. Consider whether this is acceptable for your personal
  or proprietary work.
- **LeetCode API limits:** There is no official public API; queries may break
  if LeetCode changes its endpoint. Use at your own risk.
- **AnkiConnect** must be running (i.e. Anki must be open) for note creation to
  succeed. If you encounter connection errors, ensure Anki is open and
  AnkiConnect is listening on port 8765.

## 📦 Project Structure

```
leetcode-tracker-agent/
├── leetcode_tracker_agent/    # Python package with core logic
│   ├── __init__.py
│   ├── leetcode_api.py        # Fetch solved problems via GraphQL
│   ├── summary.py             # Summarise problems using OpenAI
│   ├── google_docs.py         # Append summaries to a Google Doc
│   ├── anki_deck.py           # Add notes via AnkiConnect
│   ├── cli.py                 # Command‑line interface
│   └── types.py               # Dataclasses for problems and summaries
├── examples/                  # Placeholder for example configs or scripts
├── tests/                     # (empty) directory for future unit tests
├── README.md                  # Project overview and instructions
├── .gitignore                 # Standard gitignore for Python projects
└── LICENSE                    # MIT License
```

## 🧹 .gitignore

This repository includes a `.gitignore` file that excludes common
Python build artefacts, virtual environments, editor settings, and
Anki/Google credentials from version control. Make sure to keep any
sensitive tokens or key files out of your repository.

## 📄 License

This project is distributed under the [MIT License](LICENSE). You are free to
use, modify, and distribute this software with attribution.

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! If you have an
idea to improve the agent or want to add support for additional services,
please open an issue or submit a pull request.