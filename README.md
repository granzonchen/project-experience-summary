# D:\projects 项目经验总结

本仓库沉淀 `D:\projects` 下开发项目的经验总结：技术栈、架构亮点、踩坑记录、可复用模式与改进建议。**仅包含总结文档，不含任何项目源码**。

## 深度分析项目

| 项目 | 文档 | 类型 | 核心经验 |
|---|---|---|---|
| GoView 大屏可视化编辑器 | [projects/go-view.md](projects/go-view.md) | Vue3 低代码大屏编辑器（二次开发） | 配置化组件注册体系、操作记录式撤销、数据池订阅、参数改写联动 |
| lx-mes + lx-mes-screen | [projects/lx-mes.md](projects/lx-mes.md) | MES 制造执行系统全栈（Java + Vue2 大屏） | 聚合接口 + 并行查询、看板缓存 DTO、防重复提交三件套 |
| 昌威交通 2.0（cwjt + cwjt_front） | [projects/cwjt.md](projects/cwjt.md) | MOM 云平台（Spring Boot 3 + Vue3 monorepo） | 单体多数据源 AOP 路由、401 令牌刷新队列、后端驱动路由、交接文档工作流 |
| patent-disclosure-skill | [projects/patent-disclosure-skill.md](projects/patent-disclosure-skill.md) | 专利交底书 AI Agent Skill | 提示词工程门禁/锚点、Agent 输出契约、反幻觉具体规则、失败降级哲学 |
| 佳腾 MOM 平台（jiateng-pc） | [projects/jiateng-pc.md](projects/jiateng-pc.md) | MOM 平台（Spring Boot 2.3 + Vue2 JeecgBoot 系） | 声明式列表页体系、v-has 权限表达式、9 副本架构教训、假读写分离 |
| jt-app（生产管理 App） | [projects/jt-app.md](projects/jt-app.md) | uni-app PDA 移动端（WMS+MES+QMS+TPM） | PDA 扫码三件套、PageMixin 分页状态机、多租户动态菜单、wgt 热更新 |
| agent-hub（本地多智能体枢纽） | [projects/agent-hub.md](projects/agent-hub.md) | 多智能体调度（Python + 文件协议 + 7×L2 执行方） | 文件协议四落点、机械化验收拦截假完成、CLI 直调真身、配置漂移启动前校验 |
| 其余 37 个项目概况 | [projects/overview.md](projects/overview.md) | 快速摸底 | 技术栈分类与项目间关联 |

### projects-old 归档项目群（2020~2024，Odoo/Python/Django/uni-app 时代）

| 项目群 | 文档 | 类型 | 核心经验 |
|---|---|---|---|
| cevt | [projects/cevt.md](projects/cevt.md) | Odoo 10→14 车队管理套件（77+ 自研 addon） | 升级 checklist codify 成脚本、迁移钉 commit hash、依赖即 CI 门禁、批量导入收集-汇总-抛错 |
| ltc | [projects/ltc.md](projects/ltc.md) | Odoo 13 物流服务 + 多端前端 | ERP 作集成中枢、外部依赖显式超时重试、整仓复制做国际化的代价、0 tag 的快照灾难 |
| django-vue-admin-pro | [projects/django-vue-admin-pro.md](projects/django-vue-admin-pro.md) | Django+Vue 全栈 RBAC 脚手架 | 权限三正交面分表、鉴权只信服务端、数据权限声明即生效、配置缩进层修复≠生效 |
| dawei + dw | [projects/dawei-dw.md](projects/dawei-dw.md) | Django 复制改造样本（对照盘） | 复制裁剪三步验收、框架零污染二开、格式化清噪、路径寄生脚本 |
| Odoo 行业系 ×4 | [projects/odoo-industry.md](projects/odoo-industry.md) | LIMS/校服/通用件/煤炭 MRP | 依赖治理三级分化、_ext 包裹不改上游、审批配置化与全局补丁之弊 |
| antai / antaidaping | [projects/fork-dashboard.md](projects/fork-dashboard.md) | Odoo 制造 + uni-app 大屏（对照 ltc/hn_mall） | 后端复用+前端新仓分工、同名为 ext 两种语义、对内接口也要默认拒绝 |
| zhsq + gis | [projects/gov-screen-gis.md](projects/gov-screen-gis.md) | 政务大屏/GIS 单文件交付 | 树节点=图层=接口参数、敏感数据随交付物滞留（PII 教训）、副本当版本管理 |
| 移动端模板集群 ×6 | [projects/miniapp-cluster.md](projects/miniapp-cluster.md) | uni-app/小程序模板化开发 | 真正该沉淀的是 API 封装层而非 UI 组件、无增量提交的复制迭代不可追溯 |
| flutter 工作区 ×6 | [projects/flutter-workspace.md](projects/flutter-workspace.md) | Flutter/RN（充电桩/ThingsBoard/BLE 配网/PDA，2023） | 同平台三客户端三依赖约束、副本对漂移只发生在业务层、官方 App 二开三件套（URL 可配/本地存储/修登录）、构建产物磁盘残留 ≠ 仓库膨胀 |
| python 工具工作区 ×8 | [projects/python-workspace.md](projects/python-workspace.md) | Python 胶水脚本（TB/Odoo/MES 生态 + 抖音获客 + APS 排产） | 活跃工具与归档混放是治理温床、共享代码靠复制传播、venv 占 93% 体积、git-less 工具的能跑状态是 exe |
| vue_front_project ×22 | [projects/vue_front_project.md](projects/vue_front_project.md) | 前端项目群（F023 大屏 + go-view 双副本 + Node 后端 + 商城，2019~2024） | 能演示≠能上线（mockup 交付）、认证形同虚设三连、同需求两套实现、git 盲区藏活凭据、含知识图谱与跨工作区挂接 |

