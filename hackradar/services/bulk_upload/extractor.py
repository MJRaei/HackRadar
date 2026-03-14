"""
GitHub URL extractor.

Scans a list of text tokens for valid GitHub repository URLs,
deduplicates them, and returns them in the order first encountered.
"""

import re


# Matches https://github.com/<owner>/<repo> with an optional path suffix.
# We capture only up to the repo name (two path segments after github.com).
_GITHUB_REPO_RE = re.compile(
    r"https?://github\.com/([\w.\-]+)/([\w.\-]+)"
)


class GitHubUrlExtractor:
    """Extract unique, normalised GitHub repo URLs from raw text tokens."""

    def extract(self, tokens: list[str]) -> list[str]:
        """
        Scan *tokens* for GitHub repo URLs.

        Returns a deduplicated list in first-encountered order.
        Each URL is normalised to ``https://github.com/<owner>/<repo>``
        (trailing slashes and sub-paths stripped).
        """
        seen: set[str] = set()
        urls: list[str] = []

        for token in tokens:
            for match in _GITHUB_REPO_RE.finditer(token):
                owner, repo = match.group(1), match.group(2)
                # Strip common suffixes like .git
                repo = repo.removesuffix(".git")
                normalised = f"https://github.com/{owner}/{repo}"
                if normalised not in seen:
                    seen.add(normalised)
                    urls.append(normalised)

        return urls
