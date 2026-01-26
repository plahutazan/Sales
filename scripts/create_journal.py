from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import shutil


JOURNAL_DIR = Path("journals")
ARCHIVE_ROOT = Path("archive") / "journals"
TEMPLATE_FILE = Path("templates") / "daily.md"

KEEP_DAYS = 7  # keep the most recent 7 days in journals/


def safe_move(src: Path, dst_dir: Path) -> Path:
    """Move src into dst_dir without overwriting; add (1), (2) if needed."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    target = dst_dir / src.name

    if not target.exists():
        shutil.move(str(src), str(target))
        return target

    stem, suffix = src.stem, src.suffix
    i = 1
    while True:
        candidate = dst_dir / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            shutil.move(str(src), str(candidate))
            return candidate
        i += 1


def archive_old_journals(now: datetime) -> None:
    """Move journals older than KEEP_DAYS into archive/journals/YYYY/MM/."""
    JOURNAL_DIR.mkdir(exist_ok=True)

    cutoff = now - timedelta(days=KEEP_DAYS)

    for md in JOURNAL_DIR.glob("*.md"):
        # Use file modified time to decide age (works even with pretty filenames)
        mtime = datetime.fromtimestamp(md.stat().st_mtime)

        if mtime < cutoff:
            year = mtime.strftime("%Y")
            month = mtime.strftime("%m")
            dest_dir = ARCHIVE_ROOT / year / month
            moved_to = safe_move(md, dest_dir)
            print(f"Archived: {md.name} -> {moved_to}")


def format_filename(now: datetime) -> str:
    # Example: "Monday, 26. Jan"
    weekday = now.strftime("%A")      # Monday
    day = now.day                    # 26 (no leading zero, works on Windows)
    month = now.strftime("%b")       # Jan
    return f"{weekday}, {day}. {month}.md"


def main() -> None:
    now = datetime.now()

    # 1) Archive old journals first
    archive_old_journals(now)

    # 2) Create today's journal in journals/
    JOURNAL_DIR.mkdir(exist_ok=True)

    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE_FILE}\n"
            f"Create it at templates/daily.md"
        )

    filename = format_filename(now)
    output_file = JOURNAL_DIR / filename

    if output_file.exists():
        print(f"Journal already exists: {output_file}")
        return

    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    # Placeholders you can use in the template
    pretty_date = f"{now.strftime('%A')}, {now.day}. {now.strftime('%b')}"
    date_iso = now.strftime("%Y-%m-%d")

    content = template.format(date=pretty_date, date_iso=date_iso)

    output_file.write_text(content, encoding="utf-8")
    print(f"Created journal: {output_file}")


if __name__ == "__main__":
    main()
