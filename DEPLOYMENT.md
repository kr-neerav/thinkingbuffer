# Deployment Guide

This guide details how to deploy the **thinkingbuffer** website to Cloudflare Pages with automatic git-push deployments.

## 1. Local Git Setup

If you haven't synced your local project with GitHub yet, run the following commands in the root of this project:

```bash
# Initialize a Git repository inside the thinkingbuffer directory
git init

# Make sure the default branch is main
git branch -M main

# Add all files to staging (following the rules in .gitignore)
git add .

# Create the initial commit
git commit -m "Initial commit"

# Add the GitHub remote repository
git remote add origin git@github.com:kr-neerav/thinkingbuffer.git
# (Alternatively, if using HTTPS: https://github.com/kr-neerav/thinkingbuffer.git)

# Push the code to GitHub
git push -u origin main
```

## 2. Cloudflare Pages Configuration

Once your repository is synced to GitHub:

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. In the sidebar, select **Workers & Pages**.
3. Click **Create Application** -> **Pages** tab -> **Connect to Git**.
4. Authorize Cloudflare with your GitHub account, then choose `kr-neerav/thinkingbuffer` from your repositories.
5. In the configuration step:
   - **Project name**: `thinkingbuffer` (or any name you prefer)
   - **Production branch**: `main`
   - **Framework preset**: `Astro`
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
6. In **Environment variables (advanced)**, add:
   - `NODE_VERSION` = `22` (to match the project's requirement of Node `>=22.12.0`)
   - Any other public configuration environment variables your build might require.
7. Click **Save and Deploy**.

Cloudflare will now trigger a build and publish the site. Every future `git push` to the `main` branch will automatically trigger a new deployment.
