#!/usr/bin/env python
"""
Temporary script to upload the Kindle Markdown file to Notion
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from notion_uploader import NotionUploader

def main():
    # Initialize uploader
    uploader = NotionUploader()

    # File and parent URL
    filepath = '/Users/kentookubo/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault/Kindle/50 Trades in 50 Weeks.md'
    parent_url = 'https://www.notion.so/16132a3709e4816cb512e4d73d345003'

    print(f"Uploading: {filepath}")
    print(f"Parent URL: {parent_url}")

    try:
        # Upload the file
        page_id = uploader.upload_markdown_file(
            filepath=filepath,
            parent_url=parent_url
        )

        print(f"\n✅ Successfully uploaded!")
        print(f"Page ID: {page_id}")
        print(f"View at: https://www.notion.so/{page_id.replace('-', '')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
