# AutoTune Reviewer

Spotifyの曲URLから自動的にブログ記事とSNS投稿を生成するシステム

## 📋 必要要件

- Python 3.8以上
- OpenAI API キー

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install requests beautifulsoup4 openai
```

または、以下の内容で`requirements.txt`を作成して：

```
requests>=2.31.0
beautifulsoup4>=4.12.0
openai>=1.0.0
```

実行：

```bash
pip install -r requirements.txt
```

### 2. OpenAI APIキーの設定

環境変数として設定：

```bash
# macOS/Linux
export OPENAI_API_KEY='your-api-key-here'

# Windows (コマンドプロンプト)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

または、`main.py`の`OPENAI_API_KEY`変数に直接設定（非推奨）。

## 📝 使い方

### 1. 入力ファイルの準備

`input.csv`に処理したいSpotify URLを追加：

```csv
ID,Spotify_URL,処理フラグ
1,https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp,NEW
2,https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI,NEW
```

### 2. スクリプトの実行

```bash
python main.py
```

### 3. 結果の確認

- `output/`ディレクトリに`post_[ID].md`ファイルが生成されます
- `input.csv`の処理フラグが`DONE`に更新されます

## 📁 ファイル構造

```
AutoTuneReviewer/
├── main.py              # メインスクリプト
├── input.csv            # 入力データ
├── output/              # 生成された記事（自動作成）
│   ├── post_1.md
│   ├── post_2.md
│   └── ...
├── requirements.txt     # 依存パッケージ
└── README.md           # このファイル
```

## 🔧 処理フロー

1. **CSV読み込み**: `処理フラグ`が`NEW`の行を抽出
2. **情報抽出**: SpotifyのURLから曲名、アーティスト名、埋め込みコードを取得
3. **コンテンツ生成**: OpenAI APIで記事とSNS投稿を生成
4. **ファイル出力**: Markdown形式で記事を保存
5. **フラグ更新**: 処理完了した行を`DONE`に更新

## ⚙️ カスタマイズ

### LLMモデルの変更

`main.py`の`generate_content_with_llm`関数内：

```python
'model': 'gpt-4o',  # gpt-3.5-turbo などに変更可能
```

### 記事の文字数調整

`generate_content_with_llm`関数のプロンプトを編集：

```python
prompt = f"""...ブログ紹介文（日本語で1200字程度）..."""
```

## 🚨 トラブルシューティング

### OpenAI APIエラー

- APIキーが正しく設定されているか確認
- APIの使用制限や料金残高を確認
- インターネット接続を確認

### Spotify情報の取得失敗

- URLが正しい形式か確認（`https://open.spotify.com/track/...`）
- ネットワーク接続を確認
- フォールバック機能により、最低限の埋め込みコードは生成されます

## 📈 次のステップ（フェーズ2）

- [ ] Webサイトへの自動公開機能
- [ ] SNS自動投稿機能
- [ ] Streamlit/Next.jsでのUI構築
- [ ] Vercelへのデプロイ

## 📄 ライセンス

MIT License
