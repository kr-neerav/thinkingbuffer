---
name: blog-writer
description: Drafts personal-brand blog posts in Markdown using observable style checks, required-versus-optional visual rules, verified external links, and an explicit save workflow.
---

# Blog Writer Skill

When the user asks you to draft or help write a blog post using this skill, follow Section 5 in order. Sections 1–4 are the acceptance rules applied during drafting. Section 6 governs skill edits. Do not write a blog post when the user asks about the skill itself.

## 1. Audience and Brand Outcome

- **Audience:** [TBD: ask the user for the target reader role and level; do not assume an audience]. Do not draft until the user supplies the target reader role and level. While this [TBD] is open, ask outside the draft `What is the target reader role and level?` and stop until answered; do not write an `Assumed reader:` line as permission to draft on assumption.
- **Brand outcome each post must achieve:** Every post MUST do all four:
  1. State the reader's takeaway in a `> Takeaway:` blockquote placed directly after the H1 heading. The blockquote MUST be one sentence of 10–25 words.
  2. End with a section headed `## What to do next` containing 1–3 imperative sentences (each starting with a verb).
  3. Use the brand voice defined in [TBD: ask the user for 3–5 named voice traits plus one example sentence; do not invent a voice].
  4. Include the author's real-world personal experience connecting the core insight to concrete engineering practice.
- **Acceptance check:** A critic rejects the draft if any of the four items above is missing or if any draft content was written while the audience [TBD] is still open (no assumed reader role or level is permitted).

## 2. Writing Style — Observable Checks

Every bullet below is checked by counting or by searching the text. If a check fails, the line number fails.

