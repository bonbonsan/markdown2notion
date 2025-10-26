# Markdown2Notion# Markdown2Notion MCP Server



A Model Context Protocol (MCP) server for uploading Markdown files to Notion. This tool allows you to easily convert Markdown documents into Notion pages while preserving formatting and structure.MarkdownファイルをNotionページとして効率的にアップロードするためのMCPサーバーです。



## 🚀 Features## 機能



- ✅ **Convert Markdown files to Notion pages** - Seamlessly transform your .md files- MarkdownファイルをNotionページとして作成

- ✅ **Automatic large file handling** - Files with 100+ blocks are automatically split- **ファイル名をページタイトルとして使用**（拡張子は自動除去）

- ✅ **URL-based page targeting** - Simply provide a Notion page URL as parent- データベースまたは親ページへの追加に対応

- ✅ **Support for common Markdown elements** - Headers, lists, code blocks, links, etc.- H1-H6見出し、リスト、コードブロック、通常テキストをサポート

- ✅ **Database and page support** - Upload to databases or as child pages

- ✅ **Built on FastMCP framework** - Easy integration with MCP clients## セットアップ



## 📦 Installation### 1. 依存関係のインストール



1. **Clone the repository:**```bash

```bashpip install -e .

git clone <repository-url>```

cd markdown2notion

```### 2. 環境変数の設定



2. **Install dependencies:**`.env`ファイルを作成し、Notion APIトークンを設定：

```bash

pip install -r requirements.txt```

# or using pyproject.tomlNOTION_TOKEN=your_notion_api_token_here

pip install -e .```

```

### 3. CLINEでの使用

3. **Set up your Notion API token:**

```bash`cline_mcp_settings.json`に以下の設定を追加：

# Create .env file

echo "NOTION_TOKEN=your_notion_api_token_here" > .env```json

```{

  "mcpServers": {

**To get your Notion API token:**    "markdown2notion": {

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)      "command": "python",

2. Create a new integration      "args": ["/path/to/markdown2notion/src/server.py"],

3. Copy the Internal Integration Token      "env": {

4. **Important:** Give the integration access to your target pages/databases        "NOTION_TOKEN": "your_notion_api_token_here"

      }

## 🔧 Usage    }

  }

### As MCP Server (Recommended)}

```

Configure in your MCP client settings (like Claude Desktop's `cline_mcp_settings.json`):

## 使用方法

```json

{### upload_markdown

  "mcpServers": {

    "markdown2notion": {Markdownファイルをアップロード：

      "command": "python",

      "args": ["/path/to/markdown2notion/src/server.py"]```

    }upload_markdown(filepath="/path/to/file.md", database_id="your_database_id")

  }```

}

```パラメータ:

- `filepath`: アップロードするMarkdownファイルのパス

**Note:** The server automatically loads the `NOTION_TOKEN` from your `.env` file.- `database_id`: 追加先のNotionデータベースID（オプション）

- `parent_page_id`: 親ページID（database_idが未指定の場合）

### Direct Usage

## ライセンス

You can also use the components directly:

MIT License
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

### Upload a file using URL (easiest):
```
upload_markdown(
    filepath="/path/to/document.md", 
    parent_url="https://www.notion.so/16132a3709e4816cb512e4d73d345003"
)
```

### Upload a file to a database:
```
upload_markdown("/path/to/document.md", database_id="abc123...")
```

### Upload content directly:
```
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

```
markdown2notion/
├── src/
│   ├── server.py           # MCP server implementation
│   ├── notion_uploader.py  # Core Notion API client
│   ├── markdown_processor.py # Markdown to Notion blocks converter
│   └── __init__.py
├── docs/
│   ├── design.md          # Architecture documentation
│   └── api/               # Detailed API docs
├── examples/
│   └── sample-document.md # Example Markdown file
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