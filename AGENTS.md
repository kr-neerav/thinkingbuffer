## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)

## Media Sources for Comics & Blog

When requested to get audio/video links for blog posts or comic chapters, access these playlists and shows:

### YouTube Playlists
- English: `https://www.youtube.com/playlist?list=PLZGq6jRnwVEo`
- Hindi: `https://www.youtube.com/playlist?list=PLO9UZttFOQmU`

### Spotify Shows
- English: `https://open.spotify.com/show/76thxc8Hsaqmg8Jkkm9Vmt?si=cr05k4mwTg2osNu26mowTw`
- Hindi: `https://open.spotify.com/show/7qSDnzLNps4zMretdDh65K?si=1nEWqwAISlOYZouXf7K63w`

### Audio/Video Resolution Workflow
1. Access the English and Hindi YouTube playlists to extract the chapter's video URL (`youtube_url`).
2. Access the English and Hindi Spotify shows to locate the chapter's episode URLs (`spotify_en`, `spotify_hi`).
3. Embed or update these URLs in chapter frontmatter (`spotify_en`, `spotify_hi`, `youtube_url`) and render them into Tab 3 (Audio & Video).
