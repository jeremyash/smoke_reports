# Deleting reports from the RxSmoke Report Archive

This guide describes how to remove unwanted Smoke Reports, PB Piedmont maps, and Multi-burn Exposure reports from the GitHub Pages archive at https://reports.rxsmoke.org/.

Run all commands from the root of the local `smoke_reports` repository.

## What the scripts do

- `scripts/select_reports.py` displays a numbered list of HTML reports currently in `docs/sr/`, `docs/pb/`, and (if present) `docs/mb/`. You choose reports by number or range. After confirmation, it **adds their relative paths** to `scripts/delete_reports.txt`. It does not delete anything.
- `scripts/delete_reports.txt` is the list of reports selected for deletion, one path per line, relative to `docs/` (for example, `sr/20261020-example-i1036.html`). Blank lines and lines beginning with `#` are ignored. Existing entries are not duplicated by the selector.
- `scripts/cleanup_reports.py` checks the list against the files and metadata in `docs/index.html`. It defaults to a **dry run**. With `--apply`, it deletes the selected HTML files and removes their matching archive metadata entries.

## Complete cleanup process

### 1. Synchronize with GitHub

The report generator can upload reports directly to GitHub, so the remote repository may have new commits.

```bash
git status --short
git pull --rebase origin main
```

If Git reports uncommitted changes or a rebase conflict, resolve those before proceeding; don't force-push. It is safest to start with a clean working tree.

### 2. Select reports

```bash
python3 scripts/select_reports.py
```

Review the numbered list. Enter one or more numbers separated by commas, or a range such as `1,3,5-8`. Check the displayed selected paths, then type `y` to append them to `scripts/delete_reports.txt`. Press Enter at the initial prompt or answer `n` at confirmation to cancel without changes.

You can also edit `scripts/delete_reports.txt` manually. Paths must start with `sr/`, `pb/`, or `mb/` and point to an `.html` report under `docs/`.

### 3. Preview without deleting

```bash
python3 scripts/cleanup_reports.py
```

For each selected report, inspect **HTML file** and **Index entries**. A report may have multiple index entries; the cleanup removes all matching entries. A report with a file but no index entry is an orphaned file and can be removed. Reports with neither a file nor an index entry are treated as already deleted and skipped. If an index entry exists but its HTML file is missing, the script stops for review.

Check the summary's **Ready to remove** count. **Do not proceed** if a listed path is not one you intend to delete.

### 4. Apply the deletion

```bash
python3 scripts/cleanup_reports.py --apply
```

The script removes the selected HTML files and their matching `report-entry` metadata from `docs/index.html`. It does **not** publish anything until you commit and push.

### 5. Verify the changes

```bash
git status --short
git diff --stat
git diff -- docs/index.html
find docs/sr docs/pb -type f -name '*.html' | sort
```

If you also have Multi-burn Exposure reports, inspect `docs/mb/` separately. Verify that only intended report files were deleted, that the index no longer references them, and that reports you want to keep remain.

If the changes are not right, **stop before committing**. Review the deletion list and use Git to restore only the files you actually want restored.

### 6. Commit and publish

```bash
git add docs/index.html docs/sr docs/pb
# If docs/mb exists and was modified, stage it as well:
# git add docs/mb
git commit -m "Remove selected reports from archive"
git pull --rebase origin main
git push origin main
```

If you have edited the scripts and want to publish those changes too, stage them explicitly (for example, `git add scripts/cleanup_reports.py scripts/select_reports.py`). To commit this guide, run `git add delete_reports_readme.md` before committing.

The Report Products table and Recent Activity display may take a little time to reflect GitHub Pages deployment or browser cache updates. Check https://reports.rxsmoke.org/ after the push.

## Reusing the deletion list

You can leave old paths in `scripts/delete_reports.txt`. The cleanup script skips reports that are already deleted and have no remaining index entry. The selector will not append a path already in the list.

For a shorter list, you may manually remove completed entries after a successful cleanup. That is optional.

## Safety notes

- **Selecting is not deleting.** `select_reports.py` only edits the text list.
- **Dry run is the default.** `cleanup_reports.py` makes no changes without `--apply`.
- The cleanup acts only on the paths in the deletion list, not on filenames that merely look like tests.
- Report files are removed from the current published site and Git checkout, but remain in Git history unless history is separately rewritten; routine cleanup does not require rewriting history.
- If new reports are uploaded while you work, pull/rebase and recheck before pushing. Never force-push over uploads.

## Quick reference

```bash
# From smoke_reports/
python3 scripts/select_reports.py       # Choose reports; writes deletion list only
python3 scripts/cleanup_reports.py      # Preview
python3 scripts/cleanup_reports.py --apply  # Delete locally
git status --short                       # Verify
git diff --stat
git add docs/index.html docs/sr docs/pb
git commit -m "Remove selected reports from archive"
git pull --rebase origin main
git push origin main
```
