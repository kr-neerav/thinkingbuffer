#!/bin/bash

# Source directory containing the books and chapters
SOURCE_DIR="/Users/neerav/Documents/Projects/mythology-texts/mythology podcast/ramayana"

# Destination directory in your Astro project
DEST_DIR="src/pages/comics/ramayana"

BOOK_NUM=$1
CHAP_NUM=$2

if [ -z "$BOOK_NUM" ] || [ -z "$CHAP_NUM" ]; then
    echo "Usage: ./move_comics.sh <book_number> <chapter_number>"
    echo "Example: ./move_comics.sh 1 2"
    exit 1
fi

echo "Scanning for images in Book $BOOK_NUM, Chapter $CHAP_NUM in $SOURCE_DIR..."

# Find all 'annotated' directories that match the book and chapter numbers
find "$SOURCE_DIR" -type d -name "annotated" | grep -iE "book_0?${BOOK_NUM}.*chapter_0?${CHAP_NUM}/annotated$" | while read -r src_annotated; do
    # Get the relative path from the source directory (e.g. Book_01.../Chapter_2.../annotated)
    rel_path="${src_annotated#$SOURCE_DIR/}"
    dest_annotated="$DEST_DIR/$rel_path"

    # Find images in the source annotated folder
    find "$src_annotated" -maxdepth 1 -type f \( -iname "*.jpeg" -o -iname "*.jpg" -o -iname "*.png" -o -iname "*.webp" \) | while read -r img; do
        # Create destination directory if it doesn't exist yet
        mkdir -p "$dest_annotated"
        
        # Move the image
        mv "$img" "$dest_annotated/"
        echo "Moved $(basename "$img") to $dest_annotated/"
    done
done

echo "Finished moving new comics."
