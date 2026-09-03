#!/usr/bin/env python3
"""
generate_local_comic.py
=======================
Transfers annotated comic images and storyboard from museimages / comics storage
into the thinkingbuffer Astro project, creating a fully functional local version
of the comic chapter blog post.

Usage:
  python3 .agents/scripts/generate_local_comic.py --source-dir <source_dir> --dest-dir <dest_dir> [--move]
  python3 .agents/scripts/generate_local_comic.py --intro [--move]
  python3 .agents/scripts/generate_local_comic.py --book 1 --chapter 1 [--move]
"""

import os
import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

DEFAULT_SOURCE_BASE = Path(os.path.expanduser("~/Documents/comics/ramayana_dutt"))
FALLBACK_SOURCE_BASE = Path("/Users/neerav/Documents/Projects/mythology-texts/mythology podcast/ramayana_dutt")
DEST_BASE = Path("src/pages/comics/ramayana")
MAPPING_FILE = Path("src/data/ramayana_dutt_1to1_mapping.json")

KANDA_MAPPING = {
    1: ("Book_01_Bala_Kanda", "Bāla Kāṇḍa", "बालकाण्ड"),
    2: ("Book_02_Ayodhya_Kanda", "Ayodhyā Kāṇḍa", "अयोध्याकाण्ड"),
    3: ("Book_03_Aranya_Kanda", "Āraṇya Kāṇḍa", "अरण्यकाण्ड"),
    4: ("Book_04_Kishkindha_Kanda", "Kiṣkindhā Kāṇḍa", "किष्किन्धाकाण्ड"),
    5: ("Book_05_Sundara_Kanda", "Sundara Kāṇḍa", "सुन्दरकाण्ड"),
    6: ("Book_06_Yuddha_Kanda", "Yuddha Kāṇḍa", "युद्धकाण्ड"),
    7: ("Book_07_Uttara_Kanda", "Uttara Kāṇḍa", "उत्तरकाण्ड"),
}


