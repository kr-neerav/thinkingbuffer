import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import dotenv from 'dotenv';

dotenv.config();

const {
  CLOUDFLARE_ACCOUNT_ID,
  AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY,
  R2_BUCKET_NAME,
  R2_PUBLIC_URL,
  COMICS_R2_BUCKET_NAME,
  COMICS_R2_PUBLIC_URL
} = process.env;

if (!CLOUDFLARE_ACCOUNT_ID || !AWS_ACCESS_KEY_ID || !AWS_SECRET_ACCESS_KEY) {
  console.error('Missing required AWS/Cloudflare credentials in .env file.');
  process.exit(1);
}

const s3Client = new S3Client({
  region: 'auto',
  endpoint: `https://${CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: AWS_ACCESS_KEY_ID,
    secretAccessKey: AWS_SECRET_ACCESS_KEY,
  },
  forcePathStyle: true,
});

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node upload_to_r2.js <path-to-markdown-file>');
  process.exit(1);
}

const markdownFilePath = path.resolve(args[0]);
if (!fs.existsSync(markdownFilePath)) {
  console.error(`File not found: ${markdownFilePath}`);
  process.exit(1);
}

// Ensure the repo root is the current working directory or determine it
// Since this script runs inside the repo, we can find the repo root by looking for package.json or using cwd.
const repoRoot = process.cwd();

async function uploadImages() {
  let content = fs.readFileSync(markdownFilePath, 'utf-8');
  const markdownDir = path.dirname(markdownFilePath);

  // Regex to match markdown images: ![alt](url) and HTML img tags
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  const htmlImgRegex = /<img\s+[^>]*src=["']([^"']+)["'][^>]*>/gi;
  let updatedContent = content;
  
  // Find all candidate image paths
  const localPaths = new Set();
  for (const match of content.matchAll(imageRegex)) {
    localPaths.add(match[2].trim());
  }
  for (const match of content.matchAll(htmlImgRegex)) {
    localPaths.add(match[1].trim());
  }

  // Also check frontmatter image fields
  const fmRegex = /(?:image_url|heroImage|image_url_hi):\s*["']([^"']+)["']/g;
  for (const match of content.matchAll(fmRegex)) {
    localPaths.add(match[1].trim());
  }

  for (const imagePath of localPaths) {
    // Skip remote URLs
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      continue;
    }

    let absoluteImagePath;
    if (imagePath.startsWith('/')) {
      absoluteImagePath = path.join(repoRoot, 'src/pages', imagePath);
      if (!fs.existsSync(absoluteImagePath)) {
        absoluteImagePath = path.join(repoRoot, 'public', imagePath);
      }
    } else {
      absoluteImagePath = path.resolve(markdownDir, imagePath);
    }

    if (!fs.existsSync(absoluteImagePath)) {
      console.warn(`Warning: Image not found locally: ${absoluteImagePath}`);
      continue;
    }

    // Determine the R2 key (relative path from repo root)
    let s3Key = path.relative(repoRoot, absoluteImagePath);
    // Ensure we don't have leading slashes and use forward slashes
    s3Key = s3Key.split(path.sep).join('/');

    let targetBucket = R2_BUCKET_NAME;
    let targetPublicUrl = R2_PUBLIC_URL;

    if (s3Key.includes('comics/')) {
      targetBucket = COMICS_R2_BUCKET_NAME || R2_BUCKET_NAME; // Fallback to default if missing
      targetPublicUrl = COMICS_R2_PUBLIC_URL || R2_PUBLIC_URL;
    }

    if (!targetBucket || !targetPublicUrl) {
      console.error(`Missing bucket or public URL configuration in .env for ${s3Key}`);
      continue;
    }

    console.log(`Uploading ${s3Key} to bucket ${targetBucket}...`);

    const fileBuffer = fs.readFileSync(absoluteImagePath);
    const contentType = getContentType(absoluteImagePath);

    const uploadParams = {
      Bucket: targetBucket,
      Key: s3Key,
      Body: fileBuffer,
      ContentType: contentType,
    };

    let uploaded = false;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        await s3Client.send(new PutObjectCommand(uploadParams));
        uploaded = true;
        break;
      } catch (error) {
        console.warn(`Attempt ${attempt} failed for ${s3Key}: ${error.message || error}`);
        if (attempt < 3) {
          await new Promise(res => setTimeout(res, 1000 * attempt));
        } else {
          console.error(`All retry attempts failed to upload ${s3Key}:`, error);
        }
      }
    }

    if (uploaded) {
      // Remove trailing slash from public URL if it exists
      const cleanPublicUrl = targetPublicUrl.replace(/\/$/, '');
      const newImageUrl = `${cleanPublicUrl}/${s3Key}`;
      
      console.log(`Successfully uploaded. New URL: ${newImageUrl}`);
      
      // Globally replace all occurrences of this path string in content
      const escapedPath = imagePath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pathRegex = new RegExp(escapedPath, 'g');
      updatedContent = updatedContent.replace(pathRegex, newImageUrl);
      
      // Cleanup local file
      console.log(`Deleting local file: ${absoluteImagePath}`);
      fs.unlinkSync(absoluteImagePath);

      // Clean up mirror file in other directory if present
      const altPath = absoluteImagePath.includes('/public/comics/')
        ? absoluteImagePath.replace('/public/comics/', '/src/pages/comics/')
        : (absoluteImagePath.includes('/src/pages/comics/')
          ? absoluteImagePath.replace('/src/pages/comics/', '/public/comics/')
          : null);
      if (altPath && fs.existsSync(altPath)) {
        try { fs.unlinkSync(altPath); } catch (e) {}
      }
    }
  }

  if (content !== updatedContent) {
    fs.writeFileSync(markdownFilePath, updatedContent, 'utf-8');
    console.log(`Updated markdown file: ${markdownFilePath}`);
  } else {
    console.log('No local images found or updated.');
  }

  // Clean up empty directories if left behind
  const dirsToCheck = ['annotated', 'annotated_hi', 'slides'];
  for (const dirName of dirsToCheck) {
    const dirPath = path.join(markdownDir, dirName);
    try {
      if (fs.existsSync(dirPath) && fs.readdirSync(dirPath).length === 0) {
        fs.rmdirSync(dirPath);
        console.log(`Removed empty directory: ${dirPath}`);
      }
    } catch (e) {
      // Ignore directory cleanup errors
    }

    const relToSrcPages = path.relative(path.join(repoRoot, 'src/pages'), markdownDir);
    const pubDirPath = path.join(repoRoot, 'public', relToSrcPages, dirName);
    try {
      if (fs.existsSync(pubDirPath) && fs.readdirSync(pubDirPath).length === 0) {
        fs.rmdirSync(pubDirPath);
        console.log(`Removed empty directory: ${pubDirPath}`);
      }
    } catch (e) {
      // Ignore directory cleanup errors
    }
  }
}

function getContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const map = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp'
  };
  return map[ext] || 'application/octet-stream';
}

uploadImages().catch(console.error);
