#!/bin/bash
# 批量更新文档中的版本号
# v1.13.3 -> v1.14.0

echo "开始批量更新版本号..."

# 需要更新的文档列表（排除特定版本的changelog）
files=(
    "BUILD_EXECUTION_GUIDE.md"
    "BUILD_INDEX.md"
    "BUILD_RELEASE_GUIDE.md"
    "BUILD_TOOLS_README.md"
    "GITHUB_ARCHIVE_SUMMARY.md"
    "LOCAL_BUILD_GUIDE.md"
    "PRE_BUILD_CHECKLIST.md"
    "QUICK_BUILD_REFERENCE.md"
    "RELEASE_GUIDE.md"
    "docs/CI_CD_问题排查指南.md"
    "docs/一键安装指南.md"
    "docs/应用启动失败排查指南.md"
    "docs/构建发布指南.md"
    "docs/架构设计.md"
    "docs/诊断配置向导问题指南.md"
)

# 备份计数
updated=0
skipped=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # 检查文件是否包含旧版本号
        if grep -q "1\.13\.3\|v1\.13\.3" "$file"; then
            echo "更新: $file"
            
            # 使用sed批量替换（macOS和Linux兼容）
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' 's/版本：v1\.13\.3/版本：v1.14.0/g' "$file"
                sed -i '' 's/版本: v1\.13\.3/版本: v1.14.0/g' "$file"
                sed -i '' 's/v1\.13\.3/v1.14.0/g' "$file"
                sed -i '' 's/1\.13\.3/1.14.0/g' "$file"
            else
                # Linux
                sed -i 's/版本：v1\.13\.3/版本：v1.14.0/g' "$file"
                sed -i 's/版本: v1\.13\.3/版本: v1.14.0/g' "$file"
                sed -i 's/v1\.13\.3/v1.14.0/g' "$file"
                sed -i 's/1\.13\.3/1.14.0/g' "$file"
            fi
            
            ((updated++))
        else
            echo "跳过: $file (无需更新)"
            ((skipped++))
        fi
    else
        echo "文件不存在: $file"
    fi
done

echo ""
echo "================================"
echo "批量更新完成！"
echo "================================"
echo "更新文件数: $updated"
echo "跳过文件数: $skipped"
echo ""
echo "请手动验证关键文档："
echo "- README.md"
echo "- INSTALLATION_GUIDE.md"
echo "- docs/用户手册.md"
echo "- docs/开发指南.md"
