# AutoTune Reviewer - Next.js版

Spotifyの曲URLから自動的にブログ記事とSNS投稿を生成し、静的ブログサイトとして公開するシステム

## 🎯 特徴

- **自動記事生成**: Spotify URLから曲情報を抽出し、OpenAI APIで記事を自動生成
- **静的サイト生成**: Next.jsのSSGで高速な静的ブログを構築
- **Vercelデプロイ**: ワンクリックでデプロイ可能
- **レスポンシブデザイン**: モバイルからデスクトップまで最適表示

## 📁 プロジェクト構造

```
autotune-reviewer/
├── pages/
│   ├── _app.js                     # Next.jsアプリ設定
│   ├── index.js                    # トップページ（記事一覧）
│   └── posts/
│       └── [id].js                 # 記事詳細ページ
├── scripts/
│   ├── main.py                     # 記事生成スクリプト
│   └── input.csv                   # 入力データ
├── data/
│   └── posts/                      # 生成された記事
│       ├── 1.md                    # Markdown記事
│       ├── 1.json                  # メタデータ
│       └── ...
├── lib/
│   └── posts.js                    # 記事データ取得
├── styles/
│   ├── globals.css                 # グローバルスタイル
│   ├── Home.module.css             # トップページスタイル
│   └── Post.module.css             # 記事ページスタイル
├── .env.local                      # 環境変数
├── .gitignore
├── package.json
├── next.config.js
├── vercel.json
├── requirements.txt
└── README.md
```

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/autotune-reviewer.git
cd autotune-reviewer
```

### 2. 依存パッケージのインストール

#### Node.js依存パッケージ

```bash
npm install
```

#### Python依存パッケージ

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.local` ファイルを作成：

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. 入力データの準備

`scripts/input.csv` に処理したいSpotify URLを追加：

```csv
ID,Spotify_URL,処理フラグ
1,https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp,NEW
2,https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI,NEW
```

## 💻 ローカル開発

### 記事の生成とサイトの起動

```bash
# 開発サーバーを起動（記事生成も自動実行）
npm run dev
```

ブラウザで `http://localhost:3000` にアクセス

### 個別コマンド

```bash
# 記事のみ生成
python scripts/main.py

# Next.jsのみ起動
npm run dev

# プロダクションビルド
npm run build
npm start
```

## 🌐 Vercelへのデプロイ

### 方法1: GitHub連携（推奨）

1. GitHubにリポジトリをプッシュ
2. [Vercel](https://vercel.com)にログイン
3. "New Project" → リポジトリを選択
4. 環境変数を設定:
   - `OPENAI_API_KEY`: OpenAI APIキー
5. "Deploy" をクリック

### 方法2: Vercel CLI

```bash
# Vercel CLIをインストール
npm i -g vercel

# デプロイ
vercel

# 環境変数を設定
vercel env add OPENAI_API_KEY

# プロダクションデプロイ
vercel --prod
```

### デプロイ時の注意点

- `vercel.json` でビルドコマンドが設定済み
- Pythonスクリプトが自動実行され、記事が生成される
- 生成された記事は静的サイトとしてデプロイされる

## 🔧 カスタマイズ

### LLMモデルの変更

`scripts/main.py` の `generate_content_with_llm` 関数:

```python
'model': 'gpt-4o',  # gpt-3.5-turbo などに変更可能
```

### 記事の文字数調整

プロンプト内の指示を変更:

```python
prompt = f"""...ブログ紹介文（日本語で1200字程度）..."""
```

### デザインのカスタマイズ

- `styles/Home.module.css`: トップページ
- `styles/Post.module.css`: 記事ページ
- `styles/globals.css`: 全体共通

## 📊 処理フロー

```
┌─────────────────┐
│  input.csv      │ ← Spotify URLを追加
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  main.py        │ ← Python記事生成スクリプト
│  - 曲情報抽出   │
│  - LLM記事生成  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  data/posts/    │ ← Markdown + JSON生成
│  - 1.md         │
│  - 1.json       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Next.js Build  │ ← 静的サイト生成
│  - SSG          │
│  - HTML出力     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vercel Deploy  │ ← 本番公開
└─────────────────┘
```

## 🚨 トラブルシューティング

### ビルドエラー: Pythonが見つからない

Vercelの環境変数に以下を追加:

```
PYTHON_VERSION=3.9
```

### 記事が表示されない

1. `data/posts/` ディレクトリに `.md` と `.json` ファイルが生成されているか確認
2. `npm run build` を実行してエラーがないか確認
3. ブラウザのコンソールでエラーを確認

### OpenAI APIエラー

- APIキーが正しく設定されているか確認
- APIの使用制限や料金残高を確認
- `scripts/main.py` はAPIキーがない場合、ダミーデータで動作します

### Spotify情報の取得失敗

- URLが正しい形式か確認（`https://open.spotify.com/track/...`）
- 埋め込みコードは生成されるため、記事自体は作成されます

## 📈 今後の機能拡張

- [ ] SNS自動投稿機能（Twitter/X API連携）
- [ ] 記事の自動更新（GitHub Actions）
- [ ] 検索機能の追加
- [ ] タグ・カテゴリー機能
- [ ] コメント機能
- [ ] アクセス解析

## 🤝 コントリビューション

プルリクエストを歓迎します！

1. フォーク
2. フィーチャーブランチを作成（`git checkout -b feature/amazing-feature`）
3. コミット（`git commit -m 'Add amazing feature'`）
4. プッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを作成

## 📄 ライセンス

MIT License

## 🙏 謝辞

- [Next.js](https://nextjs.org/)
- [OpenAI](https://openai.com/)
- [Spotify](https://www.spotify.com/)
- [Vercel](https://vercel.com/)