## 技术栈矩阵

| 领域 | 项目 | 技术栈 |
|---|---|---|
| 大屏可视化 | go-view | Vue3 + Vite + TS + ECharts + naive-ui |
| 大屏可视化 | lx-mes-screen | Vue2 + ECharts + DataV + autofit |
| MOM/MES 后端 | lx-mes | Spring Boot 2.3 + Cloud + MyBatis-Plus + JeecgBoot 封装 |
| MOM/MES 后端 | cwjt | Spring Boot 3.3 + OAuth2 + MyBatis-Plus + dynamic-datasource |
| MOM/MES 前端 | cwjt_front | Vue3.5 + Vite6 + pnpm monorepo + Element Plus（vben-admin 蓝本） |
| MOM 平台（佳腾） | jiateng-pc | Spring Boot 2.3 + Vue2 + JeecgBoot（donger-mom 体系） |
| MOM 体系前端（多项目） | hcmom / hexconn / card-mode / changwei / baorun / device-job-management-pc-end | Vue + JeecgBoot 系 |
| WMS 移动端 | jt-app（已深度）/ lx-wms-app / lx-wms-app-dev / vue_app | uni-app / Vue H5（wms-phone-app 系） |
| 管理后台 | medical-ui / qdkj-operate | Vue3 + Ant Design Vue |
| AI/Agent | patent-disclosure-skill | Python + Playwright + AgentSkill 规范 |
| 移动端原生 | flutter / hw_test（鸿蒙）/ uniapp | Flutter / ArkTS / uni-app |
| 学习实验 | java / js / python / R / react / go | 多语言示例 |
| **归档·Odoo 生态** | cevt / ltc / lims / xinyi / antai / rfmt / odoo14addons | Odoo 10/13/14 + Python + PostgreSQL + Nginx/Docker/k8s |
| **归档·Python 全栈** | django-vue-admin-pro / dawei / dw / zhsq | Django + DRF + Vue2 + MySQL + Docker Compose |
| **归档·多端小程序** | mms-wmp 系 / hn_mall 系 / maintenance 系 | uni-app(Vue2) / 微信原生 + ThorUI / ColorUI |
| **归档·前端项目群** | vue_front_project（fj_daping / go-view×2 / led / shop_demo_1 / 参考×6） | Vue2/Vue3 + datav + echarts + uni-app + express/sequelize |
| **归档·Flutter/RN 工作区** | flutter/（charger / tb_app_fj / feng-ji×2 / migan / warehouse_pda） | Flutter 2.12~3.7 + GetX + RN 0.63 + ThingsBoard/Odoo/Google Maps |

## 高频经验标签（跨项目）

- **低代码/可视化搭建**：配置化组件注册（go-view）、聚合接口 + 看板缓存（lx-mes）、大屏 4 种缩放模式
- **大屏项目通病与对策**：定时器泄漏 → visibility 暂停 + 单定时器；echarts 实例泄漏 → getInstanceByDom || init；客户端时钟漂移 → 服务器时间接口 + fallback；接口失败空白 → 重试 + 空数据兜底
- **高并发制造场景**：防重复提交注解 + 分布式锁 + 事务事件解耦（lx-mes）；报工聚合更新需乐观锁
- **多库/多租户**：单体多数据源 AOP 包路由（cwjt）；多工厂租户硬编码是坑；假读写分离（master/slave 同库）要自查
- **JeecgBoot 系工程**：声明式列表 Mixin + v-has 权限表达式（jiateng-pc）；前端多副本同步是维护灾难，应收敛 monorepo
- **安全**：密钥/DB 密码硬编码入仓需立即治理；请求签名（X-Sign）防篡改可复用
- **前端工程化**：pnpm catalog 统一版本 + turbo 缓存；commitlint + husky 全链路；Mock 先行验收工作流
- **智能体/提示词工程**：执行门禁 + 强制输出锚点 + 反幻觉具体规则（patent-disclosure-skill）
- **PDA/移动端**：扫码三件套（可配置广播 + 全局事件成对 on/off + 防抖）、扫码值上下文校验、PageMixin 分页状态机、wgt 热更新、弱网离线草稿（jt-app）
- **部署/发布**：单体 fat-jar 构建陷阱（repackage/嵌套 BOOT-INF）；构建产物自检纳入 CI
- **复制改造纪律（归档时代教训）**：改造点清单化 + 删减三步验收 + 副本 diff 门禁；语言/环境差异用构建变量不用整仓副本；可运行状态唯一出处是 VCS（tag），副本/快照/dump 不是版本管理
- **插件/依赖治理（归档时代教训）**：来源清单 + 装前机器校验 + _ext 叠层不改上游 + 仓库按 platform/business/customer 分层
- **敏感态三形态同治**：密钥入仓、PII 随交付物滞留、抓包/快照与代码同目录——归档前强制脱敏清单
- **外部集成三件套**：显式超时+重试、外部写不进主事务、外部身份约定配置化且无匹配告警
- **权限三正交面**：页面可见/接口可调/数据行可见分表建模；鉴权只信服务端；权限回归断言可见行数

