# WeChat HelloWorld Bot

这是一个简单的微信公众号后端示例，使用 Python Flask 实现，部署于 Vercel。

## 功能
- 任何用户消息都回复“HelloWorld”

## 部署
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 本地运行：
   ```bash
   python api.py
   ```
3. 部署到 Vercel：
   - 确保 `vercel.json` 配置正确。
   - 推送代码到 Vercel 关联仓库。

## 目录结构
- api.py：主程序
- requirements.txt：依赖
- vercel.json：Vercel 配置

## 备注
- 需在微信公众平台配置服务器地址，指向 Vercel 部署的 URL。
