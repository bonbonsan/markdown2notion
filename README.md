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
git clone https://github.com/bonbonsan/markdown2notion.git
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

#### Cline (VS Code Extension)

1. **Set up virtual environment and install dependencies:**

   ```bash
   cd markdown2notion
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Open the Command Palette → `Cline: Open MCP Settings`.
3. Add or update `cline_mcp_settings.json` with:

   ```json
   {
     "mcpServers": {
       "markdown2notion": {
         "command": "/absolute/path/to/markdown2notion/.venv/bin/python",
         "args": ["/absolute/path/to/markdown2notion/src/server.py"]
       }
     }
   }
   ```

   **⚠️ Important Notes:**
   - Use **absolute paths** for both `command` and `args`
   - Point `command` to the virtual environment's Python interpreter
   - Replace `/absolute/path/to/markdown2notion` with your actual project path
   - Example for macOS/Linux: `/Users/username/Documents/markdown2notion/.venv/bin/python`
   - Example for Windows: `C:\Users\username\Documents\markdown2notion\.venv\Scripts\python.exe`

4. **Restart VS Code** (not just Cline) after saving the configuration file.

#### Claude Code (VS Code Extension)

1. **Set up virtual environment and install dependencies:**

   ```bash
   cd markdown2notion
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create workspace settings** in your project:
   Create `.vscode/settings.json` in your project root with:

   ```json
   {
     "claude.mcpServers": {
       "markdown2notion": {
         "command": "/absolute/path/to/markdown2notion/.venv/bin/python",
         "args": ["/absolute/path/to/markdown2notion/src/server.py"],
         "enabled": true
       }
     }
   }
   ```

   **⚠️ Important Notes:**
   - Use **absolute paths** for both `command` and `args`
   - Point `command` to the virtual environment's Python interpreter
   - Replace `/absolute/path/to/markdown2notion` with your actual project path
   - Example for macOS/Linux: `/Users/username/Documents/markdown2notion/.venv/bin/python`
   - Example for Windows: `C:\Users\username\Documents\markdown2notion\.venv\Scripts\python.exe`

#### Claude Desktop (Standalone App)

1. **Set up virtual environment and install dependencies:**

   ```bash
   cd markdown2notion
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. In Claude Desktop, click **Claude → Settings → Developer → Open configuration file**.
3. Add the following entry to `claude_desktop_config.json` (macOS) or the equivalent config file on your platform:

   ```json
   {
     "mcpServers": {
       "markdown2notion": {
         "command": "/absolute/path/to/markdown2notion/.venv/bin/python",
         "args": ["/absolute/path/to/markdown2notion/src/server.py"],
         "enabled": true
       }
     }
   }
   ```

   **⚠️ Important Notes:**
   - Use **absolute paths** for both `command` and `args`
   - Point `command` to the virtual environment's Python interpreter
   - Replace `/absolute/path/to/markdown2notion` with your actual project path
   - Example for macOS/Linux: `/Users/username/Documents/markdown2notion/.venv/bin/python`
   - Example for Windows: `C:\Users\username\Documents\markdown2notion\.venv\Scripts\python.exe`

4. **Restart Claude Desktop** after saving the configuration file.

**Note:** When the server runs from this repository it reads the `NOTION_TOKEN` from your local `.env` file. Make sure you have created the `.env` file with your Notion API token as described in the Installation section.

## 🔍 Troubleshooting

### MCPサーバー接続の問題

もしCLINEやClaude Desktopで「MCPサーバーが接続されていない」というエラーが表示される場合：

1. **仮想環境のPythonパスを確認**: 設定ファイルで絶対パスを使用していることを確認
2. **依存関係のインストール**: `pip install -r requirements.txt`が仮想環境内で実行されていることを確認
3. **アプリケーションの再起動**: VS Code（CLINE使用時）またはClaude Desktopを完全に再起動
4. **パスの確認**: 設定ファイル内のパスが実際のファイル場所と一致することを確認

### Pythonスクリプトを直接実行

MCPサーバーが動作しない場合の回避策として、Pythonスクリプトを直接実行できます：

```bash
# 仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# スクリプトを実行
python -c "
from src.notion_uploader import NotionUploader
uploader = NotionUploader()
page_id = uploader.upload_markdown_file(
    filepath='/path/to/your/file.md',
    parent_url='https://www.notion.so/your-parent-page-url'
)
print(f'Uploaded! Page ID: {page_id}')
"
```

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

## 💬 プロンプト実行例

MCPサーバーが正常に設定されていれば、以下のようなプロンプトでMarkdownファイルをNotionにアップロードできます。

### CLINE（VS Code拡張）での使用例

```text
このMarkdownファイルをNotionにアップロードしてください:
/Users/username/Documents/my-notes.md

親ページURLはこちらです:
https://www.notion.so/16132a3709e4816cb512e4d73d345003
```

CLINEが自動的に`upload_markdown`ツールを呼び出し、以下のような結果が表示されます：

```text
Successfully uploaded 'my-notes.md' to Notion.
Page ID: 29932a37-09e4-819d-a790-e8c025f28af5
View at: https://www.notion.so/29932a3709e4819da790e8c025f28af5
```

### Claude Code（Claude Desktop）での使用例

```text
以下のMarkdownコンテンツを「週報 2024年10月」というタイトルでNotionページに変換してください：

# 今週の進捗
- プロジェクトAの設計完了
- バグ修正3件対応

## 来週の予定
- 実装開始
- コードレビュー

親ページ: https://www.notion.so/work-reports-abc123def456
```

Claude Codeが`upload_markdown_content`ツールを使用し、以下のような応答をします：

```text
Successfully uploaded content as '週報 2024年10月' to Notion.
Page ID: 12345678-90ab-cdef-1234-567890abcdef
View at: https://www.notion.so/12345678090abcdef1234567890abcdef
```

### データベース指定での使用例

```text
この研究ノートをNotionのデータベースにアップロードしてください：
- ファイル: /Users/username/research/ml-paper-summary.md
- データベースID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
- タイトルはファイル名を使用
```

### 複数ファイルの一括アップロード例

```text
以下のMarkdownファイルをすべて同じ親ページにアップロードしてください：
1. /path/to/chapter1.md
2. /path/to/chapter2.md  
3. /path/to/chapter3.md

親ページ: https://www.notion.so/book-draft-xyz789
```

**注意**: MCPサーバーが接続されていない場合、CLINEは自動的にPythonスクリプトの直接実行にフォールバックします。

## 📖 Examples

Upload Markdown content directly:

- `content`: Your markdown content as text (required)
- `title`: Page title (required)
- `parent_url`: Notion page URL (recommended)
- `database_id` or `parent_page_id`: Alternative target specification

**注意**: MCPサーバーが接続されていない場合、CLINEは自動的にPythonスクリプトの直接実行にフォールバックします。

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
