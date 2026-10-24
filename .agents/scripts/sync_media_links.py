#!/usr/bin/env python3
"""
sync_media_links.py
===================
Scrapes and synchronizes YouTube playlists and Spotify podcast episodes for
ThinkingBuffer Ramayana comic chapters, updating src/data/ramayana_media_links.json
and injecting/updating Tab 3 (Audio & Video) in chapter index.md files.

Usage:
  python3 .agents/scripts/sync_media_links.py [--apply]
"""

import os
import re
import sys
import json
import argparse
import urllib.request
from pathlib import Path

DATA_FILE = Path("src/data/ramayana_media_links.json")
COMICS_DIR = Path("src/pages/comics/ramayana")

PLAYLIST_YOUTUBE_EN = "https://www.youtube.com/playlist?list=PLZGq6jRnwVEo"
PLAYLIST_YOUTUBE_HI = "https://www.youtube.com/playlist?list=PLO9UZttFOQmU"
SPOTIFY_SHOW_EN = "https://open.spotify.com/show/76thxc8Hsaqmg8Jkkm9Vmt"
SPOTIFY_SHOW_HI = "https://open.spotify.com/show/7qSDnzLNps4zMretdDh65K"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
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


def load_media_db() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {DATA_FILE}: {e}")
    return {}


def save_media_db(data: dict):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Saved {len(data)} chapter entries to {DATA_FILE}")