- **Paragraph limit:** Each paragraph MUST be 1–4 sentences and 1–100 words. Headings, code blocks, tables, blockquotes, and list items are exempt from the word count; each list item MUST be 1–2 sentences.
- **Sentence limit:** Each sentence MUST be 5–25 words, counted by splitting on spaces. Headings, code, URLs, blockquotes, and table cells are exempt.
- **No repetition (searchable):** The draft MUST NOT contain (a) two identical sentences of 5 or more words, or (b) the same 5-word sequence in two different paragraphs. Quoted sources, code blocks, and the `> Takeaway:` sentence repeated once in `## What to do next` are exempt.
- **Unique headings:** Every `##` heading text MUST be unique within the post. Headings MUST follow hierarchy with no skipped level (`#` then `##` then `###`).
- **Acronyms:** An acronym is defined as 2 or more consecutive uppercase letters (A–Z), optionally including trailing digits (searchable pattern `[A-Z]{2,}[0-9]*`). This rule applies to body paragraphs and list items only; it does not apply to headings, code blocks, table cells, the `> Takeaway:` blockquote, direct quotations followed by `-- Attribution`, or literal UI labels. On first use in body text of any acronym, write the full term followed by the acronym in parentheses (pattern: `Full Term (ABC)`). Later uses SHOULD use only the acronym; restating the full term or `Full Term (ABC)` again for clarity is allowed and does not fail. A critic searches body text for each acronym to verify the first-use pattern exists.
- **Cross-domain analogy (required when marked):** If any `##` heading text contains the case-insensitive whole word `how` or `why` (found by text search of heading lines), the post MUST contain at least one sentence matching the pattern `Analogy (<source domain>): <comparison>` where `<source domain>` is non-empty. A critic verifies the trigger by searching `##` headings for `how`/`why` and verifies the sentence by searching for the literal string `Analogy (`. If no `##` heading contains `how` or `why`, an `Analogy (<source domain>): <comparison>` sentence is OPTIONAL but, if present, MUST still match the pattern. The `<source domain>` SHOULD name a source domain outside the post topic (for example navigation, mechanics, cooking, sports, gardening, or driving).
- **Banned analogy/content words:** The draft MUST NOT contain the case-insensitive words `accountant`, `receipt`, `receipts`, `filing cabinet`, `filing cabinets`, `synergy`, or `synergies`. A critic runs a text search for these strings.
- **Banned filler words:** The draft MUST NOT contain the case-insensitive whole words `very`, `really`, `quite`, `basically`, `delve`, or the phrase `in today's fast-paced world`. A critic runs a text search.
- **Title match:** The first line of the Markdown body MUST be `# <title>` where `<title>` is character-identical to the `title:` value in the frontmatter.
- **Markdown hygiene:** Code MUST be in fenced blocks with a language tag (e.g., ` ```python `). Links MUST use `[text](target)` form with non-empty text and target. Images MUST use `![alt](src)` form covered in Section 3.

## 3. Visuals, Images, and Formatting — Required Versus Optional

### 3.1 What is required versus optional

- **Hero image — REQUIRED:** Every post MUST set `heroImage:` in frontmatter to a file in the same directory as the post (form `./<lowercase-hyphenated-name>.jpg`) and MUST display that same image once in the body after the `> Takeaway:` block.
- **Inline images — REQUIRED by length:** Every post MUST include at least the hero image plus inline images by word count: 1 inline image for posts up to 800 words, 2 for 801–1600 words, and one additional image per extra 800-word block. Additional images beyond the minimum are OPTIONAL. Word count is measured on body text excluding frontmatter, code blocks, and tables.
- **Diagrams (Mermaid) — REQUIRED conditionally, otherwise PROHIBITED unless requested:** When the post describes (a) a sequence of 3 or more steps, (b) a system of 2 or more components with a labeled relationship, or (c) a decision with 2 or more branches, the post MUST include one fenced `mermaid` block. When none of (a)–(c) is present, the post MUST NOT include a diagram unless the user explicitly requests one.
- **Tables — REQUIRED conditionally:** When comparing 2 or more items across 2 or more attributes, present the comparison as a Markdown table with a header row and one row per item. Otherwise tables are OPTIONAL.
- **Lists — REQUIRED conditionally:** Any run of 3 or more items, steps, or options MUST be a bulleted or numbered list, not a paragraph. Shorter runs may be inline text.
- **Blockquotes — RESTRICTED:** Use `>` only for (a) the required `> Takeaway:` line or (b) a direct quotation followed on the next line by `-- Attribution`. Do not use blockquotes for emphasis.
- **Bold — RESTRICTED:** Use `**` only for (a) the first use of a defined term or (b) literal UI labels (exact button, menu, or field names). A defined term is a term introduced by an explicit definition sentence in the body of the form `<Term> means ...` or `<Term> is ...`, or a term listed in a per-post `### Glossary` list if present. The first use is the first case-insensitive occurrence of that exact term after its definition or glossary entry, found by text search; only that occurrence may be bolded. Do not bold whole sentences.
- **Code snippets — CONDITIONAL:** Include a fenced code block only when the post gives implementation steps, configuration, or commands. Do not include placeholder code with no executable content.

### 3.2 Image sizes, paths, and alt text

- **Size and format (all raster images):** Aspect ratio 16:9; maximum width 1200 px; JPEG format with quality setting 55–65 inclusive (target 60). Resize and compress the generated file to meet this specification before finalizing, then delete the uncompressed source (for example the original PNG) so only the final `.jpg` is saved. A critic checks width ≤1200 px and 16:9 ratio from image dimensions metadata, checks JPEG format from file type/extension, and checks quality from saved-file metadata or the writer-reported setting in Section 5 step 4; a reported setting within 55–65 passes, outside fails.
  - [TBD: preferred resize/compress tool for this repo — ask the user once; until then use any available tool that outputs the specified size and format].
- **Save location and reference:** Save every image in the exact same directory as the post Markdown file and reference it with a relative path of the form `![alt text](./filename.jpg)`. FORBIDDEN: absolute paths, `public/images/` paths, `placeholder-image-url` targets, and remote hotlinks.
- **File names:** Lowercase, hyphen-separated, ending in `.jpg` (pattern: `./<lowercase-hyphenated-name>.jpg`).
- **Alt-text convention:** Every image MUST have non-empty alt text of 4–15 words that names the concrete subject plus context and includes at least one keyword from the post title or `> Takeaway:` sentence. Alt text MUST NOT contain the strings `placeholder`, `image-url`, or `image of`. Example pattern (do not copy wording): `![<4–15-word concrete description containing one title keyword>](./<lowercase-hyphenated-name>.jpg)`.
- **Look (checkable on the image):** Generated or selected images MUST depict real-world photography or physical objects/environments. They MUST NOT contain neon glow, glowing grid lines, cyber-grids, or futuristic 3D-render styling. A critic viewing the image at display size rejects it if any banned styling is visible.
- **Concept check:** The hero image alt text and the hero image caption line MUST each contain the same takeaway keyword by case-insensitive whole-word string match. The takeaway keyword is defined as one whole word of 4 or more characters selected by the writer from the `> Takeaway:` sentence. The caption line is defined as the single line immediately following the body hero-image Markdown line, where that hero-image line itself is placed immediately after the `> Takeaway:` block; the caption line MUST use the exact format `*Caption: <4–15-word text>*` and MUST contain the takeaway keyword. A critic finds the keyword by searching the `> Takeaway:` sentence, then string-matches it in the hero alt text and in the caption line.

## 4. External Links and Book URLs — No Guessed URLs

- **Hard ban:** NEVER write, guess, estimate, or construct a URL, ASIN, ISBN link, or DOI from memory. NEVER reuse a link from another draft without re-verifying. Every link in the delivered Markdown MUST be either verified per the steps below or replaced with an explicit fallback.
- **Book-link verification procedure (follow in order):**
  1. Web-search the exact title and author with `ISBN 10` (query form: `"Book Title" "Author" ISBN 10`). Record the 10-character ISBN-10 (digits, last character may be `X`) as shown by the publisher, bookseller, or library result. Do not strip or alter characters.
  2. Form the canonical link by substitution only: `https://www.amazon.com/dp/<ISBN-10>`.
  3. Verify before publishing with both (i) an HTTP status check (for example `curl -I -L <url>`) and (ii) a full page fetch for the title check (for example `curl -L <url>` followed by inspection of the returned page `<title>`). It passes only if (i) returns 2xx and (ii) the returned page title names the requested book title. Record the check as an HTML comment above the link: `<!-- verified YYYY-MM-DD, HTTP 2xx, title matches -->` with the actual date.
  4. Fallback (mandatory if step 1 or 3 fails): Do NOT publish the unverified product link. Instead use either (a) a labeled search link of the form `https://www.amazon.com/s?k=<URL-encoded-Title-Author>` with link text suffixed `(search)` or (b) no link plus the inline marker `[TBD: verify book link for <Title> by <Author>]`. List every fallback link in a `<!-- unverified links: ... -->` comment at the bottom of the draft.
- **All other external links (same bar):** Use only a URL copied from a page actually visited in this session. Verify each with an HTTP request (2xx expected). If verification fails or no source was visited, replace the link with `[TBD: verify URL for <description>]` and list it in the bottom `unverified links` comment.
- **Acceptance check:** A critic clicks or requests each URL; any link that 404s or redirects to an unrelated product fails the draft. Any direct book/product URL that lacks either a `verified` comment or a `[TBD: verify ...]` marker fails the draft. Exception: a fallback search link exactly in the step 4(a) form `https://www.amazon.com/s?k=<URL-encoded-Title-Author>` with link text suffixed `(search)` is accepted without a `verified` comment when listed in the bottom `<!-- unverified links: ... -->` comment.

## 5. Workflow — Order of Operations

Perform these steps in this order for every post. Sections 1–4 are applied inside step 2.

1. **Gather context.** If the user has not supplied topic, outline or key points, target reader role and level (while Section 1 [TBD] is open), and personal experience connecting to the topic, ask for the missing items (specifically asking outside the draft `What personal experience or backstory connects you to this topic?`) and stop until answered. Do not draft on assumed facts or invent personal anecdotes.
2. **Draft the Markdown.** Apply Sections 1–4. Start the file with YAML frontmatter containing exactly these fields in this order:
   ```yaml
   ---
   layout: [TBD: exact relative path from the post file to Layout.astro — ask the user once and reuse]
   title: "Post title, identical to the H1"
   date: YYYY-MM-DD
   description: "One sentence, 10–25 words"
   tags: ["tag-one", "tag-two"]
   heroImage: "./hero-file-name.jpg"
   ---
   ```
   Field rules: `date` MUST be a calendar date in `YYYY-MM-DD` form; `tags` MUST be a YAML list of 1–5 lowercase hyphenated tags; `heroImage` MUST be the relative path defined in Section 3.2. Leave any unknown value as an explicit `[TBD: ...]` marker — never invent a path, date, tag, or URL.
3. **Save files.** Save the post under the repo-relative directory `src/pages/blog/YYYY/MM/` where `YYYY/MM` is taken from the frontmatter `date`, with a lowercase hyphenated slug filename (pattern: `src/pages/blog/YYYY/MM/<slug>.md`). Save each image in the same directory as the post file (pattern: `src/pages/blog/YYYY/MM/<image-name>.jpg`). Reference images only as `./<image-name>.jpg`. NEVER use machine-specific absolute paths (any path starting with `/Users/`, `/home/`, `C:\`, or similar) and NEVER save blog images elsewhere. If the repo layout differs, stop and ask; mark the correct root as [TBD] rather than guessing.
4. **Request feedback.** Present the saved relative file paths, the verification comments for links, and the image specifications (dimensions and format). Ask what to change. Do not edit SKILL.md at this stage (see Section 6).

## 6. Continuous Improvement — Scoped and Safe Updates

- **What triggers a skill edit:** Only a persistent preference triggers an edit: the user writes `always`, `from now on`, or `update the skill`, OR the user repeats the same concrete preference on two separate drafts.
- **What needs user confirmation first:** ALL edits to this SKILL.md require explicit user approval of the exact replacement wording before the file is changed. Propose the diff, wait for a yes, then edit. Silent or automatic edits are FORBIDDEN.
- **One draft never rewrites the skill:** A one-time instruction for the current draft (for example `make this one shorter` without `always`) applies only to that draft file and MUST NOT change SKILL.md. If ambiguous, ask: `Is this a one-time preference for this draft or a permanent rule for future posts?` and proceed based on the answer.
- **How to reference the skill file:** Refer to it as `this SKILL.md file`. Do not record absolute paths to it.
- **Acceptance check:** A critic approves a skill edit only if the chat shows (a) a persistent-preference trigger, (b) a proposed wording, and (c) an explicit user yes before the edit.