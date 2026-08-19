# D:\projects 项目经验总结

本仓库沉淀 `D:\projects` 下开发项目的经验总结：技术栈、架构亮点、踩坑记录、可复用模式与改进建议。**仅包含总结文档，不含任何项目源码**。

## 深度分析项目

| 项目 | 文档 | 类型 | 核心经验 |
|---|---|---|---|
| GoView 大屏可视化编辑器 | [projects/go-view.md](projects/go-view.md) | Vue3 低代码大屏编辑器（二次开发） | 配置化组件注册体系、操作记录式撤销、数据池订阅、参数改写联动 |
| lx-mes + lx-mes-screen | [projects/lx-mes.md](projects/lx-mes.md) | MES 制造执行系统全栈（Java + Vue2 大屏） | 聚合接口 + 并行查询、看板缓存 DTO、防重复提交三件套 |
| 昌威交通 2.0（cwjt + cwjt_front） | [projects/cwjt.md](projects/cwjt.md) | MOM 云平台（Spring Boot 3 + Vue3 monorepo） | 单体多数据源 AOP 路由、401 令牌刷新队列、后端驱动路由、交接文档工作流 |
| patent-disclosure-skill | [projects/patent-disclosure-skill.md](projects/patent-disclosure-skill.md) | 专利交底书 AI Agent Skill | 提示词工程门禁/锚点、Agent 输出契约、反幻觉具体规则、失败降级哲学 |
| 其余 39 个项目概况 | [projects/overview.md](projects/overview.md) | 快速摸底 | 技术栈分类与项目间关联 |

## 技术栈矩阵

| 领域 | 项目 | 技术栈 |
|---|---|---|
| 大屏可视化 | go-view | Vue3 + Vite + TS + ECharts + naive-ui |
| 大屏可视化 | lx-mes-screen | Vue2 + ECharts + DataV + autofit |
| MOM/MES 后端 | lx-mes | Spring Boot 2.3 + Cloud + MyBatis-Plus + JeecgBoot 封装 |
| MOM/MES 后端 | cwjt | Spring Boot 3.3 + OAuth2 + MyBatis-Plus + dynamic-datasource |
| MOM/MES 前端 | cwjt_front | Vue3.5 + Vite6 + pnpm monorepo + Element Plus（vben-admin 蓝本） |
| MOM 体系前端（多项目） | hcmom / hexconn / card-mode / changwei / baorun / device-job-management-pc-end | Vue + JeecgBoot 系 |
| WMS 移动端 | jt-app / lx-wms-app / lx-wms-app-dev / vue_app | Vue H5（wms-phone-app 系） |
| 管理后台 | medical-ui / qdkj-operate | Vue3 + Ant Design Vue |
| AI/Agent | patent-disclosure-skill | Python + Playwright + AgentSkill 规范 |
| 移动端原生 | flutter / hw_test（鸿蒙）/ uniapp | Flutter / ArkTS / uni-app |
| 学习实验 | java / js / python / R / react / go | 多语言示例 |

## 高频经验标签（跨项目）

- **低代码/可视化搭建**：配置化组件注册（go-view）、聚合接口 + 看板缓存（lx-mes）、大屏 4 种缩放模式
- **大屏项目通病与对策**：定时器泄漏 → visibility 暂停 + 单定时器；echarts 实例泄漏 → getInstanceByDom || init；客户端时钟漂移 → 服务器时间接口 + fallback；接口失败空白 → 重试 + 空数据兜底
- **高并发制造场景**：防重复提交注解 + 分布式锁 + 事务事件解耦（lx-mes）；报工聚合更新需乐观锁
- **多库/多租户**：单体多数据源 AOP 包路由（cwjt）；多工厂租户硬编码是坑
- **前端工程化**：pnpm catalog 统一版本 + turbo 缓存；commitlint + husky 全链路；Mock 先行验收工作流
- **智能体/提示词工程**：执行门禁 + 强制输出锚点 + 反幻觉具体规则（patent-disclosure-skill）
- **部署/发布**：单体 fat-jar 构建陷阱（repackage/嵌套 BOOT-INF）；构建产物自检纳入 CI

## 目录结构

```
project-experience-summary/
├── README.md                      # 本文件
├── projects/
│   ├── go-view.md                 # 深度文档 ×4
│   ├── lx-mes.md
│   ├── cwjt.md
│   ├── patent-disclosure-skill.md
│   └── overview.md                # 其余项目概况
└── PUSH.md                        # 推送指引
```

## 说明

- 分析基于截至 2026-08 的代码与 git 历史，均为只读勘察
- 部分项目涉及公司业务（lx-mes / cwjt / hexconn 等），本仓库只保留经验总结，不包含业务数据与源码
- 深度文档中标注的改进建议为静态分析结论，实际优先级请结合业务判断
