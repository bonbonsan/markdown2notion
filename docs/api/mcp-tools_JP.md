# MCPツールリファレンス（日本語版）

この文書では、markdown2notion MCPサーバーによって提供されるツールの詳細なAPIリファレンスを提供します。

## 概要

markdown2notion MCPサーバーは、MarkdownコンテンツをNotionワークスペースにシームレスにアップロードするための2つの主要なツールを提供します。

## ツール

### upload_markdown

ローカルMarkdownファイルをNotionページに変換してアップロードします。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|----|----|------|
| `filepath` | string | ✓ | アップロードするMarkdownファイルの絶対パス |
| `parent_url` | string | ✓ | 新しいページを作成する親NotionページのURL |
| `title` | string | ✗ | 新しいページのカスタムタイトル（デフォルトはファイル名） |

#### 戻り値

```json
{
  "status": "success",
  "page_url": "https://notion.so/page-id",
  "message": "MarkdownファイルがNotionに正常にアップロードされました"
}
```

#### 例

```python
# MCPクライアント経由での使用例
result = await client.call_tool(
    "upload_markdown",
    {
        "filepath": "/Users/john/documents/project-notes.md",
        "parent_url": "https://notion.so/workspace/parent-page-abc123",
        "title": "プロジェクトメモ"
    }
)
```

#### エラーハンドリング

| エラー | 原因 | 解決方法 |
|--------|------|---------|
| `FileNotFoundError` | ファイルパスが無効 | ファイルパスが存在し、アクセス可能であることを確認 |
| `PermissionError` | ファイル読み取り権限がない | ファイル権限を確認 |
| `ValueError` | 無効なNotion URL | 有効なNotion ページURLを提供 |
| `APIError` | Notion APIエラー | APIトークンとページアクセス権を確認 |

### upload_markdown_content

Markdown文字列を直接Notionページに変換してアップロードします。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|----|----|------|
| `content` | string | ✓ | アップロードするMarkdownコンテンツ |
| `parent_url` | string | ✓ | 新しいページを作成する親NotionページのURL |
| `title` | string | ✓ | 新しいページのタイトル |

#### 戻り値

```json
{
  "status": "success", 
  "page_url": "https://notion.so/page-id",
  "message": "Markdownコンテンツが正常にアップロードされました"
}
```

#### 例

```python
# MCPクライアント経由での使用例
result = await client.call_tool(
    "upload_markdown_content",
    {
        "content": "# タイトル\n\nこれはサンプルコンテンツです。",
        "parent_url": "https://notion.so/workspace/parent-page-abc123",
        "title": "新しいページ"
    }
)
```

#### エラーハンドリング

| エラー | 原因 | 解決方法 |
|--------|------|---------|
| `ValueError` | 空のコンテンツまたは無効なURL | 有効なコンテンツとNotion URLを提供 |
| `APIError` | Notion APIエラー | APIトークンとページアクセス権を確認 |

## 高度な機能

### 自動ブロック分割

両ツールとも、100ブロックを超えるコンテンツの自動処理をサポートしています：

- **問題**: NotionのAPIは単一リクエストあたり最大100ブロック
- **解決方法**: コンテンツを自動的に分割し、複数のAPIコールで処理
- **結果**: 大きなドキュメントも単一のNotionページとして正常にアップロード

### URL形式のサポート

以下のNotion URL形式をサポートしています：

```
✓ https://notion.so/workspace/page-title-abc123
✓ https://notion.so/page-title-abc123  
✓ https://www.notion.so/workspace/page-title-abc123
✓ 内部データベースURL
```

### サポートされるMarkdown要素

| 要素 | Notionブロック型 | 例 |
|------|----------------|-----|
| 見出し | heading_1, heading_2, heading_3 | `# 見出し` |
| 段落 | paragraph | 通常のテキスト |
| リスト | bulleted_list_item | `- 項目` |
| 番号付きリスト | numbered_list_item | `1. 項目` |
| コードブロック | code | ` ```python ` |
| インラインコード | rich_text with code | `` `code` `` |
| 太字 | rich_text with bold | `**太字**` |
| 斜体 | rich_text with italic | `*斜体*` |
| 取り消し線 | rich_text with strikethrough | `~~取り消し~~` |

## 設定要件

### 環境変数

| 変数 | 説明 | 必須 |
|------|------|------|
| `NOTION_TOKEN` | Notion統合トークン | ✓ |

### Notion権限

統合には以下の権限が必要です：

- **ページの読み取り**: 親ページの存在確認
- **ページの作成**: 新しいページの作成
- **コンテンツの挿入**: ブロックの追加

## 制限事項

### APIレート制限

- Notion APIには1分間に3リクエストのレート制限があります
- 大きなドキュメントは複数のAPIコールが必要な場合があります
- ツールは自動的にレート制限を処理します

### コンテンツサイズ

- 個々のブロックは最大2000文字まで
- 画像やファイルの埋め込みは現在サポートされていません
- テーブルは将来の更新でサポート予定

### URL要件

- 親ページは統合からアクセス可能である必要があります
- データベースへの直接アップロードは現在サポートされていません

## トラブルシューティング

### 一般的な問題

**「ページが見つかりません」**
- Notionページが存在し、統合がアクセス権を持っていることを確認
- URLが正しい形式であることを確認

**「レート制限エラー」**
- しばらく待ってから再試行
- 並行アップロードを避ける

**「認証エラー」**
- `NOTION_TOKEN`環境変数を確認
- トークンが有効で期限切れでないことを確認

### デバッグのヒント

1. **詳細ログ**: エラーメッセージには通常特定の問題が含まれています
2. **URL検証**: ブラウザでNotion URLが正常に開くことを確認
3. **権限確認**: Notionワークスペースでの統合権限を確認
4. **ファイル確認**: Markdownファイルが有効で読み取り可能であることを確認

## API応答の例

### 成功応答

```json
{
  "status": "success",
  "page_url": "https://notion.so/workspace/new-page-def456", 
  "message": "Markdownが正常にアップロードされました",
  "blocks_created": 25,
  "title": "プロジェクトドキュメント"
}
```

### エラー応答

```json
{
  "status": "error",
  "error_type": "FileNotFoundError",
  "message": "指定されたファイルが見つかりません: /path/to/file.md",
  "details": "ファイルパスを確認し、ファイルが存在することを確認してください"
}
```

## ベストプラクティス

### ファイル管理

- MarkdownファイルにはUTF-8エンコーディングを使用
- 特殊文字やemojisはサポートされています
- バックアップコピーを保持することを推奨

### パフォーマンス

- 大きなファイルの場合、処理に時間がかかる場合があります
- 定期的なアップロードにはバッチ処理を検討
- ネットワーク接続の安定性を確保

### セキュリティ

- Notionトークンを安全に保管
- 最小限必要な権限のみを付与
- 定期的なアクセス権の確認を実施