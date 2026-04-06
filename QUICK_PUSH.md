# 🚀 快速推送指南

---

## ⚠️ 网络代理问题

你的 Git 推送失败是因为系统配置了代理（端口 1080）。

**解决方案**:

### 方法 1: 临时禁用代理（推荐）

```bash
cd E:\Quant_Production

# 禁用代理
git config --global http.proxy ""
git config --global https.proxy ""

# 推送
git push -u origin main --force
```

### 方法 2: 使用 SSH（如果已配置）

```bash
# 改用 SSH 地址
git remote set-url origin git@github.com:wanming-ss/quant-production.git

# 推送
git push -u origin main --force
```

### 方法 3: 手动在 GitHub Desktop 推送

1. 打开 GitHub Desktop
2. File → Add Local Repository → 选择 `E:\Quant_Production`
3. 点击 Push origin

---

## 📝 完整推送命令（复制执行）

### Windows PowerShell

```powershell
# 1. 进入目录
cd E:\Quant_Production

# 2. 禁用代理
git config --global http.proxy ""
git config --global https.proxy ""

# 3. 设置远程仓库
git remote remove origin 2>$null
git remote add origin https://github.com/wanming-ss/quant-production.git

# 4. 重命名分支
git branch -M main

# 5. 推送（会提示输入 GitHub 用户名和密码）
git push -u origin main --force
```

---

## 🔐 GitHub 认证

### 使用 Personal Access Token (PAT)

当 Git 提示输入密码时，**不要输入 GitHub 密码**，而是使用 Token：

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 填写：
   - **Note**: `quant-production`
   - **Expiration**: `No expiration`
   - **Select scopes**: 勾选 `repo` (Full control of private repositories)
4. 点击 **Generate token**
5. **复制 Token**（只显示一次！）
6. Git 提示密码时，粘贴这个 Token

---

## ✅ 验证推送成功

推送成功后，访问：
https://github.com/wanming-ss/quant-production

你应该能看到所有文件！

---

## 📊 预期输出

```
Enumerating objects: 180, done.
Counting objects: 100% (180/180), done.
Delta compression using up to 8 threads
Compressing objects: 100% (150/150), done.
Writing objects: 100% (180/180), 1.25 MiB | 2.50 MiB/s, done.
Total 180 (delta 0), reused 0 (delta 0), pack-reused 0
remote:
remote: Create a pull request for 'main' on GitHub by visiting:
remote:      https://github.com/wanming-ss/quant-production/pull/new/main
remote:
To https://github.com/wanming-ss/quant-production.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## 🎉 推送后的下一步

### 1. 更新 README

编辑 README.md，将 `YOUR_USERNAME` 替换为 `wanming-ss`

### 2. 创建 Release

1. 访问：https://github.com/wanming-ss/quant-production/releases/new
2. Tag: `v1.0.0`
3. Title: `AI-Native Quant Framework v1.0.0`
4. 复制 `.github/RELEASE_TEMPLATE.md` 内容
5. 点击 **Publish release**

### 3. 配置 GitHub Pages（可选）

1. Settings → Pages
2. Source: `main` branch
3. 保存

---

## 📞 遇到问题？

### 问题：认证失败

**解决**: 使用 Personal Access Token，不要使用密码

### 问题：仍然提示代理错误

**解决**: 
```bash
# 检查代理配置
git config --global --list | findstr proxy

# 删除所有代理配置
git config --global --unset http.proxy
git config --global --unset https.proxy
git config --global --unset http.sslVerify
```

### 问题：权限错误

**解决**: 确认你是仓库所有者或有推送权限

---

> **提示**: 如果命令行推送困难，可以使用 **GitHub Desktop** 图形化工具！
