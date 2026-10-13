#!/bin/bash
# 🚀 一键把 网站/ 同步到阿里云服务器（流程与门禁见 剧本/部署.md）
set -e
cd "$(dirname "$0")"

if [ ! -f 部署配置 ]; then
  echo "❌ 还没有服务器信息：先把 部署配置.example 复制为 部署配置 并填写（步骤见 README.md）"
  exit 1
fi
source 部署配置

echo "📸 服务器快照上一版（保留最近 10 份）…"
ssh "$SERVER_USER@$SERVER_HOST" "
  mkdir -p '$SERVER_DIR-backups'
  if [ -d '$SERVER_DIR' ]; then
    rm -rf '$SERVER_DIR-backups/$(date +%Y%m%d-%H%M)'
    cp -r '$SERVER_DIR' '$SERVER_DIR-backups/$(date +%Y%m%d-%H%M)'
  fi
  ls -dt '$SERVER_DIR-backups'/*/ 2>/dev/null | tail -n +11 | xargs rm -rf 2>/dev/null || true
"

echo "🎁 上线包装：退出键 + 署名统一（QF工作室/皮皮）…"
python3 包装.py

echo "🚀 开始同步到 $SERVER_USER@$SERVER_HOST:$SERVER_DIR …"
rsync -avz --delete \
  --exclude '部署.sh' --exclude '部署配置' --exclude '部署配置.example' --exclude 'README.md' \
  --exclude '门禁扫描.py' --exclude '门禁词库.txt' --exclude '门禁报告.txt' --exclude '包装.py' \
  ./ "$SERVER_USER@$SERVER_HOST:$SERVER_DIR/"

echo ""
echo "✅ 同步完成！备案通过后正式地址：https://pipiai.top/ （当前域名待命，见 剧本/部署.md）"
