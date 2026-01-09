# Cloudflare 域名接入指南 (针对 bmwuv.com)

目前的报错 `Error 1001: DNS resolution error` 表示 Cloudflare 无法识别你的域名。这是因为你可能还没有在 Cloudflare 账号中添加该域名，或者虽然添加了但还没有完成 DNS 服务器的修改验证。

请严格按照以下步骤操作：

## 第一步：在 Cloudflare 添加域名

1.  **注册/登录**: 访问 [dash.cloudflare.com](https://dash.cloudflare.com/) 并登录你的账号。
2.  **添加站点**: 点击右上角的 **"Add a site" (添加站点)** 按钮。
3.  **输入域名**: 输入 `bmwuv.com`，然后点击 **"Continue" (继续)**。
4.  **选择套餐**: 滚动到底部，选择 **"Free" (免费版)** 套餐（通常在最下面），然后点击 **"Continue"**。
5.  **DNS 扫描**: Cloudflare 会自动扫描你现有的 DNS 记录。扫描完成后，点击 **"Continue"**。

## 第二步：获取 Cloudflare 的名称服务器 (Nameservers)

在接下来的页面中，Cloudflare 会提示你需要修改 Nameservers。它会给你两个地址，看起来像这样（注意：**这是我屏幕上真实显示的**）：
*   corey.ns.cloudflare.com
*   margaret.ns.cloudflare.com
*   **请复制这两个地址。**

## 第三步：在阿里云修改 DNS 服务器

1.  登录 [阿里云域名控制台](https://dc.console.aliyun.com/)。
2.  找到域名 `bmwuv.com`，点击 **"管理"**。
3.  在左侧菜单或概览页中找到 **"DNS修改"** 或 **"修改DNS服务器"**。
4.  选择 **"修改DNS服务器"**。
5.  将现有的阿里云 DNS（如 `dns1.hichina.com` 等）**全部删除**。
6.  填入你在 **第二步** 中获取的那两个 Cloudflare 地址。
7.  点击 **"保存"**。

## 第四步：在 Cloudflare 配置 DNS 解析 (指向你的服务器)

1.  回到 Cloudflare 控制台，点击 **"Done, check nameservers"**。
2.  等待生效（通常几分钟到几小时）。当你在 Cloudflare 首页看到域名状态变为 **"Active" (绿色)** 时，说明接入成功。
3.  进入该域名的 **DNS** 设置页面。
4.  点击 **"Add record" (添加记录)**，添加以下两条记录，将你的域名指向你的云服务器 IP：

    *   **记录 1 (根域名)**:
        *   Type (类型): `A`
        *   Name (名称): `@`
        *   Content (内容): `你的云服务器公网IP` (例如: 123.45.67.89)
        *   Proxy status (代理状态): 开启 (橙色云朵) -> 这样才有 CDN 和防护。
        *   TTL: Auto

    *   **记录 2 (www 子域名)**:
        *   Type (类型): `CNAME`
        *   Name (名称): `www`
        *   Content (内容): `bmwuv.com`
        *   Proxy status (代理状态): 开启 (橙色云朵)
        *   TTL: Auto

## 第五步：配置 SSL/TLS (解决 HTTPS 问题)

微信小程序强制要求 HTTPS。使用 Cloudflare 后，设置非常简单：

1.  在 Cloudflare 左侧菜单点击 **"SSL/TLS"**。
2.  将加密模式设置为 **"Full" (完全)** 或 **"Full (strict)"**。
    *   **Flexible (灵活)**: ❌ 不要在小程序后端使用，容易导致重定向循环。
    *   **Full (完全)**: ✅ 推荐。你需要服务器上配置一个自签名证书（甚至不需要是有效的，只要有证书即可）。
    *   **Full (strict)**: 🌟 最佳。需要服务器上配置有效的证书（如 Let's Encrypt）。

## 验证
完成上述步骤后，等待 10-30 分钟，再次访问 `http://bmwuv.com/`，你应该能看到你的网站（或 Nginx 的欢迎页），而不再是 1001 错误。