## 目录结构

```
project-experience-summary/
├── README.md                      # 本文件
├── METHOD.md                      # 项目经验提炼方法论（复盘标尺）
├── GLOBAL_RULES.md                # 跨项目全局经验规则 R-01~R-12
├── LEGACY_LESSONS.md              # 归档时代跨项目规则 R-13~R-21
├── projects/
│   ├── go-view.md                 # 深度文档 ×6（活跃项目）
│   ├── lx-mes.md
│   ├── cwjt.md
│   ├── patent-disclosure-skill.md
│   ├── jiateng-pc.md
│   ├── jt-app.md
│   ├── overview.md                # 其余项目概况
│   ├── cevt.md                    # 归档项目群 8 篇 ↓
│   ├── ltc.md
│   ├── django-vue-admin-pro.md
│   ├── dawei-dw.md
│   ├── odoo-industry.md
│   ├── fork-dashboard.md
│   ├── gov-screen-gis.md
│   ├── miniapp-cluster.md
│   └── vue_front_project.md       # 前端项目群复盘（画像+技术深读+知识图谱）
└── PUSH.md                        # 推送指引
```

## 全局通用规则

- [GLOBAL_RULES.md](GLOBAL_RULES.md)：12 条跨项目强制规则（提交规范/密钥零明文/构建自检/Monorepo/请求四件套/大屏对策/追溯校验/数据库版本控制/Mock 先行/交接续接/JeecgBoot 锁版本），编号 R-01~R-12 便于引用
- [LEGACY_LESSONS.md](LEGACY_LESSONS.md)：R-13~R-21 共 9 条，提炼自 projects-old 归档项目群 8 篇复盘（复制改造纪律/VCS 唯一出处/依赖门禁/配置模板化/敏感态三形态/外部集成三件套/权限三正交面/测试资产/双源对账）
- [METHOD.md](METHOD.md)：经验提炼方法论——三层漏斗、迁移性三档判断（金/留/弃）、复盘模板与规则准入门槛，后续所有复盘按此标尺执行

## 说明

- 分析基于截至 2026-08 的代码与 git 历史，均为只读勘察
- 部分项目涉及公司业务（lx-mes / cwjt / hexconn 等），本仓库只保留经验总结，不包含业务数据与源码
- 深度文档中标注的改进建议为静态分析结论，实际优先级请结合业务判断

## 推送门禁与脱敏约定（2026-09-12）

本仓库有**两个远端**：`origin` = GitHub（**公开**）、`gitee` = Gitee（私有）——**两者都视为公开可见面**。

- **写什么**：项目经验、技术细节、方法论（含客户/项目名，系本仓内容本体，已确认可公开）
- **不写什么**：**凭据**（口令 / token / key / 私钥 / 带账号连接串）、**内网与部署地址**（RFC1918、IP:端口、内网域名）、以及任何运行时数据

**推送前门禁**（已启用：`git config core.hooksPath .githooks`）：

```bash
node scripts/publish-audit.mjs [ref]    # 手动体检（默认 HEAD）；命中即退出码 1
```

`.githooks/pre-push` 会在推送每个分支前自动跑同一套规则，**命中即拒绝推送**（9 条规则：sk- 密钥 / GitHub PAT / AWS AK / 私钥块 / 带账号连接串 / 口令赋值 / RFC1918 / 非回环 IP:端口 / 内网域名）。

> 地址类信息一律写成占位符（如 `<DB_HOST>:<DB_PORT>`）或用环境变量注入；**不要在说明/记录里复述原值**（复述 = 没脱敏）。
> 历史曾含内网地址，已于 2026-09-12 用 `git filter-repo --replace-text` 重写并强推；备份见 `project-experience-summary-full-backup-20260912.bundle`（仓库同级目录）。
