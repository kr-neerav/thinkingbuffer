---
name: design-guidelines
description: Follow these guidelines whenever proposing or implementing design changes to the Thinking Buffer website.
---

# Thinking Buffer Design Guidelines

Follow these guidelines strictly whenever you are asked to design, update, or propose changes to the website.

## 1. Core Aesthetic (Soft Minimal Premium)
- **Soft Minimal Premium**: The design should be clean and airy, but elevated with a premium feel. Use soft, subtle drop shadows, rounded corners, and smooth pastel gradients.
- **Typography**: The site uses the `Inter` font. Keep typography crisp and legible. Use clear heading hierarchies (`h1` through `h6`) with tight letter spacing (`letter-spacing: -0.02em`).
- **Card UI**: Content blocks (blogs, comics) should be presented as "cards" with a white background, rounded corners (e.g., `border-radius: 16px`), and a very soft, diffused shadow (`box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08)`). Do not use harsh borders on cards.

## 2. Layout Structure
- **App Container**: The main website content is housed inside a massive floating rounded container, rather than stretching across the entire browser window. The outer body background is a slightly darker, neutral off-white/gray to make the app container pop.
- **Hero Sections**: The top of the app container often features a soft pastel gradient background.

## 3. Color System (Light Mode Locked)
- The site relies on a CSS variable system defined in `src/styles/global.css`.
- **Light Mode Only**: To preserve the specific pastel aesthetic from the original mockup, **dark mode inversion is disabled**. The site must always render in light mode.
- **Background Gradient**: The hero background uses a soft, blended gradient moving from a light peachy/orange (`#FFEEDB`) at the top left to a pastel blue (`#E5EEF9`) at the top right, fading down to a solid off-white (`#F8F9FA`).
- Do not hardcode colors in components. Always use the predefined CSS variables.

## 4. Media & Assets
- **External CDN for Large Media**: High-resolution images (like comics) MUST NOT be stored in the repository. They are hosted on Cloudflare CDN.
- When adding new comics or media-heavy posts, you must reference the external Cloudflare URL in the Markdown frontmatter (e.g., `image_url: "https://..."`) and render it from there.

## 5. Technology Stack
- **Framework**: Astro (Zero JS by default)
- **Styling**: Vanilla CSS. Do not introduce Tailwind CSS or other utility frameworks unless explicitly requested by the user.
