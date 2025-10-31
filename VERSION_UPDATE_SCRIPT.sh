#!/bin/bash
# 批量更新所有文档中的版本号

echo "开始批量更新文档版本号..."

# 需要更新的文件列表
FILES=(
    "BUILD_SUCCESS_REPORT.md"
    "FINAL_BUILD_SUMMARY.md"
    "RELEASE_NOTES_v18.0.0.md"
    "RELEASE_SUCCESS_REPORT.md"
    "MANUAL_RELEASE_GUIDE.md"
    "OPTIMIZATION_SUMMARY_v17.0.0.md"
    "docs/USER_MANUAL.md"
    "docs/用户手册.md"
    "docs/开发指南.md"
    "docs/构建发布指南.md"
)

# 替换 v16.0.0 → v18.0.0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "更新 $file..."
        sed -i 's/v16\.0\.0/v18.0.0/g' "$file"
        sed -i 's/16\.0\.0/18.0.0/g' "$file"
    fi
done

# 替换 v17.0.0 → v18.0.0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        sed -i 's/v17\.0\.0/v18.0.0/g' "$file"
        sed -i 's/17\.0\.0/18.0.0/g' "$file"
    fi
done

echo "✅ 批量更新完成！"
