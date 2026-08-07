---
name: blog-writer
description: Assists the user in drafting blog posts in markdown format. Enforces a balanced writing style (not too verbose, not too concise, non-repetitive) and prioritizes highly visual content. Also instructs the agent to automatically update this skill based on ongoing user feedback.
---

# Blog Writer Skill

When the user asks you to draft or help write a blog post using this skill, follow these guidelines strictly:

## 1. Writing Style and Tone
- **Balanced Length:** Do not be overly verbose, but avoid being too brief. Provide enough detail to be easily understood without unnecessary fluff.
- **No Repetition:** Ensure concepts are stated clearly once. Avoid repeating yourself.
- **Easy to Understand:** Use accessible language. Break down complex topics into digestible parts.
- **Cross-Domain Analogies:** When explaining insights, draw relatable analogies from entirely different domains. Don't restrict yourself to technical domains; include examples that would resonate with varied audiences, such as kids, adults, or older generations.
- **Markdown Format:** Always deliver the final draft in clean, well-formatted Markdown.

## 2. Visual Emphasis (Crucial)
The user is a highly visual person. Break up walls of text and illustrate concepts using visual elements wherever possible:
- **Images:** Suggest image placements with descriptive alt text (e.g., `![Abstract visualization of X](placeholder-image-url)`). If appropriate, use your image generation tools to create actual visuals for the blog. 
  - **Concept:** Ensure the generated images surface the *core conceptual theme* of the post (e.g., risk mitigation, earning a future, not just literal interpretations).
  - **Aesthetics (Tactile and Real):** Avoid overly bright, glowing digital imagery, abstract cyber-grid lines, or futuristic 3D renders. Instead, prioritize realistic, tactile, and grounded images. Make them look like real-world photography or scenes containing physical objects and environments that feel tangible and relatable.
  - **Optimization (Crucial for R2 storage):** To ensure images load fast on laptops and don't bloat the user's Cloudflare R2 bucket:
    1. Set the AspectRatio to 16:9 when generating the image.
    2. Before finalizing the post, compress and resize the generated image using the macOS `sips` command. Resize the max width to 1200px and convert to a compressed JPEG (e.g., `sips -Z 1200 -s format jpeg -s formatOptions 60 image.png --out image.jpg`). Remove the original uncompressed PNG.
- **Diagrams:** Use Mermaid.js diagrams (`mermaid` code blocks) to explain workflows, architectures, or relationships.
- **Formatting:** Use tables, bolding, blockquotes, and lists to make the content scannable and visually appealing.
- **Code Snippets:** Use formatted code blocks if discussing technical implementations.

## 3. External Links & Book URLs
- **Reliable Book Links Process:** Never guess, estimate, or construct Amazon ASINs or URLs from memory.
  1. Search specifically for the book's verified **10-digit ISBN-10** (e.g. searching `"Book Title" "Author" ISBN 10`).
  2. Construct the canonical Amazon product link using the verified ISBN-10: `https://www.amazon.com/dp/<ISBN-10>` (for books, the ISBN-10 is the ASIN).
  3. Validate the URL via HTTP request before publishing. If an exact product page cannot be verified, use a clean search link fallback (e.g., `https://www.amazon.com/s?k=Title+Author`).

## 3. Workflow
1. **Context Gathering:** Ask the user for the specific context, topic, or outline if they haven't provided enough details.
2. **Drafting:** Generate the blog post incorporating the style and visual elements mentioned above. Always include YAML frontmatter at the top (including `layout` calculated relative to `Layout.astro`, `title`, `date`, `description`, `tags`) so Astro can parse and display it.
3. **Saving:** Always save the drafted blog posts in the workspace using date-based subfolders under `src/pages/blog/` in the format `src/pages/blog/YYYY/MM/` (e.g., `src/pages/blog/2026/08/blog_draft.md`).
4. **Feedback Loop:** Ask the user for their thoughts on the draft. 

## 4. Continuous Improvement (Self-Updating)
As the user provides feedback on the blogs you write (e.g., "Make it punchier", "Use more diagrams", "Change the tone"), you must **automatically update this `SKILL.md` file** to incorporate their preferences.
- When they give feedback on the writing style, seamlessly run a tool to edit this file (`/Users/neerav/Documents/Projects/thinkingbuffer/.agents/skills/blog-writer/SKILL.md`) to refine the constraints for future use.
