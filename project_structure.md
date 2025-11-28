# AutoTune Reviewer - Next.js プロジェクト構造

```
autotune-reviewer/
├── pages/
│   ├── index.js                    # トップページ（記事一覧）
│   └── posts/
│       └── [id].js                 # 記事詳細ページ（動的ルーティング）
├── scripts/
│   ├── main.py                     # 記事生成スクリプト（改良版）
│   └── input.csv                   # 入力データ
├── data/
│   └── posts/                      # 生成された記事（Markdown + JSON）
├── public/
│   └── styles/
│       └── global.css              # グローバルスタイル
├── lib/
│   └── posts.js                    # 記事データ取得ユーティリティ
├── components/
│   └── Layout.js                   # レイアウトコンポーネント
├── .env.local                      # 環境変数（OpenAI APIキー）
├── .gitignore
├── package.json
├── requirements.txt                # Python依存パッケージ
├── next.config.js
└── README.md
```

## 主要な変更点

1. **`main.py`**: JSON形式のメタデータも出力
2. **Next.js pages**: SSGで静的記事を生成
3. **ビルドプロセス**: Python → Next.js の順で実行
4. **Vercel対応**: 環境変数とビルド設定を最適化
