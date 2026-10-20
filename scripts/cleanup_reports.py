
#!/usr/bin/env python3

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
INDEX = DOCS / "index.html"
DELETE_LIST = ROOT / "scripts" / "delete_reports.txt"

# Matches the report metadata blocks in docs/index.html
ENTRY_PATTERN = re.compile(
    r"""(?P<entry><div\b(?=[^>]*\bclass=['"]report-entry['"])[^>]*>.*?</div>)""",
    re.DOTALL,
)

URL_PATTERN = re.compile(
    r"""data-url=['"]([^'"]+)['"]"""
)


def load_deletion_list():
    paths = []

    for line in DELETE_LIST.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        relative = Path(line)

        if (
            relative.is_absolute()
            or ".." in relative.parts
            or relative.suffix.lower() != ".html"
            or relative.parts[0] not in ("sr", "pb", "mb")
        ):
            raise ValueError(f"Invalid report path: {line}")

        paths.append(relative.as_posix())

    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate paths in deletion list")

    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Remove selected reports and archive entries."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete files and update docs/index.html",
    )
    args = parser.parse_args()

    targets = load_deletion_list()
    index_html = INDEX.read_text(encoding="utf-8")

    entries = list(ENTRY_PATTERN.finditer(index_html))
    found_urls = {}

    for match in entries:
        url_match = URL_PATTERN.search(match.group("entry"))

        if url_match:
            url = url_match.group(1)
            found_urls.setdefault(url, []).append(match)

    print(f"\n{'APPLY' if args.apply else 'DRY RUN'}")
    print("=" * 65)

    errors = []

    for target in targets:
        file_path = DOCS / target
        matches = found_urls.get(target, [])

        file_exists = file_path.is_file()

        print(f"\n{target}")
        print(f"  HTML file: {'Found' if file_exists else 'MISSING'}")
        print(f"  Index entries: {len(matches)}")

        if not file_exists and len(matches) == 0:
            print("  Status: Already deleted — skipping")
            continue

        if not file_exists and len(matches) > 0:
            print("  Status: Missing HTML file but archive entry exists")
            errors.append(target)

        if file_exists and len(matches) == 0:
            print("  Status: Orphaned HTML file — will remove")

    if errors:
        print("\nStopped: missing files or unexpected index entries.")
        print("No changes made.")
        return

    pending = [
        target for target in targets
        if (DOCS / target).is_file()
    ]

    print(f"\nReports listed: {len(targets)}")
    print(f"Already deleted: {len(targets) - len(pending)}")
    print(f"Ready to remove: {len(pending)}")

    if not args.apply:
        print("No files changed. Run with --apply to proceed.")
        return

    # Remove selected metadata entries from the archive.
    for target in targets:
        if not (DOCS / target).is_file():
            continue

        for match in found_urls.get(target, []):
            entry = match.group("entry")
            index_html = index_html.replace(entry + "\n", "", 1)

    INDEX.write_text(index_html, encoding="utf-8")

    # Remove the selected report HTML files.
    for target in targets:
        file_path = DOCS / target

        if file_path.is_file():
            file_path.unlink()

    print("\nCleanup complete.")
    print("Review changes with: git diff --stat")
    print("Review deletions with: git status --short")


if __name__ == "__main__":
    main()
