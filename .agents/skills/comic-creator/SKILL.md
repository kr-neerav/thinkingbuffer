---
name: comic-creator
description: Generates an Astro markdown blog post for a Ramayana comic chapter with three tabs (Comics, Narration & Discussion, Audio & Video) and bilingual toggle (English + Hindi) based on studio images, storyboards, narration, discussion JSON, and media embeds.
---

# Comic Creator Skill

This skill automates the creation of a new comic chapter post. It reads studio slide images, bilingual storyboards, narration prose, and discussion inquiries from MythologyMuse outputs, generates the markdown file with three view tabs (Comics, Narration & Discussion, Audio & Video), and uploads images to Cloudflare R2 using the `r2-image-uploader` script.

## Usage

When the user asks to create or update a comic chapter (e.g., Book 1, Chapter 1 or Introduction):

### 1. Source Assets Location
Assets are generated into:
`/Users/neerav/Documents/Projects/MythologyMuse/mythologies/ramayana_dutt/outputs/`

Each chapter folder (e.g. `Book_1_Bala_Kanda_Chapter_1` or `Book_0_Introduction`) contains:
- Slide artwork: `<chapter_dir>/studio_images/slide_XX_final.jpg` (Text is not burned into the image; artwork is language-agnostic)
- English storyboard: `comic_storyboard_*.json`
- Hindi storyboard: `comic_storyboard_hindi_*.json`
- Narration: `narration_*.json` (or `english_narration_*.txt` / `hindi_narration_*.txt`)
- Discussion: `discussion_*.json` (Q&A, reflection, and actionable takeaways)

### 2. Generate Local Post
Run `./move_comics.sh`:
```bash
./move_comics.sh <book_number> <chapter_number>
# For Introduction:
./move_comics.sh intro
```
This script:
1. Copies the final slide images into `.../slides/`
2. Syncs the first slide as the chapter hero image in `public/images/comics/`
3. Reads English and Hindi storyboards, narration paragraphs, and discussion inquiries
4. Generates `index.md` with:
   - **Tab 1: Comic**: Each slide presents the artwork with bilingual captions placed directly below the image.
   - **Tab 2: Narration & Discussion**: Full story prose paragraphs followed by structured inquiry cards (Question, Reflection, and Actionable Takeaway).
   - **Tab 3: Audio & Video**: Embedded inline Spotify episode players (bilingual English + Hindi) and embedded YouTube video player (or coming soon preview card).
   - **Language Toggle**: Synchronized switcher for English and Hindi active across all tabs.

### 3. Audio & Video Links
When instructed to fetch or populate audio/video links for a chapter, access these sources:

- **YouTube Playlists**:
  - English: `https://www.youtube.com/playlist?list=PLZGq6jRnwVEo`
  - Hindi: `https://www.youtube.com/playlist?list=PLO9UZttFOQmU`
- **Spotify Shows**:
  - English: `https://open.spotify.com/show/76thxc8Hsaqmg8Jkkm9Vmt?si=cr05k4mwTg2osNu26mowTw`
  - Hindi: `https://open.spotify.com/show/7qSDnzLNps4zMretdDh65K?si=1nEWqwAISlOYZouXf7K63w`

Match the chapter title/number to the corresponding items in the playlist/show, extract the episode and video URLs, and save them in the chapter frontmatter:
```yaml
has_media: true
spotify_en: "https://open.spotify.com/episode/<episode_id>"
spotify_hi: "https://open.spotify.com/episode/<episode_id>"
youtube_url: "https://www.youtube.com/watch?v=<video_id>"
```

### 4. Upload Images to R2
After verifying the local post, upload images to Cloudflare R2:
```bash
node .agents/scripts/upload_to_r2.js src/pages/comics/ramayana/Book_XX_.../Book_X_..._Chapter_Y/index.md
# For Introduction:
node .agents/scripts/upload_to_r2.js src/pages/comics/ramayana/introduction/index.md
```
This command uploads the local slide images to the Cloudflare R2 bucket, updates the URLs in markdown and frontmatter, and deletes local temporary image files.

### 5. Verification
Run `npm run build` or inspect with `astro dev` to verify that tabs and language toggles function properly.
