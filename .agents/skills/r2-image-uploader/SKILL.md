---
name: r2-image-uploader
description: Uploads local images referenced in markdown files to Cloudflare R2 and updates the references.
---

# R2 Image Uploader Skill

This skill ensures that local images added to Markdown files (like blog posts or comics) are automatically uploaded to Cloudflare R2 and their references in the Markdown are updated to use public R2 URLs.

## Usage

Whenever you draft a new blog post or comic, or modify an existing one by adding local images:
1. Ensure the markdown file is saved.
2. Ensure you have the Cloudflare R2 environment variables set up in the `.env` file (`CLOUDFLARE_ACCOUNT_ID`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`, `COMICS_R2_BUCKET_NAME`, `COMICS_R2_PUBLIC_URL`).
3. Run the Node.js script located at `.agents/scripts/upload_to_r2.js`, passing the path to the modified markdown file as an argument.

## Command

```bash
node .agents/scripts/upload_to_r2.js <path-to-markdown-file>
```

Example:
```bash
node .agents/scripts/upload_to_r2.js src/pages/blog/2026/08/my_new_blog.md
```

## Behavior
- The script parses the markdown file for local image references (e.g., `![alt](./image.jpg)`).
- It uploads the local images to the configured R2 bucket, preserving the relative path from the repository root (e.g., `src/pages/blog/2026/08/image.jpg`).
- It replaces the local reference in the markdown file with the public R2 URL.
- It deletes the local image file after a successful upload.

## Note for Agent
Always invoke this script **after** you finish generating and saving images for a new blog post or comic!
