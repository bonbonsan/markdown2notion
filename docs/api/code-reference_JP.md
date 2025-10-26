# コードリファレンス（日本語版）

この文書では、markdown2notionライブラリのコードベースの詳細な技術リファレンスを提供します。

## プロジェクト構造

```
src/
├── __init__.py              # パッケージ初期化
├── markdown_processor.py   # Markdown解析とNotion変換
├── notion_uploader.py      # Notion API統合
└── server.py               # MCP サーバー実装
```

## コアクラス

### MarkdownProcessor

Markdownコンテンツを解析し、Notionブロック形式に変換します。

#### クラス定義

```python
class MarkdownProcessor:
    """Markdownコンテンツの処理とNotion形式への変換を担当"""
    
    def __init__(self):
        """Mistune Markdown パーサーを初期化"""
        
    def convert_to_notion_blocks(self, markdown_content: str) -> List[Dict[str, Any]]:
        """MarkdownをNotionブロックの配列に変換"""
```

#### メソッド詳細

##### `convert_to_notion_blocks(markdown_content: str)`

**目的**: Markdown文字列をNotionブロック形式に変換

**パラメータ**:
- `markdown_content` (str): 変換するMarkdownコンテンツ

**戻り値**: 
- `List[Dict[str, Any]]`: Notionブロック仕様のディクショナリのリスト

**サポートされる変換**:

| Markdown要素 | Notionブロック型 | 実装 |
|-------------|----------------|-----|
| `# 見出し` | `heading_1` | `_create_heading_block(1, text)` |
| `## 見出し` | `heading_2` | `_create_heading_block(2, text)` |
| `### 見出し` | `heading_3` | `_create_heading_block(3, text)` |
| 段落 | `paragraph` | `_create_paragraph_block(text)` |
| `- 項目` | `bulleted_list_item` | `_create_list_block(text, False)` |
| `1. 項目` | `numbered_list_item` | `_create_list_block(text, True)` |
| ` ```code``` ` | `code` | `_create_code_block(code, language)` |

##### `_create_rich_text(text: str)`

**目的**: テキストの書式設定（太字、斜体など）を処理

**実装詳細**:
```python
def _create_rich_text(self, text: str) -> List[Dict[str, Any]]:
    # **太字** → {"type": "text", "annotations": {"bold": True}}
    # *斜体* → {"type": "text", "annotations": {"italic": True}}
    # `コード` → {"type": "text", "annotations": {"code": True}}
```

### NotionUploader

Notion APIとの統合と大容量コンテンツの処理を担当。

#### クラス定義

```python
class NotionUploader:
    """Notion API統合とページ作成を管理"""
    
    def __init__(self, token: str):
        """Notion clientを初期化し、認証を設定"""
        
    def upload_markdown(self, markdown_content: str, parent_page_id: str, title: str) -> str:
        """完全なmarkdown → notion変換プロセス"""
```

#### 主要メソッド

##### `upload_markdown(markdown_content, parent_page_id, title)`

**目的**: Markdownコンテンツの完全なアップロードプロセス

**プロセスフロー**:
```python
def upload_markdown(self, markdown_content: str, parent_page_id: str, title: str) -> str:
    # 1. Markdownをブロックに変換
    blocks = self.processor.convert_to_notion_blocks(markdown_content)
    
    # 2. 初期ページを作成
    page = self.client.pages.create(
        parent={"page_id": parent_page_id},
        properties={"title": {"title": [{"text": {"content": title}}]}}
    )
    
    # 3. 大容量コンテンツ対応でブロックを追加
    self._create_page_with_blocks(page["id"], blocks)
    
    return page["url"]
```

##### `_create_page_with_blocks(page_id, blocks)`

**目的**: 100ブロック制限を考慮したブロックの追加

**実装戦略**:
```python
def _create_page_with_blocks(self, page_id: str, blocks: List[Dict]) -> None:
    """100ブロック制限を処理する自動分割実装"""
    
    # 100ブロックずつに分割
    for i in range(0, len(blocks), 100):
        chunk = blocks[i:i+100]
        
        # APIコール実行
        self.client.blocks.children.append(
            block_id=page_id,
            children=chunk
        )
        
        # レート制限対応
        time.sleep(0.1)
```

##### `extract_page_id_from_url(notion_url)`

**目的**: 様々なNotion URLからページIDを抽出

**実装**:
```python
@staticmethod
def extract_page_id_from_url(notion_url: str) -> str:
    """URLパターンマッチングでページIDを抽出"""
    
    patterns = [
        r'https://(?:www\.)?notion\.so/([a-f0-9]{32})',
        r'https://(?:www\.)?notion\.so/.*/([a-f0-9-]+)',
        # 他のパターン...
    ]
    
    for pattern in patterns:
        match = re.search(pattern, notion_url)
        if match:
            return match.group(1).replace('-', '')
    
    raise ValueError(f"有効なNotion URLではありません: {notion_url}")
```

### MCPServer

Model Context Protocol実装によるAI統合。

#### クラス定義

```python
class MCPServer:
    """FastMCPを使用したMCPサーバー実装"""
    
    def __init__(self):
        """サーバーとツールハンドラーを初期化"""
        
    async def upload_markdown_tool(self, filepath: str, parent_url: str, title: str = None) -> str:
        """ファイルベースのmarkdownアップロードツール"""
        
    async def upload_markdown_content_tool(self, content: str, parent_url: str, title: str) -> str:
        """コンテンツベースのmarkdownアップロードツール"""
```

