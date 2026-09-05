# Project Experience Summary 进度记录

> 更新时间：2026-09-05
> 仓库：`D:\projects\project-experience-summary` ↔ `https://github.com/granzonchen/project-experience-summary`

---

## ✅ 已完成（projects-old 归档项目群，2026-09-05）

| # | 产出 | 说明 |
|---|---|---|
| 0 | `METHOD.md` | **经验提炼方法论本体**：证据链原则、三层漏斗、迁移性三档（金/留/弃）、复盘五段模板、规则准入门槛、沉淀分流表、质量自检清单 |
| 1 | `projects/cevt.md` | Odoo 10→14 车队套件：升级 checklist codify、迁移钉 commit hash、依赖即 CI 门禁、单仓大爆炸 |
| 2 | `projects/ltc.md` | 物流 Odoo+多端：ERP 集成中枢、超时重试踩坑后补、整仓复制国际化、0 tag 快照灾难、注释当开关 |
| 3 | `projects/django-vue-admin-pro.md` | Django+Vue RBAC 脚手架：权限三正交面、鉴权只信服务端、数据权限声明即生效、缩进层修复≠生效 |
| 4 | `projects/dawei-dw.md` | 复制改造样本：删减三步验收、框架零污染、格式化清噪、路径寄生脚本、VCS 三重失守 |
| 5 | `projects/odoo-industry.md` | lims/xinyi/odoo14addons/rfmt 对照：依赖治理三级分化、_ext 包裹、审批配置化与全局补丁 |
| 6 | `projects/fork-dashboard.md` | antai/antaidaping：后端复用+前端新仓、ext 两种语义、对内接口默认拒绝 |
| 7 | `projects/gov-screen-gis.md` | 政务大屏/GIS：敏感数据随交付物滞留（PII）、树节点=图层、副本当版本管理 |
| 8 | `projects/miniapp-cluster.md` | 模板化移动端：该沉淀的是 API 封装层、无增量提交的复制迭代、低价值项目判据 |
| 9 | `LEGACY_LESSONS.md` | **R-13~R-21 共 9 条跨项目规则**（复制改造纪律/VCS 唯一出处/依赖门禁/配置模板化/敏感态三形态/外部集成三件套/权限三正交面/测试资产/双源对账），GLOBAL_RULES 已加指向 |

> 隐私处置：8 篇复盘对敏感信息零复制，只记位置与类型（api.md PII、各项目明文口令、k8s secrets 等已逐一定位，处置建议见各篇"证据索引"末节）。

---

## ✅ 已完成（6 个深度分析）

| # | 项目 | 文档 | 关键标签 | 提交 |
|---|---|---|---|---|
| 1 | **go-view** | `projects/go-view.md` | Vue3 大屏编辑器、配置化组件注册、操作记录式撤销、数据池订阅、23 个踩坑 | `1c473fc` |
| 2 | **lx-mes + lx-mes-screen** | `projects/lx-mes.md` | MES 全栈、聚合接口+并行查询、看板缓存 DTO、防重复三件套、假读写分离 | `1c473fc` |
| 3 | **cwjt + cwjt_front** | `projects/cwjt.md` | MOM 云平台、单体多数据源 AOP 路由、401 令牌刷新队列、后端驱动路由、交接文档工作流 | `1c473fc` |
| 4 | **patent-disclosure-skill** | `projects/patent-disclosure-skill.md` | 专利交底书 AI Skill、提示词门禁/锚点、Agent 输出契约、反幻觉规则、失败降级 | `1c473fc` |
| 5 | **jiateng-pc** | `projects/jiateng-pc.md` | 佳腾 MOM 平台、声明式列表 Mixin、v-has 权限表达式、9 副本架构灾难、硬编码密钥/假读写分离 | `abdc4e3` |
| 6 | **jt-app** | `projects/jt-app.md` | 嘉腾生产管理 uni-app、PDA 扫码三件套、PageMixin 分页状态机、多租户动态菜单、P0 级登出崩溃 | `b7aebbd` |

---

## 📋 索引文档

| 文件 | 说明 |
|---|---|
| `README.md` | 总索引、技术栈矩阵、6 大高频经验标签 |
| `projects/overview.md` | 其余 37 个项目概况清单 |
| `PUSH.md` | HTTPS + PAT 推送指引 |

---

## 🔗 项目关联洞察

- **JeecgBoot 体系同源**：lx-mes、jiateng-pc、card-mode、hcmom、hexconn、changwei、baorun、device-job-management-pc-end 均为东珥 donger-mom-* 变体
- **wms-phone-app 模板系**：jt-app、lx-wms-app、lx-wms-app-dev、vue_app 同源
- **两代架构对照**：cwjt（Vue3 monorepo 重写）vs jiateng-pc（Vue2 JeecgBoot 旧栈）
- **共性坑**：硬编码密钥、假读写分离、多副本同步、返回码不统一、无规范链、构建产物未自检

---

## 📍 待分析候选（其余 37 个）

### 高价值优先
| 项目 | 类型 | 理由 |
|---|---|---|
| **hcmom** | MOM 前端 + graphify-out | 有知识图谱产物，疑似已做过架构分析 |
| **medical-ui** | 管理后台（vben-admin） | Vue3 + Ant Design Vue，规范较新 |
| **qdkj-operate-master-master** | 石化运营大屏 | Vue + Ant Design Vue + ECharts，可视化经验互补 |
| **hengyi-mall** | 电商（DongerShop） | donger-plus 体系，商城业务对比 MOM |
| **flutter** | 移动端（充电桩等） | Flutter 原生跨端，技术栈互补 |
| **uniapp/odoo** | uni-app + odoo | ERP 集成场景 |
| **hexconn / card-mode** | MOM 前端 | donger-mom 变体，可补全 JeecgBoot 体系图谱 |

### 其他
- vue_app / vue_front_project / app（WMS 移动端变体）
- baorun（宝润 MOM 云平台）
- changwei（昌威前身）
- JeecgBoot（开源框架源码）
- device-job-management-pc-end / hexconn-project-delivery
- react / python / R / java / js / go（学习/实验类）

---

## 📝 下一步建议

新对话启动时直接说：
> 继续 project-experience-summary 任务，分析 D:\projects\hcmom（或其他候选）

或：
> `/resume` 读取此文件续接

---

## 🔐 GitHub 推送凭据

- 用户名：`granzonchen`
- 当前 Token：已存入 Windows 凭据管理器（`git:https://github.com`）
- 如需轮换：GitHub Settings → Developer settings → Tokens → 删除旧 → 生成新 → 粘贴给助手执行 `cmdkey /generic:git:https://github.com /user:granzonchen /pass:<新token>`