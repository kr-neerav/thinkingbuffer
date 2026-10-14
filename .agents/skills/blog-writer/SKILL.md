---
name: blog-writer
description: Drafts personal-brand engineering blog posts in Markdown using a two-phase text-then-visuals workflow, natural skimmability rules, bot-safe link verification, and personal experience storytelling. Use when the user asks to plan, draft, edit, or publish a blog post.
---

# Blog Writer Skill

When the user asks you to draft or help write a blog post using this skill, follow Section 5 in order. Sections 1-4 are the acceptance rules applied during drafting. Section 6 governs skill edits. Do not write a blog post when the user asks about the skill itself.

## 1. Audience and Brand Outcome

- **Target audience:**
  - **Default:** Mid-to-Senior Software and Data Engineers, Tech Leads, and Engineering Managers who want practical, production-tested patterns rather than introductory tutorials.
  - **Per-post override:** If the user specifies a different target reader role and level for a post, use that override. If the user's topic clearly targets a non-engineering audience and no role/level was stated, ask outside the draft: `What is the target reader role and level for this post?` and pause until answered.
- **Brand voice:**
  - **Default traits:** Pragmatic, direct, battle-tested, curious, and concrete.
  - **Reference cadence:** "We cut shuffle spill by 60% not by adding cluster nodes, but by fixing one skewed join key."
- **Brand outcome each post must achieve:** Every post MUST do all four:
  1. State the reader's takeaway in a `> Takeaway:` blockquote placed directly after the H1 heading. The blockquote MUST be one sentence of 10-25 words.
  2. End with a section headed `## What to do next` containing 1-3 imperative sentences (each starting with a verb).
  3. Match the brand voice traits defined above without conversational throat-clearing.
  4. Anchor the core insight in the author's real-world personal experience using a 4-part arc:
     - **Situation:** The concrete system, team, or workflow involved.
     - **Friction:** What broke, scaled poorly, or surprised the author.
     - **Decision:** The specific trade-off or approach chosen (and what was rejected).
     - **Outcome:** The concrete result, metric, or lesson learned.
- **Acceptance check:** A critic rejects the draft if any of the four items above is missing, or if the personal experience is invented rather than supplied by the author.

## 2. Writing Style - Observable Checks

Every bullet below is checked by counting or by searching the text. If a check fails, the line number fails.

- **Paragraph limit:** Each body paragraph MUST be 1-4 sentences and 1-100 words. Headings, code blocks, tables, blockquotes, and list items are exempt from the paragraph word count. Each list item MUST be 1-3 sentences.
- **Sentence limit and cadence:** Each sentence MUST be 1-30 words, counted by splitting on spaces, with an average sentence length across the post of 12-20 words. Short punchy sentences (1-4 words) are encouraged for rhythm and emphasis. Headings, code, URLs, blockquotes, and table cells are exempt.
- **No repetition (searchable):** The draft MUST NOT contain (a) two identical sentences of 6 or more words, or (b) the same 8-word sequence in two different paragraphs. Quoted sources, code blocks, standard multi-word technical noun phrases (for example `Apache Spark driver memory` or `dead letter queue`), and the `> Takeaway:` sentence callback in `## What to do next` are exempt.
- **Unique headings:** Every `##` heading text MUST be unique within the post. Headings MUST follow hierarchy with no skipped level (`#` then `##` then `###`).
- **Acronyms:** An acronym is defined as 2 or more consecutive uppercase letters (A-Z), optionally including trailing digits (searchable pattern `[A-Z]{2,}[0-9]*`).
  - **Scope:** Applies to body paragraphs and list items only; exempts headings, code blocks, table cells, the `> Takeaway:` blockquote, direct quotations, and literal UI labels.
  - **Universal allowlist (no expansion required):** `API`, `REST`, `gRPC`, `JSON`, `YAML`, `XML`, `CSV`, `HTML`, `CSS`, `HTTP`, `HTTPS`, `TCP`, `IP`, `DNS`, `URL`, `URI`, `SQL`, `CLI`, `SDK`, `IDE`, `PR`, `CI`, `CD`, `AWS`, `GCP`, `EC2`, `S3`, `EMR`, `CPU`, `GPU`, `RAM`, `SSD`, `IO`, `UI`, `UX`, `AI`, `ML`, `LLM`, `RAG`, `SLA`, `SLO`, `KPI`, `ROI`, `OK`, `ID`, `US`, `UTC`, and HTTP status or heading tokens (`2xx`, `4xx`, `5xx`, `H1`, `H2`, `H3`).
  - **Expansion rule:** On first use in body text of any acronym NOT on the allowlist, write the full term followed by the acronym in parentheses (pattern: `Full Term (ABC)`). Later uses SHOULD use only the acronym.