#### ツール実装

##### `upload_markdown_tool`

**MCP ツール定義**:
```python
@server.tool()
async def upload_markdown(
    filepath: Annotated[str, "Markdownファイルへの絶対パス"],
    parent_url: Annotated[str, "親NotionページのURL"], 
    title: Annotated[str, "ページタイトル（省略可）"] = None
) -> str:
    """ローカルMarkdownファイルをNotionにアップロード"""
```

**エラーハンドリング戦略**:
```python
try:
    # ファイル読み取り
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # URL処理
    page_id = NotionUploader.extract_page_id_from_url(parent_url)
    
    # アップロード実行
    result_url = uploader.upload_markdown(content, page_id, title or Path(filepath).stem)
    
except FileNotFoundError:
    return f"エラー: ファイルが見つかりません: {filepath}"
except ValueError as e:
    return f"エラー: {str(e)}"
except Exception as e:
    return f"アップロードエラー: {str(e)}"
```

## データフロー

### 完全なプロセスフロー

```
1. AIアシスタント要求
   ↓
2. MCP Server (server.py)
   ├── ファイル読み取り/コンテンツ受信
   ├── URL検証とページID抽出
   └── NotionUploader呼び出し
   ↓
3. NotionUploader (notion_uploader.py)
   ├── MarkdownProcessor呼び出し
   ├── 初期ページ作成
   └── ブロック追加（100個ずつ）
   ↓
4. MarkdownProcessor (markdown_processor.py)
   ├── Markdown解析（Mistune）
   ├── ブロック変換
   └── リッチテキスト処理
   ↓
5. Notion API
   ├── ページ作成API
   └── ブロック追加API（複数回）
```

### エラーハンドリングフロー

```
任意の段階でエラー発生
   ↓
例外キャッチ
   ↓
ユーザーフレンドリーなメッセージ生成
   ↓
MCPクライアントに返却
   ↓
AIアシスタントに表示
```

## 設計パターン

### 責任の分離

- **MarkdownProcessor**: Markdown解析のみに集中
- **NotionUploader**: API統合とビジネスロジック
- **MCPServer**: プロトコル処理とユーザーインターフェース

### エラー処理戦略

```python
# 層化エラーハンドリング
try:
    # コア処理
    result = process_data()
except SpecificError as e:
    # 特定エラーの処理
    logger.error(f"特定エラー: {e}")
    return user_friendly_message(e)
except Exception as e:
    # 一般エラーの処理 
    logger.error(f"予期しないエラー: {e}")
    return "内部エラーが発生しました"
```

### 非同期処理

```python
# MCPは非同期処理を要求
async def upload_process():
    # I/Oバウンド操作を非同期で処理
    content = await read_file_async(filepath)
    result = await notion_upload_async(content)
    return result
```

## パフォーマンス考慮事項

### メモリ使用量

- **ストリーミング処理**: 大きなファイルの読み取り時
- **ブロック分割**: メモリ効率的な100ブロックずつの処理
- **レスポンス管理**: 大きなレスポンスオブジェクトの適切な処理

### API効率性

```python
# レート制限対応
time.sleep(0.1)  # APIコール間の待機

# バッチ処理最適化
chunks = [blocks[i:i+100] for i in range(0, len(blocks), 100)]
for chunk in chunks:
    api_call(chunk)
```

## テスト戦略

### ユニットテスト構造

```python
class TestMarkdownProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = MarkdownProcessor()
    
    def test_heading_conversion(self):
        # 見出し変換のテスト
        
    def test_list_conversion(self):
        # リスト変換のテスト
        
    @patch('notion_client.Client')
    def test_with_mocked_api(self, mock_client):
        # モッククライアントを使用したテスト
```

### 統合テスト

```python
class TestNotionIntegration(unittest.TestCase):
    @unittest.skipIf(not NOTION_TOKEN, "NOTION_TOKENが必要")
    def test_real_upload(self):
        # 実際のNotion APIを使用したテスト
```

## 拡張ポイント

### 新しいMarkdown要素の追加

```python
# markdown_processor.pyに新しい変換を追加
def _handle_new_element(self, element):
    """新しいMarkdown要素の処理"""
    return {
        "object": "block",
        "type": "new_block_type",
        "new_block_type": {
            # 新しいブロック定義
        }
    }
```

### 追加MCPツール

```python
# server.pyに新しいツールを追加
@server.tool()
async def new_tool(param: str) -> str:
    """新しい機能のMCPツール"""
    # 実装
```

## セキュリティ考慮事項

### 入力検証

```python
def validate_input(content: str) -> bool:
    """入力コンテンツの検証"""
    if not content or len(content) > MAX_CONTENT_SIZE:
        return False
    return True
```

### 認証管理

```python
# 環境変数からの安全なトークン取得
token = os.getenv('NOTION_TOKEN')
if not token:
    raise ValueError("NOTION_TOKENが設定されていません")
```

## デバッグユーティリティ

### ログ設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 開発モード

```python
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'

if DEBUG_MODE:
    # デバッグ情報の出力
    logger.debug(f"処理するブロック数: {len(blocks)}")
```