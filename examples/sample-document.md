# プロジェクト概要

このドキュメントはMarkdown2Notionのテスト用サンプルファイルです。

## 主な機能

Markdown2Notionサーバーは以下の機能を提供します：

- **ファイルアップロード**: Markdownファイルを直接Notionにアップロード
- **コンテンツ変換**: 各種Markdown要素をNotionブロックに変換
- **タイトル自動設定**: ファイル名をページタイトルとして使用

## サポートする要素

### テキスト要素

通常の段落テキストはもちろん、**太字**や*斜体*もサポートしています。

### リスト

#### 箇条書き
- 項目1
- 項目2  
- 項目3

#### 番号付きリスト
1. 最初の項目
2. 二番目の項目
3. 三番目の項目

### コードブロック

```python
def hello_world():
    print("Hello, Notion!")
    return "success"
```

```javascript
function greetNotion() {
    console.log("Hello from JavaScript!");
    return true;
}
```

### 引用

> これは引用ブロックの例です。
> 重要な情報を強調するために使用できます。

### ToDo項目

- [ ] 未完了タスク
- [x] 完了済みタスク
- [ ] もう一つの未完了タスク

## 技術詳細

この文書は`sample-document.md`として保存されているため、Notionでは「sample-document」というタイトルのページとして作成されます。

### 使用技術

- **FastMCP**: MCPサーバー実装
- **Notion API**: ページ作成とコンテンツ管理
- **Python**: サーバーサイド処理

## 結論

Markdown2NotionはMarkdownファイルをNotionページとして効率的にアップロードするための実用的なツールです。