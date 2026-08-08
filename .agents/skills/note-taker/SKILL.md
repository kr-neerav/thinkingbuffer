---
name: note-taker
description: >-
  Use this skill when the user wants to capture notes, store thoughts, or save information in a temporary space for later retrieval or processing.
---

# Note Taker Skill

This skill handles capturing and managing notes for the user. It provides a simple way to store thoughts, code snippets, or any other information temporarily, and later retrieve or process them.

## Storage Location

All notes should be stored in the following directory within the workspace:
`.agents/notes/`

## Workflows

### Capturing Notes
When the user asks to take a note, capture a thought, or save some information:
1. If this is the first note, you may need to ensure the `.agents/notes/` directory exists.
2. Create or append the note to a file in `.agents/notes/`. 
   - If the user doesn't specify a file name, append the note to `.agents/notes/scratchpad.md`.
   - If the note is about a specific topic, you can create a dedicated markdown file (e.g., `.agents/notes/architecture.md`).
3. Format the note clearly using markdown. Add a timestamp and any relevant context (like what the user was reading or working on).
4. Briefly confirm to the user that the note has been saved.

### Retrieving and Processing Notes
When the user asks to review, summarize, or retrieve their notes:
1. Read the contents of `.agents/notes/scratchpad.md` or other relevant files in the `.agents/notes/` directory.
2. Present the notes to the user, or perform the requested action (e.g., summarizing, organizing, or extracting action items).
