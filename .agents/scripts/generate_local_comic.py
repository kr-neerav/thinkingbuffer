#!/usr/bin/env python3
"""
generate_local_comic.py
=======================
Transfers comic slide images, storyboards, narration, and discussion from
MythologyMuse outputs (or legacy comics storage) into the thinkingbuffer Astro
project, generating a dual-language, two-tab (Comics + Narration & Discussion)
chapter post.

Usage:
  python3 .agents/scripts/generate_local_comic.py --book 1 --chapter 1 [--move]
  python3 .agents/scripts/generate_local_comic.py intro [--move]
  python3 .agents/scripts/generate_local_comic.py 1 1 [--move]
"""

import os
import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

DEFAULT_SOURCE_BASE = Path("/Users/neerav/Documents/Projects/MythologyMuse/mythologies/ramayana_dutt/outputs")
FALLBACK_SOURCE_BASE = Path(os.path.expanduser("~/Documents/comics/ramayana_dutt"))
TERTIARY_SOURCE_BASE = Path("/Users/neerav/Documents/Projects/mythology-texts/mythology podcast/ramayana_dutt")
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
    """Finds the source chapter directory in outputs or comics storage."""
    if not source_base.exists():
        return None

    # 1. Match exact output folder patterns like Book_1_Bala_Kanda_Chapter_1
    pattern = f"Book_{book_num}_*Chapter_{chap_num}"
    matches = [d for d in source_base.glob(pattern) if d.is_dir() and "backup" not in d.name.lower()]
    if matches:
        return matches[0]

    # Recursive glob
    rec_matches = [d for d in source_base.glob(f"**/{pattern}") if d.is_dir() and "backup" not in d.name.lower()]
    if rec_matches:
        return rec_matches[0]

    # 2. Check kanda folder if nested
    kanda_folder = KANDA_MAPPING.get(book_num, (f"Book_{book_num:02d}", "", ""))[0]
    book_dir = source_base / kanda_folder
    if book_dir.exists():
        for ch in book_dir.iterdir():
            if ch.is_dir() and f"Chapter_{chap_num}" in ch.name and "backup" not in ch.name.lower():
                return ch

    return None


def find_dest_chapter(dest_base: Path, book_num: int, chap_num: int) -> Path | None:
    """Finds or constructs destination chapter directory in Astro."""
    kanda_folder = KANDA_MAPPING.get(book_num, (f"Book_{book_num:02d}", "", ""))[0]
    book_dir = dest_base / kanda_folder

    if book_dir.exists():
        for ch in book_dir.iterdir():
            if ch.is_dir() and re.search(rf"Chapter_0?{chap_num}$", ch.name, re.IGNORECASE):
                return ch

    # Fallback to standard directory name
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


def clean_text_tags(text: str) -> str:
    """Strips trailing emotion tags and replaces em/en dashes with hyphens."""
    t = text.replace("—", " - ").replace("–", "-")
    t = re.sub(r"\s*-\s*", " - ", t)
    return re.sub(r"<[^>]+>", "", t).strip()


def parse_discussion_item(en_raw: str, hi_raw: str) -> dict:
    """Parses Question, Reflection, and Takeaway from raw text."""
    en_clean = clean_text_tags(en_raw)
    hi_clean = clean_text_tags(hi_raw)

    q_en_m = re.search(r"Question:\s*(.*?)(?=Reflection:|$)", en_clean, re.DOTALL | re.IGNORECASE)
    r_en_m = re.search(r"Reflection:\s*(.*?)(?=Takeaway:|$)", en_clean, re.DOTALL | re.IGNORECASE)
    t_en_m = re.search(r"Takeaway:\s*(.*?)$", en_clean, re.DOTALL | re.IGNORECASE)

    q_hi_m = re.search(r"प्रश्न:\s*(.*?)(?=विवेचना:|$)", hi_clean, re.DOTALL)
    r_hi_m = re.search(r"विवेचना:\s*(.*?)(?=जीवन-सूत्र:|$)", hi_clean, re.DOTALL)
    t_hi_m = re.search(r"जीवन-सूत्र:\s*(.*?)$", hi_clean, re.DOTALL)

    return {
        "q_en": q_en_m.group(1).strip() if q_en_m else en_clean,
        "r_en": r_en_m.group(1).strip() if r_en_m else "",
        "t_en": t_en_m.group(1).strip() if t_en_m else "",
        "q_hi": q_hi_m.group(1).strip() if q_hi_m else hi_clean,
        "r_hi": r_hi_m.group(1).strip() if r_hi_m else "",
        "t_hi": t_hi_m.group(1).strip() if t_hi_m else "",
    }


