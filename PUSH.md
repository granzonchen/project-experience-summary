# 推送指引（HTTPS + Personal Access Token）

本仓库已初始化并完成本地提交。以下步骤需要你手动执行（涉及 GitHub 授权）。

## 1. 创建 GitHub 仓库

1. 打开 https://github.com/new
2. Repository name：`project-experience-summary`
3. 选择 Public 或 Private
4. **不要**勾选 "Add a README"（本地已有）
5. 点击 Create repository

## 2. 生成 Personal Access Token

1. GitHub 右上角头像 → Settings
2. 左侧 Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. 勾选 `repo` 权限（完整仓库读写）
5. 生成后**立即复制**（只显示一次），妥善保管

## 3. 本地关联并推送

在 PowerShell 中执行（注意命令中的占位符）：

```powershell
git -C D:\projects\project-experience-summary remote add origin https://github.com/granzonchen/project-experience-summary.git
git -C D:\projects\project-experience-summary push -u origin main
```

- 首次推送会弹出凭据窗口（Git Credential Manager）
- 用户名填 `granzonchen`，密码处**粘贴 Token**（不是 GitHub 登录密码）
- 成功后 Token 由 Git for Windows 自动存入 Windows 凭据管理器，后续 `git push` 无需再输入

## 4. 后续更新流程

```powershell
# 有新文档时
git -C D:\projects\project-experience-summary add .
git -C D:\projects\project-experience-summary commit -m "docs: 更新xxx"
git -C D:\projects\project-experience-summary push
```

## 安全注意

- Token 只在首次推送时粘贴一次，不要写入任何文件或文档
- 若 Token 泄露：GitHub Settings → Developer settings → Tokens → Revoke 即可
- 本仓库只包含 Markdown 总结文档，不含任何项目源码，可放心公开
