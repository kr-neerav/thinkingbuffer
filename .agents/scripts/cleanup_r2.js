import fs from 'fs';
import path from 'path';
import { S3Client, ListObjectsV2Command, DeleteObjectsCommand } from '@aws-sdk/client-s3';
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
const doDelete = args.includes('--delete') || args.includes('-d');
const markdownArg = args.find(arg => !arg.startsWith('-'));

if (!markdownArg) {
  console.error('Usage: node cleanup_r2.js <path-to-markdown-file> [--delete]');
  process.exit(1);
}

const markdownFilePath = path.resolve(markdownArg);
if (!fs.existsSync(markdownFilePath)) {
  console.error(`File not found: ${markdownFilePath}`);
  process.exit(1);
}

const repoRoot = process.cwd();
const markdownDir = path.dirname(markdownFilePath);
const relChapterDir = path.relative(repoRoot, markdownDir).split(path.sep).join('/');

// Target bucket & URL
let targetBucket = R2_BUCKET_NAME;
let targetPublicUrl = R2_PUBLIC_URL;
if (relChapterDir.includes('src/pages/comics/')) {
  targetBucket = COMICS_R2_BUCKET_NAME || R2_BUCKET_NAME;
  targetPublicUrl = COMICS_R2_PUBLIC_URL || R2_PUBLIC_URL;
}

async function cleanup() {
  const content = fs.readFileSync(markdownFilePath, 'utf-8');
  
  // Find all active R2 image URLs referenced in the markdown
  const activeKeys = new Set();
  const cleanPublicUrl = (targetPublicUrl || '').replace(/\/$/, '');
  const urlRegex = new RegExp(`${cleanPublicUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/([^)\\s"]+)`, 'g');
  let match;
  while ((match = urlRegex.exec(content)) !== null) {
    activeKeys.add(match[1]);
  }

  // Prefix for listing
  const prefix = `${relChapterDir}/`;
  console.log(`Checking bucket "${targetBucket}" with prefix: "${prefix}"`);
  console.log(`Active R2 keys referenced in markdown: ${activeKeys.size}`);

  const listCommand = new ListObjectsV2Command({
    Bucket: targetBucket,
    Prefix: prefix,
  });

  const listResponse = await s3Client.send(listCommand);
  const objects = listResponse.Contents || [];

  if (objects.length === 0) {
    console.log('No objects found on R2 under prefix:', prefix);
    return;
  }

  const obsoleteObjects = objects.filter(obj => !activeKeys.has(obj.Key));

  console.log(`Found ${objects.length} total object(s) on R2 under prefix.`);
  console.log(`Active object(s): ${objects.length - obsoleteObjects.length}`);
  console.log(`Obsolete / orphaned object(s): ${obsoleteObjects.length}`);

  if (obsoleteObjects.length === 0) {
    console.log('No obsolete images to delete. R2 is clean!');
    return;
  }

  console.log('\nObsolete objects identified for removal:');
  obsoleteObjects.forEach(obj => console.log(` - ${obj.Key}`));

  if (!doDelete) {
    console.log('\n[DRY RUN] To delete these objects, re-run with the --delete flag:');
    console.log(`node .agents/scripts/cleanup_r2.js ${path.relative(repoRoot, markdownFilePath)} --delete`);
    return;
  }

  console.log('\nDeleting obsolete objects from R2...');
  const deleteCommand = new DeleteObjectsCommand({
    Bucket: targetBucket,
    Delete: {
      Objects: obsoleteObjects.map(obj => ({ Key: obj.Key })),
    },
  });

  await s3Client.send(deleteCommand);
  console.log(`Successfully deleted ${obsoleteObjects.length} obsolete object(s) from R2!`);
}

cleanup().catch(console.error);
