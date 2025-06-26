# Terminal Notification (+tn)

このコマンドは、現在のOS環境に応じて音を鳴らすためのショートカットです。

## 使用方法
```
+tn
```

## 動作
OS判定を行い、適切なコマンドを実行します：

### OS判定方法
`uname -s` コマンドでOS種別を取得し、結果に応じて分岐：
- `Linux` の場合: Linux環境
- `Darwin` の場合: macOS環境

### 実行コマンド
- **Linux**: `paplay /usr/share/sounds/freedesktop/stereo/complete.oga`
- **macOS**: `terminal-notifier -sound Bottle -message 'Claude Code task finished'`

## 用途
Claude Codeがタスクを完了した時に音で通知するために使用します。