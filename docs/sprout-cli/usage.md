# sprout 使用方法

## インストール

```bash
# 開発版のインストール
pip install -e .

# または通常のインストール
pip install .
```

## 基本的な使い方

### 1. 新しい開発環境の作成

```bash
sprout create feature-branch
```

このコマンドは以下を実行します：
1. `.sprout/feature-branch`にworktreeを作成
2. `.env.example`をテンプレートとして`.env`を生成
3. 必要な環境変数の入力を促す
4. ポート番号を自動的に割り当てる

### 2. 開発環境の一覧表示

```bash
sprout ls
```

出力例：
```
                    Sprout Worktrees                    
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Branch        ┃ Path                    ┃ Status   ┃ Last Modified   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ feature-auth  │ .sprout/feature-auth    │ ● current│ 2024-01-15 14:30│
├───────────────┼─────────────────────────┼──────────┼─────────────────┤
│ feature-ui    │ .sprout/feature-ui      │          │ 2024-01-14 10:15│
└───────────────┴─────────────────────────┴──────────┴─────────────────┘
```

### 3. 開発環境の削除

```bash
sprout rm feature-branch
```

確認プロンプトが表示されます：
- worktreeの削除確認
- gitブランチの削除確認（オプション）

### 4. 開発環境のパス取得

```bash
# パスを表示
sprout path feature-branch

# 直接移動する場合
cd $(sprout path feature-branch)
```

## .env.example テンプレートの書き方

### 基本的な環境変数
```env
DATABASE_URL={{ DATABASE_URL }}
API_KEY={{ API_KEY }}
```

### 自動ポート割り当て
```env
WEB_PORT={{ auto_port() }}
API_PORT={{ auto_port() }}
DB_PORT={{ auto_port() }}
```

### Docker Compose変数（そのまま保持）
```env
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-myproject}
```

### 固定値
```env
ENVIRONMENT=development
DEBUG=true
```

## 実践的な例

### 1. 複数の開発環境を並行運用

```bash
# 認証機能の開発
sprout create feature-auth
cd .sprout/feature-auth
docker compose up -d

# UI改善の開発（別ターミナル）
sprout create feature-ui  
cd .sprout/feature-ui
docker compose up -d

# ポートは自動的に異なる番号が割り当てられる
```

### 2. 環境変数の事前設定

```bash
# シェルで環境変数を設定
export API_KEY="my-secret-key"
export DATABASE_URL="postgres://localhost/mydb"

# sproutは自動的にこれらの値を使用
sprout create feature-branch
```

### 3. ブランチの切り替え

```bash
# 現在の環境を確認
sprout ls

# 別の環境に移動
cd $(sprout path another-branch)
```

## トラブルシューティング

### "Not in a git repository" エラー
- Gitリポジトリのルートディレクトリで実行してください

### ".env.example file not found" エラー
- プロジェクトルートに`.env.example`を作成してください

### "Could not find an available port" エラー
- 多くのポートが使用中の場合に発生
- 不要なサービスを停止してください

### worktreeが削除できない
- 該当ディレクトリでプロセスが実行中の可能性
- ディレクトリを移動してから再試行してください