def load_mapping_data():
    if MAPPING_FILE.exists():
        try:
            with open(MAPPING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {MAPPING_FILE}: {e}")
    return []


def find_source_chapter(source_base: Path, book_num: int, chap_num: int) -> Path | None:
    """Finds the source chapter directory in comics storage."""
    if not source_base.exists():
        return None

    # Search for matching chapter folder
    pattern = f"Book_{book_num}_*Chapter_{chap_num}"
    matches = list(source_base.glob(f"**/{pattern}"))
    if matches:
        return matches[0]

    # Also search by book dir
    kanda_folder = KANDA_MAPPING.get(book_num, (f"Book_{book_num:02d}", "", ""))[0]
    book_dir = source_base / kanda_folder
    if book_dir.exists():
        for ch in book_dir.iterdir():
            if ch.is_dir() and f"Chapter_{chap_num}" in ch.name:
                return ch

    return None


def find_dest_chapter(dest_base: Path, book_num: int, chap_num: int) -> Path | None:
    """Finds or constructs the destination chapter directory in Astro."""
    kanda_folder = KANDA_MAPPING.get(book_num, (f"Book_{book_num:02d}", "", ""))[0]
    book_dir = dest_base / kanda_folder

    if book_dir.exists():
        for ch in book_dir.iterdir():
            if ch.is_dir() and re.search(rf"Chapter_0?{chap_num}$", ch.name, re.IGNORECASE):
                return ch

    # Fallback to standard name
    return book_dir / f"Book_{book_num}_{kanda_folder.split('_', 2)[-1]}_Chapter_{chap_num}"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extracts existing frontmatter YAML and body content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_yaml = parts[1]
            body = parts[2]
            fm = {}
            for line in raw_yaml.strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    fm[key] = val
            return fm, body
    return {}, content


def process_chapter(
    source_dir: Path,
    dest_dir: Path,
    is_intro: bool = False,
    book_num: int = 1,
    chap_num: int = 1,
    move_files: bool = False
):
    print(f"\n==========================================")
    print(f"Source Chapter : {source_dir}")
    print(f"Dest Chapter   : {dest_dir}")
    print(f"Mode           : {'MOVE' if move_files else 'COPY'}")
    print(f"Is Intro       : {is_intro}")
    print(f"==========================================\n")

    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist.")
        sys.exit(1)

    # 1. Locate source annotated images (English and optional Hindi)
    src_annotated = source_dir / "annotated"
    if not src_annotated.exists():
        # Check if source_dir itself is annotated or has images
        src_annotated = source_dir

    image_extensions = (".jpg", ".jpeg", ".png", ".webp")
    source_images = [
        p for p in src_annotated.iterdir()
        if p.is_file() and p.suffix.lower() in image_extensions
        and not p.name.startswith(".")
    ]

    # Filter out discarded candidate files if any
    source_images = [p for p in source_images if "candidate" not in p.stem.lower()]
    named_en = [p for p in source_images if re.search(r"(?:Introduction|Book_\d+)_Slide\d+", p.name, re.I)]
    if named_en:
        source_images = named_en
    source_images.sort(key=lambda p: p.name)

    if not source_images:
        print(f"Error: No annotated images found in {src_annotated}")
        sys.exit(1)

    print(f"Found {len(source_images)} English annotated image(s):")
    for img in source_images:
        print(f"  • {img.name}")

    # Check for Hindi annotated images
    src_annotated_hi = source_dir / "annotated_hi"
    source_images_hi = []
    if src_annotated_hi.exists() and src_annotated_hi.is_dir():
        source_images_hi = [
            p for p in src_annotated_hi.iterdir()
            if p.is_file() and p.suffix.lower() in image_extensions
            and not p.name.startswith(".")
        ]
        source_images_hi = [p for p in source_images_hi if "candidate" not in p.stem.lower()]
        named_hi = [p for p in source_images_hi if re.search(r"(?:Introduction|Book_\d+)_Slide\d+", p.name, re.I)]
        if named_hi:
            source_images_hi = named_hi
        source_images_hi.sort(key=lambda p: p.name)

    if source_images_hi:
        print(f"\nFound {len(source_images_hi)} Hindi annotated image(s):")
        for img in source_images_hi:
            print(f"  • (HI) {img.name}")

    # 2. Transfer English images to destination annotated/
    dest_annotated = dest_dir / "annotated"
    dest_annotated.mkdir(parents=True, exist_ok=True)

    dest_images = []
    for img in source_images:
        target_file = dest_annotated / img.name
        if move_files:
            shutil.move(str(img), str(target_file))
            print(f"Moved: {img.name} -> {target_file}")
        else:
            shutil.copy2(str(img), str(target_file))
            print(f"Copied: {img.name} -> {target_file}")
        dest_images.append(target_file)

    # Transfer Hindi images to destination annotated_hi/ if available
    dest_images_hi = []
    if source_images_hi:
        dest_annotated_hi = dest_dir / "annotated_hi"
        dest_annotated_hi.mkdir(parents=True, exist_ok=True)
        for img in source_images_hi:
            target_file = dest_annotated_hi / img.name
            if move_files:
                shutil.move(str(img), str(target_file))
                print(f"Moved (HI): {img.name} -> {target_file}")
            else:
                shutil.copy2(str(img), str(target_file))
                print(f"Copied (HI): {img.name} -> {target_file}")
            dest_images_hi.append(target_file)

    # Sync hero image to public/images/comics for landing and book page cards
    public_comics_dir = Path("public/images/comics")
    public_comics_dir.mkdir(parents=True, exist_ok=True)
    if dest_images:
        chapter_hero_path = public_comics_dir / f"{dest_dir.name}_hero.jpg"
        shutil.copy2(str(dest_images[0]), str(chapter_hero_path))
        if is_intro:
            shutil.copy2(str(dest_images[0]), str(public_comics_dir / "ramayana_hero.jpg"))
            print(f"Updated global hero image: public/images/comics/ramayana_hero.jpg")

    # 3. Locate Storyboard JSON (filter out Hindi storyboard to pick English as primary)
    storyboard_files = [
        p for p in source_dir.glob("*comic_storyboard*.json")
        if "hindi" not in p.name.lower()
    ]
    if not storyboard_files:
        storyboard_files = list(source_dir.glob("*comic_storyboard*.json"))

    if not storyboard_files and FALLBACK_SOURCE_BASE.exists():
        # Search fallback mythology-texts repo
        if is_intro:
            sb_fallback = FALLBACK_SOURCE_BASE / "Introduction" / "comic_storyboard_Introduction.json"
            if sb_fallback.exists():
                storyboard_files = [sb_fallback]
        else:
            cand = [
                p for p in FALLBACK_SOURCE_BASE.glob(f"**/*Chapter_{chap_num}/*comic_storyboard*.json")
                if "hindi" not in p.name.lower()
            ]
            if cand:
                storyboard_files = cand

    storyboard = []
    if storyboard_files:
        sb_path = storyboard_files[0]
        print(f"\nUsing Storyboard: {sb_path}")
        try:
            with open(sb_path, "r", encoding="utf-8") as f:
                storyboard = json.load(f)
        except Exception as e:
            print(f"Warning: Could not parse storyboard JSON {sb_path}: {e}")
    else:
        print("\nWarning: No storyboard JSON found. Using image filenames for slide titles.")

    # 4. Generate local index.md
    dest_index_md = dest_dir / "index.md"
    existing_fm = {}
    if dest_index_md.exists():
        try:
            with open(dest_index_md, "r", encoding="utf-8") as f:
                existing_fm, _ = parse_frontmatter(f.read())
        except Exception:
            pass

    # Determine metadata
    mapping_data = load_mapping_data()
    matched_meta = next(
        (m for m in mapping_data if m.get("book_num") == book_num and m.get("section_number") == chap_num),
        {}
    )

    kanda_slug, kanda_iast, kanda_sanskrit = KANDA_MAPPING.get(
        book_num, (f"Book_{book_num:02d}", f"Book {book_num}", "")
    )

    layout_rel = "../../../../layouts/ComicLayout.astro" if is_intro else "../../../../../layouts/ComicLayout.astro"

    if is_intro:
        page_title = "Introduction: Welcome to the Odyssey"
        tags = '["Ramayana", "Comics", "Mythology", "Introduction"]'
        book_num = 0
        section_number = 0
        roman = "Intro"
        sanskrit_title = "Prastāvanā & Samkṣepa"
        english_title = "Welcome to the Odyssey - An Illustrated Introduction to the Ramayana"
        prev_link_html = '<a href="/comics/ramayana/" class="prev-link">← Ramayana Master Index</a>'
        next_link_html = '<a href="/comics/ramayana/Book_01_Bala_Kanda/Book_1_Bala_Kanda_Chapter_1/" class="next-link">Book 1, Chapter 1: The Sage\'s Question →</a>'
    else:
        page_title = existing_fm.get("title") or f"Book {book_num}: {kanda_iast} - Chapter {chap_num}"
        tags = f'["Ramayana", "Comics", "Mythology", "{kanda_iast}"]'
        section_number = chap_num
        roman = matched_meta.get("roman", str(chap_num))
        sanskrit_title = matched_meta.get("thematic_sanskrit_title", existing_fm.get("sanskrit_title", ""))
        english_title = matched_meta.get("thematic_english_title", existing_fm.get("english_title", ""))

        if chap_num == 1:
            prev_link_html = '<a href="/comics/ramayana/introduction/" class="prev-link">← Introduction</a>'
        else:
            prev_link_html = f'<a href="/comics/ramayana/{kanda_slug}/Book_{book_num}_{kanda_slug.split("_", 2)[-1]}_Chapter_{chap_num - 1}/" class="prev-link">← Previous Chapter</a>'
        next_link_html = f'<a href="/comics/ramayana/{kanda_slug}/Book_{book_num}_{kanda_slug.split("_", 2)[-1]}_Chapter_{chap_num + 1}/" class="next-link">Next Chapter →</a>'

    first_image_rel = f"./annotated/{dest_images[0].name}"
    today_str = datetime.now().strftime("%Y-%m-%d")
    pub_date = existing_fm.get("date") or today_str

    has_hindi = len(dest_images_hi) > 0
    first_hi_image_rel = f"./annotated_hi/{dest_images_hi[0].name}" if has_hindi else None

    # Build Markdown Content
    lines = [
        "---",
        f"layout: {layout_rel}",
        f'title: "{page_title}"',
        f"date: {pub_date}",
        f"tags: {tags}",
        f'image_url: "{first_image_rel}"',
        f'heroImage: "{first_image_rel}"',
    ]

    if has_hindi and first_hi_image_rel:
        lines.append(f'image_url_hi: "{first_hi_image_rel}"')
        lines.append('has_hindi: true')

    lines.extend([
        f"book_num: {book_num}",
        f'kanda_iast: "{kanda_iast}"',
        f'kanda_sanskrit: "{kanda_sanskrit}"',
        f"section_number: {section_number}",
        f'roman: "{roman}"',
        f'sanskrit_title: "{sanskrit_title}"',
        f'english_title: "{english_title}"',
        'status: "published"',
        "---",
        "",
        '<div class="nav-links-chapter">',
        f"  {prev_link_html}",
        f"  {next_link_html}",
        "</div>",
        ""
    ])

    # Render each slide
    if storyboard:
        for idx, slide_item in enumerate(storyboard, start=1):
            s_num = slide_item.get("slide", idx)
            s_title = slide_item.get("title") or slide_item.get("slide_label") or f"Slide {s_num}"
            if s_title.startswith(f"Slide{s_num:02d}") or s_title.startswith(f"Slide {s_num}"):
                cleaned_title = re.sub(r"^Slide\s*\d+\s*[-–:]*\s*", "", s_title).strip()
            else:
                cleaned_title = s_title

            # Match destination English image for this slide
            matched_img = None
            for p in dest_images:
                p_name_lower = p.stem.lower()
                if f"slide{int(s_num):02d}" in p_name_lower or f"slide_{int(s_num):02d}" in p_name_lower:
                    matched_img = p
                    break
            if not matched_img and idx <= len(dest_images):
                matched_img = dest_images[idx - 1]

            if matched_img:
                lines.append(f"## Slide {int(s_num):02d} - {cleaned_title}")
                lines.append("")
                lines.append(f"![Slide {int(s_num):02d} - {cleaned_title}](./annotated/{matched_img.name})")

                # Match corresponding Hindi image if available
                if dest_images_hi:
                    matched_img_hi = next((h for h in dest_images_hi if h.name == matched_img.name), None)
                    if not matched_img_hi:
                        for h in dest_images_hi:
                            h_name_lower = h.stem.lower()
                            if f"slide{int(s_num):02d}" in h_name_lower or f"slide_{int(s_num):02d}" in h_name_lower:
                                matched_img_hi = h
                                break
                    if not matched_img_hi and idx <= len(dest_images_hi):
                        matched_img_hi = dest_images_hi[idx - 1]

                    if matched_img_hi:
                        lines.append(f"![Slide {int(s_num):02d} - {cleaned_title} (Hindi)](./annotated_hi/{matched_img_hi.name})")

                lines.append("")
    else:
        for idx, p in enumerate(dest_images, start=1):
            s_title = p.stem.replace("_", " ")
            lines.append(f"## Slide {idx:02d} - {s_title}")
            lines.append("")
            lines.append(f"![Slide {idx:02d} - {s_title}](./annotated/{p.name})")

            # Match corresponding Hindi image if available
            if dest_images_hi:
                matched_img_hi = next((h for h in dest_images_hi if h.name == p.name), None)
                if not matched_img_hi and idx <= len(dest_images_hi):
                    matched_img_hi = dest_images_hi[idx - 1]
                if matched_img_hi:
                    lines.append(f"![Slide {idx:02d} - {s_title} (Hindi)](./annotated_hi/{matched_img_hi.name})")

            lines.append("")

    lines.append('<div class="nav-links-chapter">')
    lines.append(f"  {prev_link_html}")
    lines.append(f"  {next_link_html}")
    lines.append("</div>")
    lines.append("")

    new_content = "\n".join(lines)
    with open(dest_index_md, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n✓ Generated local blog post: {dest_index_md}")
    print(f"  English slides count: {len(dest_images)}")
    if dest_images_hi:
        print(f"  Hindi slides count  : {len(dest_images_hi)}")
    print(f"  Hero image: {first_image_rel}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate local comic blog post from storage assets.")
    parser.add_argument("book_arg", nargs="?", help="Book number or 'intro'/'introduction'")
    parser.add_argument("chap_arg", nargs="?", help="Chapter number")
    parser.add_argument("--intro", action="store_true", help="Process Introduction chapter")
    parser.add_argument("--book", type=int, help="Book number (1-7)")
    parser.add_argument("--chapter", type=int, help="Chapter number")
    parser.add_argument("--source-dir", help="Explicit source directory")
    parser.add_argument("--dest-dir", help="Explicit destination directory")
    parser.add_argument("--move", action="store_true", help="Move images instead of copying")
    args = parser.parse_args()

    is_intro = False
    book_num = 1
    chap_num = 1

    # Check positional args
    if args.intro:
        is_intro = True
    elif args.book_arg:
        first = str(args.book_arg).lower().strip()
        if first in ("intro", "introduction", "0"):
            is_intro = True
        elif first.isdigit():
            book_num = int(first)
            if args.chap_arg and args.chap_arg.isdigit():
                chap_num = int(args.chap_arg)
                if book_num == 1 and chap_num == 0:
                    is_intro = True
            elif args.chap_arg and args.chap_arg.lower() in ("intro", "introduction"):
                is_intro = True
    elif args.book is not None and args.chapter is not None:
        book_num = args.book
        chap_num = args.chapter
        if book_num == 1 and chap_num == 0:
            is_intro = True

    source_dir = None
    dest_dir = None

    if args.source_dir:
        source_dir = Path(args.source_dir).expanduser().resolve()
    if args.dest_dir:
        dest_dir = Path(args.dest_dir).resolve()

    if is_intro:
        if not source_dir:
            source_dir = DEFAULT_SOURCE_BASE / "Introduction"
            if not source_dir.exists():
                source_dir = DEFAULT_SOURCE_BASE / "Introduction" / "Introduction"
            if not source_dir.exists():
                source_dir = FALLBACK_SOURCE_BASE / "Introduction"
        if not dest_dir:
            dest_dir = DEST_BASE / "introduction"
        process_chapter(source_dir, dest_dir, is_intro=True, book_num=0, chap_num=0, move_files=args.move)
    else:
        if not source_dir:
            source_dir = find_source_chapter(DEFAULT_SOURCE_BASE, book_num, chap_num)
            if not source_dir:
                source_dir = find_source_chapter(FALLBACK_SOURCE_BASE, book_num, chap_num)
        if not dest_dir:
            dest_dir = find_dest_chapter(DEST_BASE, book_num, chap_num)

        if not source_dir or not dest_dir:
            print(f"Error: Could not locate Book {book_num}, Chapter {chap_num}")
            sys.exit(1)

        process_chapter(source_dir, dest_dir, is_intro=False, book_num=book_num, chap_num=chap_num, move_files=args.move)


if __name__ == "__main__":
    main()