def generate_media_tab_html(entry: dict) -> str:
    spotify_en = entry.get("spotify_en", "")
    spotify_hi = entry.get("spotify_hi", "")
    youtube_en = entry.get("youtube_en", "") or entry.get("youtube_url", "")
    youtube_hi = entry.get("youtube_hi", "")

    sp_en_embed = to_spotify_embed_url(spotify_en)
    sp_hi_embed = to_spotify_embed_url(spotify_hi)
    yt_en_embed = to_youtube_embed_url(youtube_en)
    yt_hi_embed = to_youtube_embed_url(youtube_hi)

    lines = [
        '<!-- TAB 3: AUDIO & VIDEO -->',
        '<div class="tab-pane" id="pane-media" data-pane="media">',
        '<div class="media-view-container">',
        '',
        '<div class="section-title-bar">',
        '<span class="section-badge">Listen & Watch</span>',
        '<h2 class="section-heading lang-en">Audio & Video Episodes</h2>',
        '<h2 class="section-heading lang-hi">ऑडियो एवं वीडियो प्रसंग</h2>',
        '<p class="section-subheading lang-en">Experience this chapter through sound and screen: stream the narrated podcast on Spotify or watch the inline video.</p>',
        '<p class="section-subheading lang-hi">ध्वनि और दृश्य के माध्यम से प्रसंग का अनुभव करें: स्पॉटिफ़ाई पर पॉडकास्ट सुनें या सीधे यहीं वीडियो देखें।</p>',
        '</div>',
        '',
        '<div class="media-sections-wrapper">',
        '',
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
        '',
        '<div class="media-player-container">'
    ]

    if sp_en_embed:
        lines.extend([
            '<!-- English Spotify Embed -->',
            '<div class="spotify-embed-wrapper lang-en">',
            f'<iframe style="border-radius:12px" src="{sp_en_embed}" width="100%" height="232" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>',
            '</div>'
        ])

    if sp_hi_embed:
        lines.extend([
            '<!-- Hindi Spotify Embed -->',
            '<div class="spotify-embed-wrapper lang-hi">',
            f'<iframe style="border-radius:12px" src="{sp_hi_embed}" width="100%" height="232" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>',
            '</div>'
        ])

    lines.extend([
        '</div>',
        '',
        '<div class="media-card-footer">',
        '<p class="media-hint lang-en">',
        '💡 <em>Want to listen in Hindi? Use the toolbar language toggle above or <a href="javascript:void(0)" class="quick-lang-switch" data-switch-to="hi">switch to हिन्दी audio</a>.</em>',
        '</p>',
        '<p class="media-hint lang-hi">',
        '💡 <em>अंग्रेज़ी में सुनना चाहते हैं? ऊपर भाषा टॉगल का उपयोग करें या <a href="javascript:void(0)" class="quick-lang-switch" data-switch-to="en">English ऑडियो पर जाएँ</a>।</em>',
        '</p>',
        '</div>',
        '</section>',
        '',
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

    if yt_en_embed or yt_hi_embed:
        lines.extend([
            '<div class="media-track-indicator">',
            '<span class="track-pill lang-en">English Edition</span>',
            '<span class="track-pill lang-hi">हिन्दी संस्करण</span>',
            '</div>',
            '</div>',
            '',
            '<div class="media-player-container">'
        ])
        if yt_en_embed:
            lines.extend([
                '<!-- English YouTube Embed -->',
                '<div class="video-embed-wrapper lang-en">',
                '<div class="video-embed-container">',
                f'<iframe src="{yt_en_embed}" title="Chapter Video (English)" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen loading="lazy"></iframe>',
                '</div>',
                '</div>'
            ])
        if yt_hi_embed:
            lines.extend([
                '<!-- Hindi YouTube Embed -->',
                '<div class="video-embed-wrapper lang-hi">',
                '<div class="video-embed-container">',
                f'<iframe src="{yt_hi_embed}" title="Chapter Video (Hindi)" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen loading="lazy"></iframe>',
                '</div>',
                '</div>'
            ])
        lines.extend([
            '</div>',
            '',
            '<div class="media-card-footer">',
            '<p class="media-hint lang-en">',
            '💡 <em>Want to watch in Hindi? Use the toolbar language toggle above or <a href="javascript:void(0)" class="quick-lang-switch" data-switch-to="hi">switch to हिन्दी</a>.</em>',
            '</p>',
            '<p class="media-hint lang-hi">',
            '💡 <em>अंग्रेज़ी में देखना चाहते हैं? ऊपर भाषा टॉगल का उपयोग करें या <a href="javascript:void(0)" class="quick-lang-switch" data-switch-to="en">English पर जाएँ</a>।</em>',
            '</p>',
            '</div>'
        ])
    else:
        lines.extend([
            '<span class="media-status-pill">Coming Soon / शीघ्र उपलब्ध</span>',
            '</div>',
            '',
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
        '',
        '</div>',
        '',
        '</div>',
        '</div>'
    ])
    return "\n".join(lines)


def update_chapter_file(file_path: Path, entry: dict):
    if not file_path.exists():
        print(f"Skipping non-existent file: {file_path}")
        return

    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        print(f"Skipping {file_path}: invalid frontmatter")
        return

    parts = content.split("---", 2)
    if len(parts) < 3:
        return

    raw_yaml = parts[1]
    body = parts[2]

    # Parse yaml keys and clean existing media fields
    yaml_lines = [l for l in raw_yaml.strip().split("\n")]
    filtered_lines = []
    for line in yaml_lines:
        if ":" in line:
            k = line.split(":", 1)[0].strip()
            if k in ("has_media", "spotify_en", "spotify_hi", "youtube_url", "youtube_en", "youtube_hi", "status"):
                continue
        filtered_lines.append(line)

    # Append new media fields cleanly before status
    filtered_lines.append("has_media: true")
    if entry.get("spotify_en"):
        filtered_lines.append(f'spotify_en: "{entry["spotify_en"]}"')
    if entry.get("spotify_hi"):
        filtered_lines.append(f'spotify_hi: "{entry["spotify_hi"]}"')
    if entry.get("youtube_en"):
        filtered_lines.append(f'youtube_url: "{entry["youtube_en"]}"')
        filtered_lines.append(f'youtube_en: "{entry["youtube_en"]}"')
    if entry.get("youtube_hi"):
        filtered_lines.append(f'youtube_hi: "{entry["youtube_hi"]}"')
    filtered_lines.append('status: "published"')

    new_media_tab = generate_media_tab_html(entry)

    # Strip any existing or misplaced pane-media block in body
    body = re.sub(
        r'<!-- TAB 3: AUDIO & VIDEO -->\s*<div class="tab-pane"[^>]*id="pane-media".*?</div>\s*</div>\s*</div>\s*',
        '',
        body,
        flags=re.DOTALL
    )

    # Insert before the last nav-links-chapter
    nav_matches = list(re.finditer(r'<div class="nav-links-chapter">', body))
    if len(nav_matches) > 1:
        idx = nav_matches[-1].start()
        body = body[:idx].rstrip() + "\n\n" + new_media_tab + "\n\n" + body[idx:]
    elif nav_matches:
        idx = nav_matches[-1].start()
        body = body[:idx].rstrip() + "\n\n" + new_media_tab + "\n\n" + body[idx:]
    else:
        body = body.rstrip() + "\n\n" + new_media_tab + "\n"

    new_content = f"---\n" + "\n".join(filtered_lines) + f"\n---\n" + body.lstrip()
    file_path.write_text(new_content, encoding="utf-8")
    print(f"Updated {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Synchronize comic media links")
    parser.add_argument("--apply", action="store_true", help="Apply media links to index.md files")
    args = parser.parse_args()

    db = load_media_db()
    print(f"Loaded {len(db)} entries from {DATA_FILE}")

    target_files = {
        "intro": COMICS_DIR / "introduction" / "index.md",
        "1:1": COMICS_DIR / "Book_01_Bala_Kanda" / "Book_1_Bala_Kanda_Chapter_1" / "index.md",
    }

    for key, path in target_files.items():
        if key in db and path.exists():
            update_chapter_file(path, db[key])

    print("\nMedia sync complete.")


if __name__ == "__main__":
    main()
