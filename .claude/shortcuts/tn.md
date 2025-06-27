# Terminal Notification (+tn)

This command is a shortcut to play a sound notification based on the current OS environment.

## Usage
```
+tn
```

## Behavior
Detects the OS and executes the appropriate command:

### OS Detection Method
Uses `uname -s` command to determine OS type:
- `Linux`: Linux environment
- `Darwin`: macOS environment

### Executed Commands
- **Linux**: `paplay /usr/share/sounds/freedesktop/stereo/complete.oga`
- **macOS**: `terminal-notifier -sound Bottle -message 'Claude Code task finished'`

## Purpose
Used to notify with sound when Claude Code completes a task.