---
name: comic-creator
description: Generates an Astro markdown blog post for a Ramayana comic chapter based on storyboard JSON and comic images, and uploads the images to R2.
---

# Comic Creator Skill

This skill automates the creation of a new comic chapter blog post. It reads the storyboard JSON, maps it to the generated comic images, creates the Markdown file with a specific Comic Layout, and then uploads the images to Cloudflare R2 using the `r2-image-uploader` skill.

## Usage

When the user asks to "create a comic" for a specific book and chapter (e.g., Book 1, Chapter 2):

### 1. Gather Information & Move Assets
Assets are generated via the `museimages` studio into:
- English source images: `~/Documents/comics/ramayana_dutt/Book_XX_.../Book_X_..._Chapter_Y/annotated/` (or `Introduction/Introduction/annotated/` for Intro)
- Hindi source images: `~/Documents/comics/ramayana_dutt/Book_XX_.../Book_X_..._Chapter_Y/annotated_hi/` (or `Introduction/Introduction/annotated_hi/` for Intro)
- English storyboard: `~/Documents/comics/ramayana_dutt/Book_XX_.../Book_X_..._Chapter_Y/comic_storyboard_*.json`
- Hindi storyboard: `~/Documents/comics/ramayana_dutt/Book_XX_.../Book_X_..._Chapter_Y/comic_storyboard_hindi_*.json`

Use the `./move_comics.sh` script to copy assets and generate the local blog post:
```bash
./move_comics.sh <book_number> <chapter_number>
# For Introduction:
./move_comics.sh intro
```
This transfers the English annotated images into `.../annotated/`, Hindi images into `.../annotated_hi/`, and creates/updates `index.md` with both English and Hindi image references.

### 2. Markdown Structure with Dual-Language Support
The comic layout supports instant toggling between English and Hindi.
Each slide includes both image references:
```markdown
## Slide XX - [Slide Title]

![Slide XX - [Slide Title]](./annotated/[filename.jpeg])
![Slide XX - [Slide Title] (Hindi)](./annotated_hi/[filename.jpeg])
```

### 3. Upload Images to R2
After the file is saved/generated, run the `r2-image-uploader` script on the markdown file:
```bash
node .agents/scripts/upload_to_r2.js src/pages/comics/ramayana/Book_XX_.../Book_X_..._Chapter_Y/index.md
```
This will automatically upload both English and Hindi images to the Cloudflare R2 comics bucket, update the image URLs in the Markdown body and frontmatter, and delete the local image files and empty folders.

### 4. Finalize
Verify that the `run_command` was successful, then inform the user that the comic chapter has been generated and images have been uploaded to R2!
