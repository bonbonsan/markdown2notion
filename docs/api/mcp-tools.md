# MCP Tools Reference

This document provides detailed information about all MCP tools available in the Markdown2Notion server.

## Tool: upload_markdown

**Purpose**: Upload a Markdown file to Notion as a new page

### Parameters

- **filepath** (required): Absolute path to the Markdown file
- **parent_url** (optional): Notion page URL (recommended method)
- **database_id** (optional): Notion database ID (alternative to parent_url)
- **parent_page_id** (optional): Notion page ID (alternative to parent_url)

### Return Value

Success message containing:
- File name that was uploaded
- Page ID of the created Notion page
- Direct URL to view the page

### Example Usage

```python
# Using parent URL (recommended)
result = upload_markdown(
    filepath="/Users/john/documents/my-notes.md",
    parent_url="https://www.notion.so/16132a3709e4816cb512e4d73d345003"
)

# Using database ID
result = upload_markdown(
    filepath="/Users/john/documents/my-notes.md", 
    database_id="abc12345-1234-1234-1234-123456789abc"
)
```

### Behavior

1. **File Processing**: Reads and parses the Markdown file
2. **Title Extraction**: Uses filename (without .md extension) as page title
3. **Block Conversion**: Converts Markdown elements to Notion blocks
4. **Smart Upload**: Automatically handles files with 100+ blocks
5. **Page Creation**: Creates the Notion page with all content

### Error Handling

- **FileNotFoundError**: File doesn't exist at specified path
- **ValueError**: Invalid parent URL format or missing required parameters
- **NotionError**: Notion API errors (permissions, rate limits, etc.)

---

## Tool: upload_markdown_content

**Purpose**: Upload raw Markdown content directly to Notion

### Parameters

- **content** (required): Markdown content as a string
- **title** (required): Title for the new Notion page
- **parent_url** (optional): Notion page URL (recommended method)
- **database_id** (optional): Notion database ID (alternative to parent_url)
- **parent_page_id** (optional): Notion page ID (alternative to parent_url)

### Return Value

Success message containing:
- Page title
- Page ID of the created Notion page  
- Direct URL to view the page

### Example Usage

```python
markdown_content = """
# My Project Notes

## Overview
This is a sample project with the following features:

- Feature A
- Feature B
- Feature C

## Code Example
```python
def hello_world():
    print("Hello, World!")
```
"""

result = upload_markdown_content(
    content=markdown_content,
    title="Project Documentation",
    parent_url="https://www.notion.so/my-workspace"
)
```

### Behavior

1. **Content Processing**: Parses the provided Markdown string
2. **Title Setting**: Uses the provided title parameter
3. **Block Conversion**: Converts Markdown elements to Notion blocks
4. **Smart Upload**: Automatically handles content with 100+ blocks
5. **Page Creation**: Creates the Notion page with all content

---

## Tool: list_database_pages

**Purpose**: List pages in a Notion database (for reference and debugging)

### Parameters

- **database_id** (required): Notion database ID
- **limit** (optional): Maximum number of pages to return (default: 10, max: 100)

### Return Value

Formatted list of pages containing:
- Page titles
- Page IDs
- Total count

### Example Usage

```python
result = list_database_pages(
    database_id="abc12345-1234-1234-1234-123456789abc",
    limit=5
)
```

### Sample Output

```
Found 3 pages in database:
- Project Documentation (ID: def12345-5678-9012-3456-789012345def)
- Meeting Notes (ID: ghi12345-9012-3456-7890-123456789ghi)
- Task List (ID: jkl12345-3456-7890-1234-567890123jkl)
```

---

## Tool: get_database_info

**Purpose**: Get information about a Notion database

### Parameters

- **database_id** (required): Notion database ID

### Return Value

Database information including:
- Database title
- Database ID
- Creation date

### Example Usage

```python
result = get_database_info(
    database_id="abc12345-1234-1234-1234-123456789abc"
)
```

### Sample Output

```
Database: My Project Database
ID: abc12345-1234-1234-1234-123456789abc
Created: 2025-01-15T10:30:00.000Z
```

---

## Common Error Messages

### Authentication Errors
```
Error: NOTION_TOKEN is required. Set it as environment variable or pass as parameter.
```
**Solution**: Ensure your `.env` file contains a valid `NOTION_TOKEN`

### Permission Errors  
```
Error: The integration does not have access to perform this action.
```
**Solution**: Grant your Notion integration access to the target page/database

### Invalid URL Errors
```
Error: Invalid Notion URL format: https://invalid-url
```
**Solution**: Ensure you're using a valid Notion page URL format

### File System Errors
```
Error: File not found: /path/to/nonexistent.md
```
**Solution**: Verify the file path exists and is accessible

---

## URL Format Support

The following Notion URL formats are supported:

- `https://notion.so/Page-Title-32characterid`
- `https://notion.so/32characterid`  
- `https://workspace.notion.site/Page-Title-32characterid`

The tool automatically extracts the page ID from any of these formats.

---

## Block Limit Handling

Notion's API has a limit of 100 blocks per page creation request. Markdown2Notion handles this automatically:

1. **≤ 100 blocks**: Single API call creates the complete page
2. **> 100 blocks**: 
   - First 100 blocks create the initial page
   - Remaining blocks are appended in chunks of 100
   - Result is a single, complete Notion page

This process is transparent to the user - you just get a fully populated page regardless of file size.