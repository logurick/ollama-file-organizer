# アーキテクチャ

## 責務分離

- Scanner: ファイル発見とメタデータ取得
- Extractor: 文書本文抽出
- Ollama Client: 構造化分類
- Destination Resolver: category_idとテンプレートから相対移動先を解決
- Path Safety: ルート外アクセス拒否
- File Operation: move / undo
- API: UIや外部連携との境界

## 重要な境界

Ollama出力はPydantic Schemaで検証し、移動先はバックエンドの許可済みテンプレートからのみ生成します。
