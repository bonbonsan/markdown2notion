# Code Reference Guide

This document provides detailed explanations of the main classes, functions, and processing flows in Markdown2Notion.

## Core Classes

### NotionUploader Class

**File**: `src/notion_uploader.py`

**Purpose**: Handles all interactions with the Notion API, including authentication, page creation, and block management.

#### Constructor

```python
def __init__(self, token: Optional[str] = None):
```

**Parameters**:
- `token` (optional): Notion API token. If not provided, loads from `NOTION_TOKEN` environment variable

**Behavior**:
- Loads environment variables from `.env` file using `python-dotenv`
- Initializes Notion client with authentication
- Creates `MarkdownProcessor` instance for content conversion
- Raises `ValueError` if no token is available

#### Key Methods

##### upload_markdown_file()

```python
def upload_markdown_file(
    self, 
    filepath: str, 
    database_id: Optional[str] = None, 
    parent_page_id: Optional[str] = None
) -> str:
```

**Purpose**: Upload a Markdown file to Notion as a new page

**Process Flow**:
1. Validates that either `database_id` or `parent_page_id` is provided
2. Uses `MarkdownProcessor` to convert file to Notion blocks
3. Calls `_create_page_with_blocks()` to handle page creation with automatic block splitting
4. Returns the created page ID

##### _create_page_with_blocks() (New)

```python
def _create_page_with_blocks(
    self,
    blocks: List[Dict[str, Any]],
    title: str,
    database_id: Optional[str] = None,
    parent_page_id: Optional[str] = None
) -> str:
```

**Purpose**: Smart page creation that automatically handles Notion's 100-block limitation

**Algorithm**:
```python
if len(blocks) <= 100:
    # Simple case: create page with all blocks
    page = client.pages.create(parent=parent, properties=properties, children=blocks)
else:
    # Complex case: split into chunks
    initial_blocks = blocks[:100]
    page = client.pages.create(parent=parent, properties=properties, children=initial_blocks)
    
    # Append remaining blocks in chunks of 100
    remaining_blocks = blocks[100:]
    for i in range(0, len(remaining_blocks), 100):
        chunk = remaining_blocks[i:i+100]
        client.blocks.children.append(block_id=page_id, children=chunk)
```

##### extract_page_id_from_url() (New Static Method)

```python
@staticmethod
def extract_page_id_from_url(url: str) -> str:
```

**Purpose**: Convert Notion URLs to properly formatted page IDs

**Supported URL Formats**:
- `https://notion.so/page-title-32chars`
- `https://notion.so/32chars`
- `https://workspace.notion.site/page-title-32chars`

**Algorithm**:
1. Remove query parameters and fragments from URL
2. Apply regex patterns to extract 32-character ID
3. Format ID with hyphens: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
4. Raise `ValueError` if URL format is invalid

---

### MarkdownProcessor Class

**File**: `src/markdown_processor.py`

**Purpose**: Converts Markdown content to Notion block format using the Mistune parser.

#### Key Methods

##### process_file()

```python
def process_file(self, filepath: str) -> Tuple[List[Dict[str, Any]], str]:
```

**Purpose**: Process a Markdown file and return Notion blocks + title

**Process Flow**:
1. Read file content with UTF-8 encoding
2. Extract title from filename (remove .md extension)
3. Call `parse_markdown_to_blocks()` to convert content
4. Return tuple of (blocks_list, title_string)

##### parse_markdown_to_blocks()

```python
def parse_markdown_to_blocks(self, content: str, title: str) -> Tuple[List[Dict[str, Any]], str]:
```

**Purpose**: Convert Markdown string to Notion block objects

**Conversion Map**:
- `# Header` → `{"type": "heading_1", "heading_1": {...}}`
- `## Subheader` → `{"type": "heading_2", "heading_2": {...}}`
- `Normal text` → `{"type": "paragraph", "paragraph": {...}}`
- `- List item` → `{"type": "bulleted_list_item", "bulleted_list_item": {...}}`
- `` `code` `` → Inline code within rich text
- ` ```code block``` ` → `{"type": "code", "code": {...}}`

**Rich Text Processing**:
Each text element supports:
- **Bold**: `{"bold": true}`
- **Italic**: `{"italic": true}`
- **Code**: `{"code": true}`
- **Links**: `{"link": {"url": "..."}}`

---

## MCP Server Functions

### Tool Registration

**File**: `src/server.py`

All MCP tools are registered using the `@mcp.tool()` decorator from FastMCP:

```python
@mcp.tool()
def upload_markdown(filepath: str, parent_url: Optional[str] = None, ...) -> str:
```

