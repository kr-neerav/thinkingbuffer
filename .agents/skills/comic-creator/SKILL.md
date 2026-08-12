---
name: comic-creator
description: Generates an Astro markdown blog post for a Ramayana comic chapter based on storyboard JSON and comic images, and uploads the images to R2.
---

# Comic Creator Skill

This skill automates the creation of a new comic chapter blog post. It reads the storyboard JSON, maps it to the generated comic images, creates the Markdown file with a specific Comic Layout, and then uploads the images to Cloudflare R2 using the `r2-image-uploader` skill.

## Usage

When the user asks to "create a comic" for a specific book and chapter (e.g., Book 1, Chapter 2):

### 1. Gather Information
Use your `list_dir` and `view_file` tools to read the storyboard JSON file from the source directory.
- The source directory format is typically: `/Users/neerav/Documents/Projects/mythology-texts/mythology podcast/ramayana/Book_XX_.../Book_X_..._Chapter_Y/`
- The file is named `comic_storyboard_Book_X_..._Chapter_Y.json`.

Then, verify the comic images exist in the Astro project:
- Target image directory: `src/pages/comics/ramayana/Book_XX_.../Book_X_..._Chapter_Y/annotated/`

### 2. Generate the Markdown Content
Create the content for `index.md` inside the chapter directory: `src/pages/comics/ramayana/Book_XX_.../Book_X_..._Chapter_Y/index.md`.

**Frontmatter:**
Set the `layout`, `title`, `date`, `tags`, and `image_url` (pointing to the relative path of the first slide's image).
```markdown
---
layout: ../../../../../layouts/ComicLayout.astro
title: "Book [Book Number]: [Book Name] - Chapter [Chapter Number]"
date: [Current Date or Chapter Date YYYY-MM-DD]
tags: ["Ramayana", "Comics", "Mythology"]
image_url: "./annotated/[first_slide_filename.jpeg]"
---
```

**Body Content:**
Add placeholder navigation links at the top and bottom:
```markdown
<div class="nav-links-chapter">
  <a href="#" class="prev-link">&larr; Previous Chapter</a>
  <a href="#" class="next-link">Next Chapter &rarr;</a>
</div>
```

Then, loop through the slides in the JSON. For each slide:
1. Output the header: `## Slide XX - [Slide Title]`
2. Output the image reference: `![Slide XX - [Slide Title]](./annotated/[filename.jpeg])`
3. (Do not output `on_slide_text`, scene dialogue, or insight text, as all text is already visually embedded in the image.)

### 3. Save the Markdown File
Use the `write_to_file` tool to save the generated content to `index.md`.

### 4. Upload Images to R2
After the file is saved, run the `r2-image-uploader` script on the new markdown file.
Use the `run_command` tool:
```bash
node .agents/scripts/upload_to_r2.js src/pages/comics/ramayana/Book_XX_.../Book_X_..._Chapter_Y/index.md
```
This will automatically upload the images to the configured R2 bucket, update the image URLs in the Markdown body and frontmatter, and delete the local image files.

### 5. Finalize
Verify that the `run_command` was successful, then inform the user that the comic chapter has been generated and images have been uploaded to R2!
