
#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DELETE_LIST = ROOT / "scripts" / "delete_reports.txt"

REPORT_DIRS = {
    "sr": "Smoke Report",
    "pb": "PB Piedmont",
    "mb": "Multi-burn Exposure",
}


def get_reports():
    reports = []

    for folder, report_type in REPORT_DIRS.items():
        directory = DOCS / folder

        if not directory.exists():
            continue

        for file in directory.glob("*.html"):
            reports.append({
                "path": file.relative_to(DOCS).as_posix(),
                "type": report_type,
                "filename": file.name,
            })

    return sorted(
        reports,
        key=lambda x: x["filename"],
        reverse=True,
    )


def load_existing():
    if not DELETE_LIST.exists():
        return set()

    return {
        line.strip()
        for line in DELETE_LIST.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def parse_selection(selection, maximum):
    selected = set()

    for part in selection.split(","):
        part = part.strip()

        if "-" in part:
            start, end = map(int, part.split("-", 1))

            if start > end:
                raise ValueError("Invalid range")

            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))

    if not selected or min(selected) < 1 or max(selected) > maximum:
        raise ValueError("Selection out of range")

    return sorted(selected)


def main():
    reports = get_reports()

    if not reports:
        print("No reports found.")
        return

    existing = load_existing()

    print("\nAVAILABLE REPORTS")
    print("=" * 100)

    for i, report in enumerate(reports, start=1):
        status = " [LISTED]" if report["path"] in existing else ""

        print(
            f"{i:>3}. "
            f"{report['type']:<20} "
            f"{report['filename']}{status}"
        )

    print("\nEnter report numbers separated by commas.")
    print("Ranges are supported, e.g. 1,3,5-8.")
    print("Press Enter without a selection to cancel.")

    selection = input("\nReports to add: ").strip()

    if not selection:
        print("Cancelled. No changes made.")
        return

    try:
        numbers = parse_selection(selection, len(reports))
    except ValueError:
        print("Invalid selection. No changes made.")
        return

    chosen = [reports[i - 1]["path"] for i in numbers]
    new_reports = [path for path in chosen if path not in existing]

    print("\nSELECTED REPORTS")
    print("=" * 65)

    for path in chosen:
        print(f"  {path}")

    if not new_reports:
        print("\nAll selected reports are already listed.")
        return

    confirm = input(
        f"\nAdd {len(new_reports)} report(s) to delete_reports.txt? [y/N]: "
    ).strip().lower()

    if confirm != "y":
        print("Cancelled. No changes made.")
        return

    DELETE_LIST.parent.mkdir(parents=True, exist_ok=True)

    with DELETE_LIST.open("a", encoding="utf-8") as file:
        if DELETE_LIST.stat().st_size > 0:
            file.write("\n")

        for path in new_reports:
            file.write(path + "\n")

    print(f"\nAdded {len(new_reports)} report(s).")
    print("Next: python3 scripts/cleanup_reports.py")


if __name__ == "__main__":
    main()
