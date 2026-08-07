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

  // Regex to match markdown images: ![alt](url)
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  let updatedContent = content;
  
  // Find all matches first
  const matches = [...content.matchAll(imageRegex)];

  for (const match of matches) {
    const fullMatch = match[0];
    const altText = match[1];
    const imagePath = match[2];

    // Skip if the image is already a remote URL
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      continue;
    }

    const absoluteImagePath = path.resolve(markdownDir, imagePath);

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

    if (s3Key.includes('src/pages/comics/')) {
      targetBucket = COMICS_R2_BUCKET_NAME || R2_BUCKET_NAME; // Fallback to default if missing
      targetPublicUrl = COMICS_R2_PUBLIC_URL || R2_PUBLIC_URL;
    }

    if (!targetBucket || !targetPublicUrl) {
      console.error(`Missing bucket or public URL configuration in .env for ${s3Key}`);
      continue;
    }

    console.log(`Uploading ${s3Key} to bucket ${targetBucket}...`);

    const fileStream = fs.createReadStream(absoluteImagePath);
    const contentType = getContentType(absoluteImagePath);

    const uploadParams = {
      Bucket: targetBucket,
      Key: s3Key,
      Body: fileStream,
      ContentType: contentType,
    };

    try {
      await s3Client.send(new PutObjectCommand(uploadParams));
      
      // Remove trailing slash from public URL if it exists
      const cleanPublicUrl = targetPublicUrl.replace(/\/$/, '');
      const newImageUrl = `${cleanPublicUrl}/${s3Key}`;
      
      console.log(`Successfully uploaded. New URL: ${newImageUrl}`);
      
      // Update the markdown content
      const newMatchStr = `![${altText}](${newImageUrl})`;
      updatedContent = updatedContent.replace(fullMatch, newMatchStr);
      
      // Cleanup local file
      console.log(`Deleting local file: ${absoluteImagePath}`);
      fs.unlinkSync(absoluteImagePath);
      
    } catch (error) {
      console.error(`Failed to upload ${s3Key}:`, error);
    }
  }

  if (content !== updatedContent) {
    fs.writeFileSync(markdownFilePath, updatedContent, 'utf-8');
    console.log(`Updated markdown file: ${markdownFilePath}`);
  } else {
    console.log('No local images found or updated.');
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
