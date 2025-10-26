# Markdown2Notion

MarkdownファイルをNotionページに効率的にアップロードするためのModel Context Protocol (MCP)サーバーです。フォーマットと構造を保持しながら、Markdownドキュメントを簡単にNotionページに変換できます。

## 🚀 機能

- ✅ **MarkdownファイルをNotionページに変換** - .mdファイルをシームレスに変換
- ✅ **大容量ファイルの自動処理** - 100ブロック以上のファイルを自動分割
- ✅ **URLベースのページ指定** - NotionページURLを直接指定可能
- ✅ **一般的なMarkdown要素のサポート** - 見出し、リスト、コードブロック、リンクなど
- ✅ **データベースとページの両方に対応** - データベースまたは子ページとしてアップロード
- ✅ **FastMCPフレームワーク採用** - MCPクライアントとの簡単な統合

## 📦 インストール

1. **リポジトリのクローン:**
```bash
git clone <repository-url>
cd markdown2notion
```

2. **依存関係のインストール:**
```bash
pip install -r requirements.txt
# または pyproject.toml を使用
pip install -e .
```

3. **Notion APIトークンの設定:**
```bash
# .env ファイルを作成
echo "NOTION_TOKEN=your_notion_api_token_here" > .env
```

**Notion APIトークンの取得方法:**
1. [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations) にアクセス
2. 新しいインテグレーションを作成
3. Internal Integration Token をコピー
4. **重要:** 対象ページ/データベースにインテグレーションのアクセス権限を付与

## 🔧 使用方法

### MCPサーバーとしての使用（推奨）

MCPクライアント設定（Claude Desktopの`cline_mcp_settings.json`など）で設定:

```json
{
  "mcpServers": {
    "markdown2notion": {
      "command": "python",
      "args": ["/path/to/markdown2notion/src/server.py"]
    }
  }
}
```

**注意:** サーバーは自動的に`.env`ファイルから`NOTION_TOKEN`を読み込みます。

### 直接使用

コンポーネントを直接使用することも可能です:

```python
from src.notion_uploader import NotionUploader

uploader = NotionUploader()

# URL使用（推奨）
page_id = uploader.upload_markdown_file(
    filepath="path/to/your/document.md",
    parent_url="https://www.notion.so/your-page-url-here"
)

# ページID直接指定
page_id = uploader.upload_markdown_file(
    filepath="path/to/your/document.md",
    parent_page_id="16132a37-09e4-816c-b512-e4d73d345003"
)
```

## 🛠 利用可能なMCPツール

MCPサーバーとして使用する際に利用できるツール:

### `upload_markdown`
MarkdownファイルをNotionにアップロード:
- `filepath`: .mdファイルのパス（必須）
- `parent_url`: NotionページURL（例：`https://notion.so/page-title-abc123...`）
- `database_id`: 対象データベースID（parent_urlの代替）
- `parent_page_id`: 親ページID（parent_urlの代替）

### `upload_markdown_content`
Markdownコンテンツを直接アップロード:
- `content`: Markdownコンテンツ（文字列）（必須）
- `title`: ページタイトル（必須）
- `parent_url`: NotionページURL（推奨）
- `database_id`または`parent_page_id`: 代替の対象指定

### `list_database_pages`
データベース内のページ一覧を表示（参考用）

### `get_database_info`
特定のデータベースの情報を取得

## 📖 使用例

### URLを使用したファイルアップロード（最も簡単）:
```
upload_markdown(
    filepath="/path/to/document.md", 
    parent_url="https://www.notion.so/16132a3709e4816cb512e4d73d345003"
)
```

### データベースにファイルをアップロード:
```
upload_markdown("/path/to/document.md", database_id="abc123...")
```

### コンテンツを直接アップロード:
```
upload_markdown_content(
    content="# My Title\nSome content", 
    title="My Page", 
    parent_url="https://notion.so/parent-page"
)
```

## 📝 サポートされるMarkdown要素

- **見出し** (H1-H6) → Notionヘッディングブロック
- **段落** → Notion段落ブロック
- **リスト**（箇条書き・番号付き）→ Notionリストブロック
- **コードブロック** → Notionコードブロック
- **インラインコード** → Notionインラインコード
- **太字・斜体テキスト** → Notionリッチテキスト書式
- **リンク** → Notionリンク

## 🔄 大容量ファイルの処理

100ブロックを超えるファイルは自動的に処理されます:
1. 最初の100ブロックで初期ページを作成
2. 残りのブロックは自動的に100ブロックずつ追加
3. 結果：すべてのコンテンツを含む単一の完全なNotionページ

## 📋 必要な環境

- Python 3.8以上
- notion-client
- fastmcp
- python-dotenv
- mistune（Markdown解析用）

## 🗂 プロジェクト構造

```
markdown2notion/
├── src/
│   ├── server.py           # MCP サーバー実装
│   ├── notion_uploader.py  # コア Notion API クライアント
│   ├── markdown_processor.py # Markdown → Notion ブロック変換
│   └── __init__.py
├── docs/
│   ├── design.md          # アーキテクチャドキュメント
│   └── api/               # 詳細APIドキュメント
├── tests/                 # テストスイート
├── .env.example          # 環境変数テンプレート
├── pyproject.toml        # プロジェクト設定
└── README.md            # このファイル
```

## 🧪 開発・テスト

### 開発環境のセットアップ
```bash
# 開発用依存関係のインストール
pip install -e ".[dev]"

# リンターとフォーマッター実行
ruff check src tests
black src tests

# 型チェック
mypy src

# テスト実行
pytest tests/ --cov=src
```

### コード品質ツール
- **Ruff**: 高速Python リンター
- **Black**: コードフォーマッター
- **MyPy**: 静的型チェック
- **Pytest**: テストフレームワーク

## 🤝 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 変更を実装
4. 適用可能な場合はテストを追加
5. プルリクエストを送信

## 📄 ライセンス

MIT License - 詳細はLICENSEファイルを参照