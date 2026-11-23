# X 视频下载器（iPhone 网页版）

## 部署
1. 将整个项目文件夹上传到你自己的 GitHub 仓库。
2. 在 Render 创建 Web Service，连接该仓库。
3. Render 通常可自动识别 `render.yaml`；若手动配置：
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. 部署完成后，用 iPhone Safari 打开 Render 提供的网址。

## iPhone 添加到主屏幕
Safari 打开网址 → 分享 → 添加到主屏幕。

## 重要说明
- 需要部署到有 Python、yt-dlp 和 ffmpeg 的服务器；单独打开 HTML 文件不能完成视频解析。
- 仅支持无需登录即可公开访问、且你有权保存的视频。不会绕过私密账号、登录、付费或其他访问限制。
- X 可能随时调整页面或媒体机制，解析成功率不作保证；请保持 yt-dlp 更新。
- 下载大文件会占用服务器临时磁盘与流量。正式公开运营前应增加速率限制、文件清理、请求大小限制和滥用防护。
- 下载到 iPhone 后，可从 Safari 下载列表打开文件，再使用分享菜单保存到「照片」。
