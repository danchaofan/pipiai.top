#!/usr/bin/env python3
# 🎁 上线包装：部署前给 网站/games/ 里的游戏副本自动做两件事（幂等，可反复跑）：
#   ① 左上角「🏠 退出」键（回作品墙）
#   ② 署名品牌统一：QF工作室 / 皮皮（2026-09-06 爸爸拍板全站统一）
# 只改拷进网站的副本；作品集里的封存版本是成长纪念册，永远不动。
import os, re, glob

标记 = 'data-pipiai-exit="1"'
注入 = (
    '<style id="pipiai-exit-style">#pipiai-exit-btn{position:fixed;left:12px;top:12px;'
    'z-index:2147483647;display:inline-flex;align-items:center;gap:6px;padding:8px 14px;'
    'border-radius:999px;background:rgba(10,14,42,.72);border:1px solid rgba(255,214,10,.55);'
    'color:#ffd60a;font:800 14px/1.2 "PingFang SC","Microsoft YaHei",system-ui,sans-serif;'
    'text-decoration:none;opacity:.45;transition:opacity .2s;box-shadow:0 4px 14px rgba(0,0,0,.35)}'
    '#pipiai-exit-btn:hover{opacity:1}</style>'
    '<a id="pipiai-exit-btn" data-pipiai-exit="1" href="../../index.html" '
    'title="回到游戏中心">🏠 退出</a>'
)

# 品牌替换（只动画面上的署名字样，不碰代码逻辑；新游戏照此口径写就不用换）
品牌替换 = [
    ('闪电游戏工作室', 'QF工作室'),
    ('大王专属定制', '皮皮专属定制'),
    ('大王出品', '皮皮出品'),
    ('——大王', '——皮皮'),   # 片尾署名，如「编剧·导演——大王」
]

根 = os.path.dirname(os.path.abspath(__file__))
for 路 in sorted(glob.glob(os.path.join(根, 'games', '*', 'index.html'))):
    with open(路, encoding='utf-8', errors='ignore') as f:
        文 = f.read()
    原文 = 文
    for 旧, 新 in 品牌替换:
        文 = 文.replace(旧, 新)

    键 = '退出键已在'
    if 标记 not in 文:
        文, n = re.subn(r'(<body[^>]*>)', lambda m: m.group(1) + 注入, 文, count=1)
        键 = '已加退出键' if n else '⚠️ 找不到 <body>，退出键没加上'

    if 文 != 原文:
        with open(路, 'w', encoding='utf-8') as f:
            f.write(文)
    名 = os.path.relpath(路, 根)
    换了 = '署名已统一' if any(旧 in 原文 for 旧, _ in 品牌替换) else '署名本来就对'
    print(f'🎁 {名}: {键} · {换了}')
print('完成（幂等，可反复运行）')
