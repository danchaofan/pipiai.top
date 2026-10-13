#!/usr/bin/env python3
# 🔍 QF工作室 · 门禁扫描器（用法：python3 门禁扫描.py）
# 扫描脚本所在目录（网站/），退出码：0=放行(🟢/🟡)  1=拦截(🔴)
# 报告同时打印并存到 网站/门禁报告.txt。红线定义见 剧本/部署.md。
import os, re, sys, datetime

扫 = os.path.dirname(os.path.abspath(__file__))
词库路径 = os.path.join(扫, '门禁词库.txt')
报告路径 = os.path.join(扫, '门禁报告.txt')
跳过 = {'部署.sh', '部署配置', '部署配置.example', 'README.md',
        '门禁扫描.py', '门禁词库.txt', '门禁报告.txt', '包装.py', '.DS_Store'}
文本后缀 = {'.html', '.css', '.js', '.json'}
白名单后缀 = {'.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg',
              '.gif', '.svg', '.ico', '.mp3', '.ogg', '.wav'}
体积上限 = 15 * 1024 * 1024

红线词, 观察词 = [], []
try:
    区 = None
    for 行 in open(词库路径, encoding='utf-8'):
        行 = 行.strip()
        if not 行 or 行.startswith('#'):
            continue
        if 行.startswith('['):
            区 = 行
        elif 区 and '红线' in 区:
            红线词.append(行)
        elif 区 and '观察' in 区:
            观察词.append(行)
except FileNotFoundError:
    print('⚠️ 找不到门禁词库.txt，只跑隐私/技术门')

隐私规则 = [
    # 校名类（"画质高中低"这种高频误报词已排除）
    ('学校名', re.compile(r'[\u4e00-\u9fa5A-Za-z]{2,8}(小学|中学|大学|实验学校|附属学校)')),
    ('年级班级', re.compile(r'\d{1,2}年级\s?\d{1,3}班')),
    ('手机号', re.compile(r'(?<!\d)1[3-9]\d{9}(?!\d)')),
    ('身份证', re.compile(r'(?<!\d)\d{17}[0-9Xx](?!\d)')),
]

红, 黄, 统计 = [], [], {}

# 分类对账：数据.js 里填的分类必须存在于 index.html 的分类表（2026-09-19 加，防"上架了却看不见"）
分类集 = set()
try:
    索引文 = open(os.path.join(扫, 'index.html'), encoding='utf-8', errors='ignore').read()
    分类m = re.search(r"分类表\s*=\s*\[(.*?)\]", 索引文)
    if 分类m:
        分类集 = {w.strip().strip("'\"") for w in 分类m.group(1).split(',') if w.strip()} - {'全部'}
except OSError:
    pass

for 目录, _, 文件们 in os.walk(扫):
    for 名 in 文件们:
        if 名 in 跳过:
            continue
        路 = os.path.join(目录, 名)
        相对 = os.path.relpath(路, 扫)
        后缀 = os.path.splitext(名)[1].lower()
        统计[后缀] = 统计.get(后缀, 0) + 1

        # 技术门：类型白名单 + 体积
        if 后缀 not in 白名单后缀:
            红.append(f'🔴 [技术] {相对}: 文件类型「{后缀 or "无后缀"}」不在白名单（php 等服务器脚本永久禁入）')
            continue
        if os.path.getsize(路) > 体积上限:
            红.append(f'🔴 [技术] {相对}: 超过 15MB 上限')
            continue

        if 后缀 not in 文本后缀:
            continue
        try:
            文本 = open(路, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue

        # 内容门
        for 词 in 红线词:
            i = 文本.find(词)
            if i >= 0:
                摘 = 文本[max(0, i - 15):i + len(词) + 15].replace('\n', ' ')
                红.append(f'🔴 [内容] {相对}: 命中「{词}」 …{摘}…')
        for 词 in 观察词:
            if 词 in 文本:
                黄.append(f'🟡 [观察] {相对}: 出现「{词}」')

        # 隐私门
        for 名字, 规则 in 隐私规则:
            m = 规则.search(文本)
            if m:
                红.append(f'🔴 [隐私] {相对}: {名字} → {m.group(0)}')

        # 外链清单（放行但报告）
        for m in re.finditer(r'https?://([A-Za-z0-9.\-]+)', 文本):
            域名 = m.group(1)
            if 域名 not in ('127.0.0.1', 'localhost'):
                黄.append(f'🟡 [外链] {相对}: {域名}')

        # 署名白名单 + 分类对账
        if 名 == '数据.js':
            if not re.search(r'boss:\s*"皮皮"', 文本):
                红.append('🔴 [隐私] 数据.js: 署名不是「皮皮」')
            if not re.search(r'name:\s*"QF工作室"', 文本):
                红.append('🔴 [隐私] 数据.js: 工作室名不对（站上口径是 QF工作室）')
            for cm in re.finditer(r'category:\s*"([^"]+)"', 文本):
                分类 = cm.group(1)
                if 分类集 and 分类 not in 分类集:
                    红.append(f'🔴 [技术] 数据.js: 分类「{分类}」不在站顶分类栏里'
                              '（要么改用已有分类，要么先去 index.html 的分类表加这个分类）')

黄 = sorted(set(黄))
行 = []
行.append(f'🔍 门禁扫描报告 · {datetime.datetime.now():%Y-%m-%d %H:%M}')
行.append(f'扫描: {扫} · 文件 {sum(统计.values())} 个（' +
           '，'.join(f'{k} {v}' for k, v in sorted(统计.items())) + '）')
行.append('')
行.append(f'🔴 拦截: {len(红)} 条')
行 += 红
行.append(f'🟡 观察: {len(黄)} 条（放行，事后报告给爸爸）')
行 += 黄
行.append('')
行.append('⛔ 拦下（红线命中；血腥词改编重扫；恐怖题材词上报爸爸——2026-09-06 规矩）' if 红
          else '✅ 放行（全自动 · 事后报告给爸爸）')
报文 = '\n'.join(行)
open(报告路径, 'w', encoding='utf-8').write(报文)
print(报文)
sys.exit(1 if 红 else 0)
