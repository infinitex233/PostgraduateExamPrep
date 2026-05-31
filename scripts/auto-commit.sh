#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# 检查是否有未提交的变更
if git diff-index --quiet HEAD -- && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "没有新的变更，跳过提交。"
  exit 0
fi

# 获取变更文件列表
changed=$(git diff --name-only HEAD 2>/dev/null || true)
untracked=$(git ls-files --others --exclude-standard 2>/dev/null || true)
all_files="$changed $untracked"

# 统计各类变更的文件数
daily_count=$(echo "$all_files" | grep -c "StudyProgress/DailyLogs/" || true)
review_count=$(echo "$all_files" | grep -c "StudyProgress/Reviews/" || true)
booknote_count=$(echo "$all_files" | grep -c "DigitalBooks/BookNotes/" || true)
index_count=$(echo "$all_files" | grep -c "ProgressIndex.md" || true)
other_count=$(echo "$all_files" | grep -v -c -E "(StudyProgress/DailyLogs/|StudyProgress/Reviews/|DigitalBooks/BookNotes/|ProgressIndex.md)" || true)

# 计算总文件数（排除空行）
total=$(echo "$all_files" | sed '/^$/d' | wc -l | tr -d ' ')

# 生成中文提交信息
parts=()
[ "$daily_count" -gt 0 ] && parts+=("学习记录(${daily_count}个)")
[ "$review_count" -gt 0 ] && parts+=("复习总结(${review_count}个)")
[ "$booknote_count" -gt 0 ] && parts+=("教材笔记(${booknote_count}个)")
[ "$index_count" -gt 0 ] && parts+=("进度索引")
[ "$other_count" -gt 0 ] && parts+=("其他(${other_count}个)")

if [ ${#parts[@]} -eq 0 ]; then
  msg="更新复习进度（${total}个文件）"
else
  # 用顿号连接各部分
  joined=$(printf "、%s" "${parts[@]}")
  joined="${joined:1}"
  msg="更新${joined}"
fi

echo "提交信息: $msg"
git add -A
git commit -m "$msg"
git push origin main
echo "推送完成。"
