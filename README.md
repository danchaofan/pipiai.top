# 🌐 作品网站部署指南（给出版人/爸爸）

零构建的纯静态站（HTML + CSS + JS），`数据.js` 是唯一要改的数据文件（一般由 `/publish` 命令代劳）。
本地预览：直接双击 `index.html`，或 `open index.html`。

## 一、服务器准备（阿里云，做一次就好）

1. 安全组放行 **80/443** 端口（ECS 控制台 → 安全组 → 添加入方向规则）。
2. 装好 nginx：`yum install -y nginx` 或 `apt install -y nginx`。
3. 建网站目录：`mkdir -p /var/www/studio`。
4. nginx 配置（`/etc/nginx/conf.d/studio.conf`）：

   ```nginx
   server {
       listen 80;
       server_name _;              # 买好域名后换成你的域名，如 game.example.com
       root /var/www/studio;
       index index.html;
       location / { try_files $uri $uri/ =404; }
   }
   ```

5. `nginx -t && systemctl reload nginx`，此时访问 `http://服务器IP` 应该能看到页面。

## 二、配置一键部署（本机，做一次就好）

1. `cp 部署配置.example 部署配置`，填入服务器 IP、用户名、目录。
2. 免密码登录（只需一次）：`ssh-copy-id 用户名@服务器IP`。
3. 以后每次上架：`bash 部署.sh`（或让工作室执行 `/publish` 自动跑）。

## 三、域名与 HTTPS（买好域名后）

1. 阿里云万网买域名（建议 .com / .me，名字让老板参与起！）。
2. 域名解析 → 添加 A 记录：`@` 和 `www` 都指向服务器公网 IP。
3. 服务器上装免费证书（Let's Encrypt 一条命令）：

   ```bash
   yum install -y certbot python3-certbot-nginx   # Ubuntu 用 apt
   certbot --nginx -d 你的域名 -d www.你的域名
   ```

4. 把 nginx 配置里的 `server_name` 换成域名，reload。从此 HTTPS 自动续期。

## 四、GitHub 版本管理（2026-10-14 起）

这个文件夹本身就是一个 git 仓库，远端是 **https://github.com/danchaofan/pipiai.top**（用 SSH 推送，本机 HTTPS 连 GitHub 不稳定）。

- 服务器地址在 `部署配置` 里，已被 `.gitignore` 挡住，永远不会上传；仓库里只留 `部署配置.example` 模板。
- 每次上架新游戏或改版后：`git add -A && git commit -m "说明" && git push`，网站每次进化都有存档可查。
- 仓库内容 = 网站文件夹里除被忽略文件外的全部（首页、数据、封面、游戏、部署工具）。

## ⚠️ 隐私与安全红线

- 网站署名只用**工作室名/昵称**，不放真实姓名、学校、住址、生活照片。
- `部署配置` 含服务器信息，不要拷给别人、不要传到公开仓库。
- 备案：国内服务器绑域名需 ICP 备案（阿里云上有引导流程，约 1~2 周）；备案期间可先用 IP 访问。
