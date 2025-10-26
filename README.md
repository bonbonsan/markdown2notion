# Markdown2Notion

A Model Context Protocol (MCP) server for uploading Markdown files to Notion. This tool allows you to easily convert Markdown documents into Notion pages while preserving formatting and structure.

## 🚀 Features

- ✅ **Convert Markdown files to Notion pages** - Seamlessly transform your .md files
- ✅ **Automatic large file handling** - Files with 100+ blocks are automatically split
- ✅ **URL-based page targeting** - Simply provide a Notion page URL as parent
- ✅ **Support for common Markdown elements** - Headers, lists, code blocks, links, etc.
- ✅ **Database and page support** - Upload to databases or as child pages
- ✅ **Built on FastMCP framework** - Easy integration with MCP clients

## 📦 Installation


1. **Clone the repository:**

```bash
git clone <repository-url>
cd markdown2notion
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
# or using pyproject.toml
pip install -e .
```

3. **Set up your Notion API token:**

```bash
# Create .env file
echo "NOTION_TOKEN=your_notion_api_token_here" > .env
```

**To get your Notion API token:**

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the Internal Integration Token
4. **Important:** Give the integration access to your target pages/databases

## 🔧 Usage

### As MCP Server (Recommended)

Configure in your MCP client settings (like Claude Desktop's `cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "markdown2notion": {
      "command": "python",
      "args": ["/path/to/markdown2notion/src/server.py"],
      "env": {
        "NOTION_TOKEN": "your_notion_api_token_here"
      }
    }
  }
}
```

**Note:** The server automatically loads the `NOTION_TOKEN` from your `.env` file.

### Direct Usage

You can also use the components directly:
```python
from src.notion_uploader import NotionUploader

uploader = NotionUploader()

# Using URL (recommended)
page_id = uploader.upload_markdown_file(
    filepath="path/to/your/document.md",
    parent_url="https://www.notion.so/your-page-url-here"
)

# Using page ID directly
page_id = uploader.upload_markdown_file(
    filepath="path/to/your/document.md",
    parent_page_id="16132a37-09e4-816c-b512-e4d73d345003"
)
```

## 🛠 Available MCP Tools

When used as an MCP server, the following tools are available:

### `upload_markdown`

Upload a Markdown file to Notion:

- `filepath`: Path to your .md file (required)
- `parent_url`: Notion page URL (e.g., `https://notion.so/page-title-abc123...`)
- `database_id`: Target database ID (alternative to parent_url)
- `parent_page_id`: Parent page ID (alternative to parent_url)

### `upload_markdown_content`

Upload Markdown content directly:

- `content`: Your markdown content as text (required)
- `title`: Page title (required)
- `parent_url`: Notion page URL (recommended)
- `database_id` or `parent_page_id`: Alternative target specification

### `list_database_pages`

List existing pages in a database for reference.

### `get_database_info`

Get information about a specific database.

## 📖 Examples

### Upload a file using URL (easiest)

```bash
upload_markdown(
    filepath="/path/to/document.md", 
    parent_url="https://www.notion.so/16132a3709e4816cb512e4d73d345003"
)
```

### Upload a file to a database

```bash
upload_markdown("/path/to/document.md", database_id="abc123...")
```

### Upload content directly

```bash
upload_markdown_content(
    content="# My Title\nSome content", 
    title="My Page", 
    parent_url="https://notion.so/parent-page"
)
```

## 📝 Supported Markdown Elements

- **Headers** (H1-H6) → Notion heading blocks
- **Paragraphs** → Notion paragraph blocks
- **Lists** (bulleted and numbered) → Notion list blocks
- **Code blocks** → Notion code blocks
- **Inline code** → Notion inline code
- **Bold and italic text** → Notion rich text formatting
- **Links** → Notion links

## 🔄 Large File Handling

Files with more than 100 blocks are automatically handled:

1. First 100 blocks create the initial page
2. Remaining blocks are automatically appended in chunks
3. Result: Single complete Notion page with all content

## 📋 Requirements

- Python 3.8+
- notion-client
- fastmcp
- python-dotenv
- mistune (for Markdown parsing)

## 🗂 Project Structure

```bash
markdown2notion/
├── src/
│   ├── server.py           # MCP server implementation
│   ├── notion_uploader.py  # Core Notion API client
│   ├── markdown_processor.py # Markdown to Notion blocks converter
│   └── __init__.py
├── docs/
│   ├── design.md          # Architecture documentation
│   └── api/               # Detailed API docs
├── tests/
│   ├── test_notion_uploader.py
│   ├── test_markdown_processor.py
│   └── test_server.py
├── .env.example          # Environment template
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