def to_spotify_embed_url(url: str) -> str:
    if not url:
        return ""
    if "/embed/" in url:
        return url
    m = re.search(r"episode/([a-zA-Z0-9]+)", url)
    if m:
        return f"https://open.spotify.com/embed/episode/{m.group(1)}?utm_source=generator"
    return url


def to_youtube_embed_url(url: str) -> str:
    if not url:
        return ""
    if "/embed/" in url:
        return url
    m = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"
    return url


def process_chapter(
    source_dir: Path,
    dest_dir: Path,
    is_intro: bool = False,
    book_num: int = 1,
    chap_num: int = 1,
    move_files: bool = False,
):
    print("\n==========================================")
    print(f"Source Chapter : {source_dir}")
    print(f"Dest Chapter   : {dest_dir}")
    print(f"Mode           : {'MOVE' if move_files else 'COPY'}")
    print(f"Is Intro       : {is_intro}")
    print("==========================================\n")

    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist.")
        sys.exit(1)

    # 1. Locate Slide Images in source directory
    # Checks studio_images/ first, falls back to source_dir itself
    img_dir = source_dir / "studio_images"
    if not img_dir.exists():
        img_dir = source_dir

    image_extensions = (".jpg", ".jpeg", ".png", ".webp")
    all_imgs = [
        p for p in img_dir.iterdir()
        if p.is_file() and p.suffix.lower() in image_extensions
        and p.name.startswith("slide_")
    ]

    # Map each slide number to its best image (favoring _final over candidates)
    slide_map: dict[int, Path] = {}
    for p in all_imgs:
        m = re.search(r"slide_0*(\d+)", p.stem, re.I)
        if m:
            s_num = int(m.group(1))
            is_final = "final" in p.stem.lower()
            if s_num not in slide_map or is_final:
                slide_map[s_num] = p

    # Sort slides by numeric slide index
    sorted_slides = sorted(slide_map.items())
    source_images = [p for _, p in sorted_slides]

    if not source_images:
        # Fallback to any images that aren't sheets
        fallback_imgs = [
            p for p in img_dir.iterdir()
            if p.is_file() and p.suffix.lower() in image_extensions
            and not p.name.startswith(".") and not p.name.startswith("sheet_")
        ]
        fallback_imgs.sort(key=lambda p: p.name)
        source_images = fallback_imgs

    if not source_images:
        print(f"Error: No slide images found in {img_dir}")
        sys.exit(1)

    print(f"Found {len(source_images)} slide image(s):")
    for img in source_images:
        print(f"  • {img.name}")

    # Compute web URL path and public/ mirror directory for Astro static serving
    try:
        rel_from_src_pages = dest_dir.relative_to(Path("src/pages"))
    except ValueError:
        repo_root = Path.cwd()
        rel_from_src_pages = dest_dir.resolve().relative_to((repo_root / "src/pages").resolve())

    web_slides_dir = f"/{rel_from_src_pages.as_posix()}/slides"
    public_slides_dir = Path("public") / rel_from_src_pages / "slides"
    public_slides_dir.mkdir(parents=True, exist_ok=True)

    # 2. Transfer Images to destination slides/ and public/
    dest_slides_dir = dest_dir / "slides"
    dest_slides_dir.mkdir(parents=True, exist_ok=True)

    dest_images = []
    for img in source_images:
        target_file = dest_slides_dir / img.name
        pub_target_file = public_slides_dir / img.name
        if move_files:
            shutil.copy2(str(img), str(pub_target_file))
            shutil.move(str(img), str(target_file))
            print(f"Moved: {img.name} -> {target_file}")
        else:
            shutil.copy2(str(img), str(target_file))
            shutil.copy2(str(img), str(pub_target_file))
            print(f"Copied: {img.name} -> {target_file} & {pub_target_file}")
        dest_images.append(target_file)

    # Copy hero image to public/images/comics
    public_comics_dir = Path("public/images/comics")
    public_comics_dir.mkdir(parents=True, exist_ok=True)
    if dest_images:
        chapter_hero_path = public_comics_dir / f"{dest_dir.name}_hero.jpg"
        shutil.copy2(str(dest_images[0]), str(chapter_hero_path))
        if is_intro:
            shutil.copy2(str(dest_images[0]), str(public_comics_dir / "ramayana_hero.jpg"))
            print("Updated global hero image: public/images/comics/ramayana_hero.jpg")

    # 3. Locate Storyboards (English & Hindi)
    sb_en_files = [p for p in source_dir.glob("*comic_storyboard*.json") if "hindi" not in p.name.lower()]
    sb_hi_files = [p for p in source_dir.glob("*comic_storyboard_hindi*.json")]

    storyboard_en = []
    if sb_en_files:
        try:
            with open(sb_en_files[0], "r", encoding="utf-8") as f:
                storyboard_en = json.load(f)
            print(f"Loaded English Storyboard: {sb_en_files[0].name}")
        except Exception as e:
            print(f"Warning: Could not parse English storyboard: {e}")

    storyboard_hi = []
    if sb_hi_files:
        try:
            with open(sb_hi_files[0], "r", encoding="utf-8") as f:
                storyboard_hi = json.load(f)
            print(f"Loaded Hindi Storyboard: {sb_hi_files[0].name}")
        except Exception as e:
            print(f"Warning: Could not parse Hindi storyboard: {e}")

    # Build slide lookup dictionaries
    sb_en_map = {item.get("slide", idx): item for idx, item in enumerate(storyboard_en, 1)}
    sb_hi_map = {item.get("slide", idx): item for idx, item in enumerate(storyboard_hi, 1)}

    # 4. Locate Narration & Discussion Data
    narration_files = list(source_dir.glob("narration_*.json"))
    discussion_files = list(source_dir.glob("discussion_*.json"))

    narration_paragraphs = []
    if narration_files:
        try:
            with open(narration_files[0], "r", encoding="utf-8") as f:
                raw_narr = json.load(f)
            for item in raw_narr:
                t_en = clean_text_tags(item.get("text_en", ""))
                t_hi = clean_text_tags(item.get("text", ""))
                if t_en or t_hi:
                    narration_paragraphs.append({"en": t_en, "hi": t_hi})
            print(f"Loaded Narration JSON: {narration_files[0].name} ({len(narration_paragraphs)} paragraphs)")
        except Exception as e:
            print(f"Warning: Could not parse narration JSON: {e}")
    else:
        # Fallback to txt files
        en_txt = source_dir / f"english_narration_{source_dir.name}.txt"
        hi_txt = source_dir / f"hindi_narration_{source_dir.name}.txt"
        if not en_txt.exists():
            cand_en = list(source_dir.glob("english_narration_*.txt"))
            if cand_en:
                en_txt = cand_en[0]
        if not hi_txt.exists():
            cand_hi = list(source_dir.glob("hindi_narration_*.txt"))
            if cand_hi:
                hi_txt = cand_hi[0]

        if en_txt.exists() and hi_txt.exists():
            try:
                with open(en_txt, "r", encoding="utf-8") as fe, open(hi_txt, "r", encoding="utf-8") as fh:
                    en_lines = [l.strip() for l in fe.readlines() if l.strip()]
                    hi_lines = [l.strip() for l in fh.readlines() if l.strip()]
                # Narrations are the lines before Question: / प्रश्न:
                for le, lh in zip(en_lines, hi_lines):
                    if le.lower().startswith("question:") or lh.startswith("प्रश्न:"):
                        break
                    narration_paragraphs.append({"en": clean_text_tags(le), "hi": clean_text_tags(lh)})
                print(f"Loaded Narration from TXT ({len(narration_paragraphs)} paragraphs)")
            except Exception as e:
                print(f"Warning: Could not parse narration TXT: {e}")

    discussion_items = []
    if discussion_files:
        try:
            with open(discussion_files[0], "r", encoding="utf-8") as f:
                raw_disc = json.load(f)
            for item in raw_disc:
                parsed = parse_discussion_item(item.get("text_en", ""), item.get("text", ""))
                discussion_items.append(parsed)
            print(f"Loaded Discussion JSON: {discussion_files[0].name} ({len(discussion_items)} items)")
        except Exception as e:
            print(f"Warning: Could not parse discussion JSON: {e}")

    has_narration = len(narration_paragraphs) > 0 or len(discussion_items) > 0
    has_hindi = len(storyboard_hi) > 0 or any(p.get("hi") for p in narration_paragraphs)

    # 5. Extract Metadata and Build index.md
    dest_index_md = dest_dir / "index.md"
    existing_fm = {}
    if dest_index_md.exists():
        try:
            with open(dest_index_md, "r", encoding="utf-8") as f:
                existing_fm, _ = parse_frontmatter(f.read())
        except Exception:
            pass

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

    first_image_rel = f"{web_slides_dir}/{dest_images[0].name}"
    today_str = datetime.now().strftime("%Y-%m-%d")
    pub_date = existing_fm.get("date") or today_str

    has_media = bool(existing_fm.get("has_media", False))
    spotify_en = existing_fm.get("spotify_en", "")
    spotify_hi = existing_fm.get("spotify_hi", "")
    youtube_url = existing_fm.get("youtube_url", "")

    if is_intro:
        spotify_en = spotify_en or "https://open.spotify.com/episode/4pAbbGom38zKsf5oLanUkt"
        spotify_hi = spotify_hi or "https://open.spotify.com/episode/6ejakwTisIvNWD7Ef8DPSQ"
        has_media = True
    elif spotify_en or spotify_hi or youtube_url:
        has_media = True

    # Frontmatter Header
    lines = [
        "---",
        f"layout: {layout_rel}",
        f'title: "{page_title}"',
        f"date: {pub_date}",
        f"tags: {tags}",
        f'image_url: "{first_image_rel}"',
        f'heroImage: "{first_image_rel}"',
        f"book_num: {book_num}",
        f'kanda_iast: "{kanda_iast}"',
        f'kanda_sanskrit: "{kanda_sanskrit}"',
        f"section_number: {section_number}",
        f'roman: "{roman}"',
        f'sanskrit_title: "{sanskrit_title}"',
        f'english_title: "{english_title}"',
        f'has_hindi: {str(has_hindi).lower()}',
        f'has_narration: {str(has_narration).lower()}',
        f'has_media: {str(has_media).lower()}',
    ]
    if spotify_en:
        lines.append(f'spotify_en: "{spotify_en}"')
    if spotify_hi:
        lines.append(f'spotify_hi: "{spotify_hi}"')
    if youtube_url is not None and youtube_url != "":
        lines.append(f'youtube_url: "{youtube_url}"')
    lines.extend([
        'status: "published"',
        "---",
        "",
        '<div class="nav-links-chapter">',
        f"{prev_link_html}",
        f"{next_link_html}",
        "</div>",
        "",
        '<!-- TAB 1: COMICS SLIDES (Text displayed below each image) -->',
        '<div class="tab-pane active" id="pane-comics" data-pane="comics">',
        ""
    ]

    # Render each comic slide
    for idx, img_path in enumerate(dest_images, start=1):
        # Extract slide number from filename or index
        m = re.search(r"slide_0*(\d+)", img_path.stem, re.I)
        s_num = int(m.group(1)) if m else idx

        sb_item_en = sb_en_map.get(s_num, {})
        sb_item_hi = sb_hi_map.get(s_num, {})

        title_en = sb_item_en.get("title") or sb_item_en.get("slide_label") or f"Slide {s_num:02d}"
        title_en = re.sub(r"^Slide\s*\d+\s*[-–:]*\s*", "", title_en).strip()

        title_hi = sb_item_hi.get("title") or title_en
        title_hi = re.sub(r"^Slide\s*\d+\s*[-–:]*\s*", "", title_hi).strip()

        caption_en = clean_text_tags(sb_item_en.get("on_slide_text", ""))
        caption_hi = clean_text_tags(sb_item_hi.get("on_slide_text", caption_en))

        is_insight = sb_item_en.get("type") == "insight" or "insight" in title_en.lower()

        slide_card_lines = [
            f'<article class="comic-slide-card" id="slide-{s_num:02d}">',
            '<div class="slide-card-header">',
            f'<span class="slide-badge">Slide {s_num:02d}</span>',
        ]
        if is_insight:
            slide_card_lines.append('<span class="slide-type-badge">Insight</span>')
        slide_card_lines.extend([
            f'<h3 class="slide-title lang-en">{title_en}</h3>',
            f'<h3 class="slide-title lang-hi">{title_hi}</h3>',
            '</div>',
            '<div class="slide-image-wrapper">',
            f'<img src="{web_slides_dir}/{img_path.name}" alt="Slide {s_num:02d} - {title_en}" loading="lazy" />',
            '</div>',
            '<div class="slide-caption-wrapper">',
            f'<p class="slide-caption-text lang-en">{caption_en}</p>',
            f'<p class="slide-caption-text lang-hi">{caption_hi}</p>',
            '</div>',
            '</article>',
            ""
        ])
        lines.extend(slide_card_lines)

    lines.extend([
        "</div>",
        "",
        '<!-- TAB 2: NARRATION & DISCUSSION -->',
        '<div class="tab-pane" id="pane-narration" data-pane="narration">',
        '<div class="narration-view-container">',
        ""
    ])

    # Add Narration Section
    if narration_paragraphs:
        lines.extend([
            '<!-- Saga Storytelling Section -->',
            '<section class="narration-saga-section">',
            '<div class="section-title-bar">',
            '<span class="section-badge">Chapter Saga</span>',
            '<h2 class="section-heading lang-en">Full Narrative</h2>',
            '<h2 class="section-heading lang-hi">संपूर्ण कथा वृत्तांत</h2>',
            "<p class=\"section-subheading lang-en\">Unabridged story based on Manmatha Nath Dutt's Valmiki Ramayana prose translation.</p>",
            '<p class="section-subheading lang-hi">मन्मथ नाथ दत्त के वाल्मीकि रामायण गद्य अनुवाद पर आधारित संपूर्ण कथा।</p>',
            '</div>',
            '<div class="narration-prose-card">',
            '<div class="narration-text-flow lang-en">'
        ])
        for p in narration_paragraphs:
            if p["en"]:
                lines.append(f'<p>{p["en"]}</p>')
        lines.extend([
            '</div>',
            '<div class="narration-text-flow lang-hi">'
        ])
        for p in narration_paragraphs:
            if p["hi"]:
                lines.append(f'<p>{p["hi"]}</p>')
        lines.extend([
            '</div>',
            '</div>',
            '</section>',
            ""
        ])

    # Add Discussion Section
    if discussion_items:
        lines.extend([
            '<!-- Philosophical Discussion & Inquiry Section -->',
            '<section class="discussion-inquiry-section">',
            '<div class="section-title-bar">',
            '<span class="section-badge">Inquiry & Reflection</span>',
            '<h2 class="section-heading lang-en">Discussion & Modern Takeaways</h2>',
            '<h2 class="section-heading lang-hi">दार्शनिक विवेचना एवं जीवन-सूत्र</h2>',
            '<p class="section-subheading lang-en">Ethical inquiry, character motives, and actionable modern wisdom.</p>',
            '<p class="section-subheading lang-hi">चरित्र, नीति और जीवन मूल्यों की गहन पड़ताल तथा आधुनिक जीवन में व्यावहारिक सूत्र।</p>',
            '</div>',
            '<div class="discussion-cards-list">'
        ])
        for i, item in enumerate(discussion_items, start=1):
            lines.extend([
                '<article class="discussion-card">',
                '<div class="discussion-card-header">',
                f'<span class="inquiry-badge">Inquiry {i:02d}</span>',
                '</div>',
                '<div class="discussion-content-block lang-en">',
                f'<h3 class="discussion-question">{item["q_en"]}</h3>',
                '<div class="discussion-reflection">',
                f'<p>{item["r_en"]}</p>',
                '</div>',
                '<div class="takeaway-card">',
                '<div class="takeaway-badge">⚡ Actionable Takeaway</div>',
                f'<p class="takeaway-text">{item["t_en"]}</p>',
                '</div>',
                '</div>',
                '<div class="discussion-content-block lang-hi">',
                f'<h3 class="discussion-question">{item["q_hi"]}</h3>',
                '<div class="discussion-reflection">',
                f'<p>{item["r_hi"]}</p>',
                '</div>',
                '<div class="takeaway-card">',
                '<div class="takeaway-badge">⚡ जीवन-सूत्र (Takeaway)</div>',
                f'<p class="takeaway-text">{item["t_hi"]}</p>',
                '</div>',
                '</div>',
                '</article>'
            ])
        lines.extend([
            '</div>',
            '</section>',
            ""
        ])

    if not has_narration:
        lines.extend([
            '<div class="narration-prose-card" style="text-align: center; padding: 3rem 1.5rem;">',
            '<p class="lang-en" style="color: var(--text-muted); font-size: 1.05rem;">The illustrated comic slides are available in the Comic tab. The full narrative translation for this chapter will appear here soon.</p>',
            '<p class="lang-hi" style="color: var(--text-muted); font-size: 1.05rem;">सचित्र कॉमिक स्लाइड्स कॉमिक टैब में उपलब्ध हैं। इस अध्याय का संपूर्ण कथा अनुवाद जल्द ही यहाँ उपलब्ध होगा।</p>',
            '</div>',
            ""
        ])

    lines.extend([
        '</div>',
        '</div>',
        ""
    ])

    if has_media or spotify_en or spotify_hi:
        spotify_en_embed = to_spotify_embed_url(spotify_en)
        spotify_hi_embed = to_spotify_embed_url(spotify_hi)
        youtube_embed = to_youtube_embed_url(youtube_url)

        lines.extend([
            '<!-- TAB 3: AUDIO & VIDEO -->',
            '<div class="tab-pane" id="pane-media" data-pane="media">',
            '<div class="media-view-container">',
            "",
            '<div class="section-title-bar">',
            '<span class="section-badge">Listen & Watch</span>',
            '<h2 class="section-heading lang-en">Audio & Video Episodes</h2>',
            '<h2 class="section-heading lang-hi">ऑडियो एवं वीडियो प्रसंग</h2>',
            '<p class="section-subheading lang-en">Experience the episode through sound and screen: stream the narrated podcast on Spotify or watch the inline video.</p>',
            '<p class="section-subheading lang-hi">ध्वनि और दृश्य के माध्यम से प्रसंग का अनुभव करें: स्पॉटिफ़ाई पर पॉडकास्ट सुनें या सीधे यहीं वीडियो देखें।</p>',
            '</div>',
            "",
            '<div class="media-sections-wrapper">',
            "",
            '<!-- Audio Card: Spotify -->',
            '<section class="media-card audio-media-card">',
            '<div class="media-card-header">',
            '<div class="media-card-header-left">',
            '<span class="media-type-badge audio-badge">',
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">',
            '<path d="M12 2C6.477 2 2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879V14.89h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12c0-5.523-4.477-10-10-10z"/>',
            '</svg>',
            'Spotify Audio',
            '</span>',
            '<h3 class="media-card-title lang-en">Narrated Podcast Episode</h3>',
            '<h3 class="media-card-title lang-hi">कथा पॉडकास्ट प्रसंग</h3>',
            '</div>',
            '<div class="media-track-indicator">',
            '<span class="track-pill lang-en">English Edition • Narrated by Kavya</span>',
            '<span class="track-pill lang-hi">हिन्दी संस्करण • काव्या द्वारा प्रस्तुत</span>',
            '</div>',
            '</div>',
            "",
            '<div class="media-player-container">'
        ])

        if spotify_en_embed:
            lines.extend([
                '<!-- English Spotify Embed -->',
                '<div class="spotify-embed-wrapper lang-en">',
                f'<iframe style="border-radius:12px" src="{spotify_en_embed}" width="100%" height="232" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>',
                '</div>'
            ])

        if spotify_hi_embed:
            lines.extend([
                '<!-- Hindi Spotify Embed -->',
                '<div class="spotify-embed-wrapper lang-hi">',
                f'<iframe style="border-radius:12px" src="{spotify_hi_embed}" width="100%" height="232" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>',
                '</div>'
            ])

        lines.extend([
            '</div>',
            "",
            '<div class="media-card-footer">',
            '<p class="media-hint lang-en">',
            '💡 <em>Want to listen in Hindi? Use the toolbar language toggle above or <a href="javascript:void(0)" class="quick-lang-switch" data-switch-to="hi">switch to हिन्दी audio</a>.</em>',
            '</p>',
            '<p class="media-hint lang-hi">',
            '💡 <em>अंग्रेज़ी में सुनना चाहते हैं? ऊपर भाषा टॉगल का उपयोग करें या <a href="javascript:void(0)" class="quick-lang-switch" data-switch-to="en">English ऑडियो पर जाएँ</a>।</em>',
            '</p>',
            '</div>',
            '</section>',
            "",
            '<!-- Video Card: YouTube -->',
            '<section class="media-card video-media-card">',
            '<div class="media-card-header">',
            '<div class="media-card-header-left">',
            '<span class="media-type-badge video-badge">',
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">',
            '<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>',
            '</svg>',
            'YouTube Video',
            '</span>',
            '<h3 class="media-card-title lang-en">Visual Chronicle</h3>',
            '<h3 class="media-card-title lang-hi">सचित्र वीडियो कथा</h3>',
            '</div>'
        ])

        if youtube_embed:
            lines.extend([
                '</div>',
                '<div class="media-player-container">',
                '<div class="video-embed-container">',
                f'<iframe src="{youtube_embed}" title="Chapter Video" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen loading="lazy"></iframe>',
                '</div>',
                '</div>'
            ])
        else:
            lines.extend([
                '<span class="media-status-pill">Coming Soon / शीघ्र उपलब्ध</span>',
                '</div>',
                '<div class="media-player-container">',
                '<div class="video-placeholder-box">',
                '<div class="video-placeholder-inner">',
                '<div class="video-play-mock-btn">',
                '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">',
                '<polygon points="5 3 19 12 5 21 5 3" fill="currentColor"></polygon>',
                '</svg>',
                '</div>',
                '<h4 class="video-placeholder-title lang-en">YouTube Video Premiere Coming Soon</h4>',
                '<h4 class="video-placeholder-title lang-hi">यूट्यूब वीडियो प्रसारण शीघ्र आ रहा है</h4>',
                '<p class="video-placeholder-text lang-en">The high-definition animated graphic video will be embedded here for direct inline viewing as soon as it premieres.</p>',
                '<p class="video-placeholder-text lang-hi">उच्च-गुणवत्ता सचित्र एनिमेटेड वीडियो प्रसारण के तुरंत बाद सीधे यहीं इनलाइन देखा जा सकेगा।</p>',
                '</div>',
                '</div>',
                '</div>'
            ])

        lines.extend([
            '</section>',
            "",
            '</div>',
            "",
            '</div>',
            '</div>'
        ])

    lines.extend([
        "",
        '<div class="nav-links-chapter">',
        f"{prev_link_html}",
        f"{next_link_html}",
        "</div>",
        ""
    ])

    new_content = "\n".join(lines)
    with open(dest_index_md, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n✓ Generated local comic post: {dest_index_md}")
    print(f"  Slide count        : {len(dest_images)}")
    print(f"  Narration paragraphs: {len(narration_paragraphs)}")
    print(f"  Discussion inquiries: {len(discussion_items)}")
    print(f"  Hero image         : {first_image_rel}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate local comic post with dual tabs & languages.")
    parser.add_argument("book_arg", nargs="?", help="Book number or 'intro'")
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
            source_dir = DEFAULT_SOURCE_BASE / "Book_0_Introduction"
            if not source_dir.exists():
                source_dir = DEFAULT_SOURCE_BASE / "Introduction"
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
            if not source_dir:
                source_dir = find_source_chapter(TERTIARY_SOURCE_BASE, book_num, chap_num)
        if not dest_dir:
            dest_dir = find_dest_chapter(DEST_BASE, book_num, chap_num)

        if not source_dir or not dest_dir:
            print(f"Error: Could not locate Book {book_num}, Chapter {chap_num}")
            sys.exit(1)

        process_chapter(source_dir, dest_dir, is_intro=False, book_num=book_num, chap_num=chap_num, move_files=args.move)


if __name__ == "__main__":
    main()