### Key Server Functions

##### upload_markdown() - Main Tool

**Process Flow**:
1. **URL Processing**: If `parent_url` provided, extract page ID using `extract_page_id_from_url()`
2. **Validation**: Ensure at least one target (URL, database_id, or parent_page_id) is specified
3. **Upload**: Call `NotionUploader.upload_markdown_file()` 
4. **Response Formatting**: Create user-friendly success message with page URL
5. **Error Handling**: Catch and format specific error types

##### Error Handling Strategy

```python
try:
    # Core upload logic
    page_id = uploader.upload_markdown_file(...)
    return f"Success message with page_id: {page_id}"
    
except FileNotFoundError:
    return f"Error: File not found: {filepath}"
except ValueError as e:
    return f"Error: {str(e)}"  # URL format, missing params, etc.
except Exception as e:
    return f"Error uploading markdown: {str(e)}"  # Notion API errors
```

---

## Processing Flow Diagrams

### File Upload Flow

```
1. MCP Client Request
   ↓
2. server.py: upload_markdown()
   ├─ Extract page ID from URL (if provided)
   ├─ Validate parameters  
   └─ Call NotionUploader.upload_markdown_file()
      ↓
3. notion_uploader.py: upload_markdown_file()
   ├─ Call MarkdownProcessor.process_file()
   └─ Call _create_page_with_blocks()
      ↓
4. markdown_processor.py: process_file()
   ├─ Read file content
   ├─ Extract title from filename
   └─ Call parse_markdown_to_blocks()
      ├─ Parse with Mistune
      ├─ Convert to Notion blocks
      └─ Return blocks list
         ↓
5. notion_uploader.py: _create_page_with_blocks()
   ├─ Check block count
   ├─ If ≤100: Single page creation
   ├─ If >100: Initial page + chunked appends
   └─ Return page ID
      ↓
6. server.py: Format success response
   └─ Return page URL to MCP client
```

### Block Splitting Flow (for large files)

```
Large Markdown File (114+ blocks)
         ↓
1. Create initial page with first 100 blocks
   POST /v1/pages
   {
     "parent": {...},
     "properties": {...},
     "children": blocks[0:100]
   }
         ↓
2. Get page_id from response
         ↓
3. Append remaining blocks in chunks
   For each chunk of 100 blocks:
   POST /v1/blocks/{page_id}/children
   {
     "children": blocks[100:200], then blocks[200:300], etc.
   }
         ↓
4. Result: Single complete Notion page
```

---

## Error Handling Patterns

### File System Errors

```python
# In NotionUploader.upload_markdown_file()
try:
    blocks, title = self.processor.process_file(filepath)
except FileNotFoundError:
    # File doesn't exist - let this propagate to server.py
    raise
except UnicodeDecodeError:
    # File encoding issue
    raise ValueError(f"Cannot read file {filepath}: encoding error")
```

### Notion API Errors

```python
# In NotionUploader._create_page_with_blocks()
try:
    page = self.client.pages.create(...)
except NotionClientError as e:
    if "unauthorized" in str(e).lower():
        raise ValueError("Notion integration lacks permission to target page/database")
    elif "rate_limited" in str(e).lower():
        raise ValueError("Notion API rate limit exceeded, please try again later")
    else:
        # Generic API error
        raise
```

### URL Format Errors

```python
# In NotionUploader.extract_page_id_from_url()
patterns = [
    r'notion\.so/[^/]*?([a-f0-9]{32})/?$',
    r'notion\.so/([a-f0-9]{32})/?$',
    r'notion\.site/[^/]*?([a-f0-9]{32})/?$',
]

for pattern in patterns:
    match = re.search(pattern, url, re.IGNORECASE)
    if match:
        return format_page_id(match.group(1))

raise ValueError(f"Invalid Notion URL format: {url}")
```

---

## Performance Optimizations

### Memory Management

- **Streaming**: Files are read once and processed in memory
- **Chunking**: Large block lists are processed in 100-block chunks
- **Lazy Loading**: Notion client is created only when needed

### API Efficiency

- **Batch Operations**: Multiple blocks sent per API call (up to 100)
- **Minimal Calls**: Efficiently pack blocks to minimize API requests
- **Error Recovery**: Graceful handling of rate limits and temporary failures

### Concurrent Safety

- **Stateless Design**: No shared state between requests
- **Thread Safe**: Each request gets its own NotionUploader instance
- **Resource Management**: Proper cleanup of file handles and network connections

This comprehensive reference should help developers understand the codebase structure and extend functionality as needed.