- **Cross-domain analogy (required when marked):** If any `##` heading text contains the case-insensitive whole word `how` or `why`, the post MUST contain at least one cross-domain analogy in natural prose, preceded immediately by an HTML comment marker: `<!-- Analogy: <source domain> -->`. The `<source domain>` MUST name a non-software domain (for example navigation, mechanics, cooking, sports, gardening, aviation, or driving). Do not print the literal prefix `Analogy (domain):` in visible reader text. A critic verifies the trigger by searching `##` headings for `how`/`why` and verifies the marker by searching for `<!-- Analogy:`.
- **Banned vocabulary and filler:** The draft MUST NOT contain the case-insensitive whole words `accountant`, `receipt`, `receipts`, `filing cabinet`, `filing cabinets`, `synergy`, `synergies`, `very`, `really`, `quite`, `basically`, `delve`, `crucial`, `robust`, `comprehensive`, `nuanced`, `multifaceted`, `furthermore`, `moreover`, `additionally`, `pivotal`, `landscape`, `tapestry`, `underscore`, `foster`, `showcase`, `intricate`, `vibrant`, `fundamental`, `significant`, or the phrase `in today's fast-paced world`. A critic runs a text search for these strings.
- **Zero em dashes:** The draft MUST NOT contain em dashes (`—`). Use standard hyphens, colons, parentheses, or periods instead. A critic runs a text search for `—`.
- **Lead with the point and be concrete:** The opening body paragraph MUST state the core premise immediately without conversational throat-clearing or preambles. Technical claims MUST name concrete tools, protocols, artifacts, or real numbers rather than generic abstractions.
- **Title match:** The first line of the Markdown body MUST be `# <title>` where `<title>` is character-identical to the `title:` value in the frontmatter.
- **Markdown hygiene:** Code MUST be in fenced blocks with a language tag (for example ` ```python `). Links MUST use `[text](target)` form with non-empty text and target. Images MUST use `![alt](src)` form covered in Section 3.

## 3. Visuals, Images, and Formatting - Required Versus Optional

### 3.1 What is required versus optional

- **Hero image - REQUIRED:** Every post MUST set `heroImage:` in frontmatter to a file in the same directory as the post (form `./<lowercase-hyphenated-name>.jpg`).
  - **Double-render guard:** Check whether the repo's `Layout.astro` automatically renders `heroImage` from frontmatter. If `Layout.astro` does NOT render it, place `![<alt>](./<hero-file-name>.jpg)` once in the Markdown body directly after the `> Takeaway:` block, followed immediately on the next line by `*Caption: <4-15-word text>*`. If `Layout.astro` DOES render `heroImage` automatically, set `heroAlt:` and `heroCaption:` in frontmatter instead and do NOT duplicate the hero image tag in the Markdown body.
- **Inline images - REQUIRED by length:** Every post MUST include at least the hero image plus inline images by word count: 1 inline image for posts up to 800 words, 2 for 801-1600 words, and 1 additional image per extra 800-word block. Additional images beyond the minimum are OPTIONAL. Word count is measured on body text excluding frontmatter, code blocks, and tables.
- **Diagrams (Mermaid) - REQUIRED conditionally, otherwise PROHIBITED unless requested:** When the post describes (a) a sequence of 3 or more steps, (b) a system of 2 or more components with a labeled relationship, or (c) a decision with 2 or more branches, the post MUST include at least one fenced `mermaid` block. When none of (a)-(c) is present, the post MUST NOT include a diagram unless the user explicitly requests one.
- **Tables - REQUIRED conditionally:** When comparing 2 or more items across 2 or more attributes, present the comparison as a Markdown table with a header row and one row per item. Otherwise tables are OPTIONAL.
- **Lists - REQUIRED conditionally:** Any run of 3 or more items, steps, or options MUST be a bulleted or numbered list, not a paragraph. Shorter runs may be inline text.
- **Blockquotes - RESTRICTED:** Use `>` only for (a) the required `> Takeaway:` line or (b) a direct quotation followed on the next line by `-- Attribution`. Do not use blockquotes for emphasis.
- **Bold - SCOPED FOR SKIMMABILITY:** Use `**` only for:
  1. **List lead-ins:** The short introductory label at the start of a bullet or numbered item (pattern: `- **Short label:** explanation...`).
  2. **Key concept phrase:** At most ONE short phrase (2-6 words) per body paragraph to aid reader skimming.
  3. **Defined terms:** The first use of a formally defined term (`<Term> means ...` or `<Term> is ...`).
  4. **Literal UI labels:** Exact button, menu, CLI flag, or field names.
  Never bold an entire sentence of 7 or more words.
- **Code snippets - CONDITIONAL:** Include a fenced code block only when the post gives implementation steps, configuration, SQL/code transformations, or commands. Do not include placeholder code with no executable content.

### 3.2 Image sizes, paths, and alt text

- **Size and format (all raster images):** Aspect ratio 16:9; maximum width 1200 px; JPEG format with quality setting 55-65 inclusive (target 60). Resize and compress the generated file to meet this specification before finalizing, then delete the uncompressed source (such as the original PNG) so only the final `.jpg` is saved.
  - **Compression tooling order of preference:** Use `magick` (ImageMagick), `sips` (macOS built-in), `ffmpeg`, or Python `Pillow` (`PIL`) to resize to `<=1200px` 16:9 and save as JPEG at quality 60.
- **Save location and reference:** Save every image in the exact same directory as the post Markdown file and reference it with a relative path of the form `![alt text](./filename.jpg)`. FORBIDDEN: machine-specific absolute paths, `public/images/` paths, `placeholder-image-url` targets, and remote hotlinks.
- **File names:** Lowercase, hyphen-separated, ending in `.jpg` (pattern: `./<lowercase-hyphenated-name>.jpg`).
- **Alt-text convention:** Every image MUST have non-empty alt text of 4-15 words that names the concrete subject plus context and includes at least one keyword from the post title or `> Takeaway:` sentence. Alt text MUST NOT contain the strings `placeholder`, `image-url`, or `image of`.
- **Look (checkable on the image):** Generated or selected images MUST depict real-world photography, clean architectural sketches, or physical objects/environments. They MUST NOT contain neon glow, glowing grid lines, cyber-grids, or futuristic 3D-render styling.
- **Concept check:** The hero image alt text and the hero image caption (`*Caption: <4-15-word text>*` or `heroCaption:`) MUST each contain the same takeaway keyword by case-insensitive whole-word string match. The takeaway keyword is defined as one whole word of 4 or more characters selected by the writer from the `> Takeaway:` sentence.

## 4. External Links and Book URLs - No Guessed URLs

- **Hard ban:** NEVER write, guess, estimate, or construct a URL, ASIN, ISBN link, or DOI from memory. NEVER reuse a link from another draft without re-verifying. Every link in the delivered Markdown MUST be either verified per the steps below or replaced with an explicit fallback.
- **Book-link verification procedure (bot-safe, follow in order):**
  1. Web-search or query a public book metadata API for the exact title and author to obtain the 10-character `ISBN-10` (digits, last character may be `X`).
  2. Verify the `ISBN-10` and book title using a curl-friendly metadata API (since direct `curl` requests to Amazon trigger automated CAPTCHA/503 blocks):
     - **Option A (OpenLibrary):** `curl -sL "https://openlibrary.org/isbn/<ISBN-10>.json"`
     - **Option B (Google Books):** `curl -sL "https://www.googleapis.com/books/v1/volumes?q=isbn:<ISBN-10>"`
     Confirm that the HTTP response is `200` and the returned JSON `title` matches the requested book title.
  3. Once verified via API, form the canonical link by substitution: `https://www.amazon.com/dp/<ISBN-10>`. Record the check as an HTML comment directly above the paragraph or list item containing the link: `<!-- verified YYYY-MM-DD, ISBN-10 <ISBN-10> confirmed via API, title matches -->`.
  4. **Fallback (mandatory if step 1 or 2 fails):** Do NOT publish an unverified `/dp/` product link. Instead use either (a) a labeled search link of the form `https://www.amazon.com/s?k=<URL-encoded-Title-Author>` with link text suffixed `(search)` or (b) no link plus the inline marker `[TBD: verify book link for <Title> by <Author>]`. List every fallback link in a `<!-- unverified links: ... -->` comment at the bottom of the draft.
- **All other external links (same bar):** Use only a URL verified in the current session. Verify each with an HTTP check (`curl -I -L -s -o /dev/null -w "%{http_code}" <url>` returning `2xx` or `3xx` to a valid destination). If verification fails or blocks automated requests, replace the link with `[TBD: verify URL for <description>]` and list it in the bottom `unverified links` comment.
- **Acceptance check:** Any direct book or external URL that lacks a `verified` comment or `[TBD: verify ...]` marker fails the draft.

## 5. Workflow - Two-Phase Order of Operations

Perform these steps in this order for every post.

1. **Gather context (Stop and Ask if Missing).**
   Check that you have all three required post inputs from the user:
   - **Topic and core thesis**
   - **Key points or outline**
   - **Personal experience connecting to the topic** (Situation, Friction, Decision, Outcome)
   If any of these is missing, ask the user outside the draft (specifically asking: `What personal experience or project backstory (situation, friction, decision, and outcome) connects you to this topic?`) and **stop until answered**. Do not draft on assumed facts or invent personal anecdotes. Also inspect the repo once to detect the relative path to `Layout.astro` if not already known.

2. **Phase 1 - Draft and Verify Markdown Text (Before Generating Raster Images).**
   Apply Sections 1-4 to write the full Markdown draft, including Mermaid diagrams, verified external links, and planned image alt-text/captions:
   ```yaml
   ---
   layout: ../../../../layouts/Layout.astro # Adjust to exact relative path in repo if different
   title: "Post title, identical to the H1"
   date: YYYY-MM-DD
   description: "One sentence, 10-25 words"
   tags: ["tag-one", "tag-two"]
   heroImage: "./hero-file-name.jpg"
   ---
   ```
   - Field rules: `date` MUST be `YYYY-MM-DD`; `tags` MUST be 1-5 lowercase hyphenated tags; `heroImage` MUST be `./<lowercase-hyphenated-name>.jpg`.
   - Run a self-check against Section 1 (4 outcomes), Section 2 (paragraph/sentence limits, 8-word repetition, acronym allowlist, `<!-- Analogy: ... -->` marker, banned words, zero em dashes), and Section 4 (link verification comments).
   - Present the draft text and proposed image prompts/captions to the user for quick editorial sign-off (unless the user explicitly asked to generate and save everything in a single pass).

3. **Phase 2 - Generate Visuals, Save Files, and Upload to R2.**
   Once the text and `> Takeaway:` keyword are locked in:
   - Save the post under the repo-relative directory `src/pages/blog/YYYY/MM/<slug>.md` where `YYYY/MM` matches the frontmatter `date`.
   - Generate or process the hero image and required inline images (`16:9`, width `<=1200 px`, JPEG quality `55-65` target `60`), save them in `src/pages/blog/YYYY/MM/<image-name>.jpg`, and delete any intermediate uncompressed `.png` files.
   - Reference images initially as `./<image-name>.jpg`. NEVER use machine-specific absolute paths (`/Users/`, `/home/`, `C:\`).
   - Run the R2 upload script to upload local images and update Markdown URLs:
     ```bash
     node .agents/scripts/upload_to_r2.js src/pages/blog/YYYY/MM/<slug>.md
     ```
     This script uploads the local `.jpg` files to Cloudflare R2, swaps local image markdown links to public R2 URLs, and deletes the local files.

4. **Report Verification and Request Feedback.**
   Present a concise verification summary containing:
   - Saved relative file paths (`src/pages/blog/YYYY/MM/...`)
   - Link verification comments
   - Image dimensions, aspect ratio, and JPEG quality settings
   - Takeaway keyword matched across `> Takeaway:`, hero alt text, and hero caption
   - R2 upload status
   Ask what to adjust. Do not edit `SKILL.md` at this stage (see Section 6).

## 6. Continuous Improvement - Scoped and Safe Updates

- **What triggers a skill edit:** Only a persistent preference triggers an edit: the user writes `always`, `from now on`, or `update the skill`, OR the user repeats the same concrete preference on two separate drafts.
- **What needs user confirmation first:** ALL edits to this `SKILL.md` file require explicit user approval of the exact replacement wording before the file is changed. Propose the diff, wait for an explicit yes, then edit. Silent or automatic edits are FORBIDDEN.
- **One draft never rewrites the skill:** A one-time instruction for the current draft (for example `make this one shorter` without `always`) applies only to that draft file and MUST NOT change `SKILL.md`. If ambiguous, ask: `Is this a one-time preference for this draft or a permanent rule for future posts?` and proceed based on the answer.
- **How to reference the skill file:** Refer to it as `this SKILL.md file`. Do not record absolute paths to it.
- **Acceptance check:** A critic approves a skill edit only if the chat shows (a) a persistent-preference trigger, (b) a proposed wording, and (c) an explicit user yes before the edit.