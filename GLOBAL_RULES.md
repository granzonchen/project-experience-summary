# 跨项目全局经验规则沉淀（2026-08）

> 基于 D:\projects 下 6 个深度分析项目（lx-mes、cwjt、jiateng-pc、jt-app、go-view、patent-disclosure-skill）的 git 历史、代码结构、踩坑记录提炼。
> 适用范围：东珥科技 donger-mom 体系（lx-mes/jiateng-pc/hcmom/hexconn/card-mode）、同团队维护项目、JeecgBoot 系 MOM 类项目。

---

## 一、提交与协作规范

### 1.1 提交信息必须规范化（全项目通病）

**现状**：
- jiateng-pc: `FEAT:/FIX:/fix:/feat:/Merge/fix/feat` 混用，无 scope，无 body
- lx-mes: 早期同质混乱，后期 `feat(mes):` 规范化
- cwjt: `feat(mes):` / `fix(bigscreen):` 规范化

**规则**：
```
<type>(<scope>): <subject>
# type: feat | fix | refactor | style | docs | test | chore | perf | revert
# scope: 模块名(mes/wms/qms/tpm/pln/qrc/mdm/retrospect/all/bigscreen/pad/app)
# subject: 动词开头，50字以内，说明"做了什么/为什么"
```

**强制要求**：
- 所有项目接入 `commitlint + husky + lint-staged`（已在 cwjt 落地，其余需补）
- MR/CR 强制检查提交格式，不合规拦截

### 1.2 核心贡献者保护与知识传递

**数据**：
- lx-mes: wuyu 43% 贡献，团队 4 人贡献 80%+ → **单点风险极高**
- jiateng-pc: guopeng 46%，团队 15+ 人但长尾分散
- jt-app: guopeng/SYF 跨项目维护

**规则**：
- 核心模块（报工、排产、追溯、大屏、条码）必须有 ≥2 人熟悉
- 核心人员离职/转岗前 2 周完成《模块交接清单》：核心流程图、关键 SQL、配置依赖、已知坑
- 关键文件（>2000 行、核心业务 Service、复杂算法）必须有设计文档/代码注释

---

## 二、代码质量与技术债红线

### 2.1 绝对禁止项（发现即阻断）

| 禁止项 | 检测方式 | 处置 |
|---|---|---|
| 密钥/密码/IP 明文入仓 | git-secrets / truffleHog / 正则扫描 | CI 阻断，历史需清理（BFG） |
| 生产环境配置入仓 | `.env.production` / `application-prod.yml` 含真实 IP | 仅允许模板/示例 |
| 超大文件（>1500 行） | SonarQube / 静态分析 | 强制拆分，新增文件报警 |
| 无测试核心业务 | 覆盖率 < 10% 的 Service/Controller | 新增/修改必须补单测 |
| 假读写分离 | sharding master/slave URL 相同 | 启动检查报警，CI 校验 |
| 依赖不锁版本 | `moment: "latest"` / 无 lockfile | 强制 `pnpm + lockfile 入库` / `versions.lock` |

### 2.2 JeecgBoot 系特有红线

| 问题 | 表现 | 规避 |
|---|---|---|
| 前端多副本同步 | jiateng-pc 9 副本，all/mes 差 66 文件 | **新项目必须 Monorepo**，老项目建立"all 为源"同步流水线 |
| vxe-table 版本分裂 | 2.9 / 3.6 并存 | 统一版本，`pnpm catalog` 管理 |
| antd 1.x + element-ui 双 UI | 样式冲突、维护成本高 | 新项目 Vue3 + Element Plus 单 UI，老项目隔离迁移 |
| ESLint 规则大面积关闭 | 15+ 条关闭，`console.log` 靠打包兜底 | 分阶段开启，新代码 0 容忍 |

---

## 三、架构与设计守则

### 3.1 MOM 核心域建模原则

1. **工单状态机显式化**：7 态（待拆分→已拆分→已发布→已开始→完成/暂停/作废）必须用枚举+状态机库，禁止散落 `if/else`
2. **WMS 单据流向固化**：通知单→单据→出入库，6 大类（采购/外协/成品/研发/内部/其他）共享基类，差异用策略模式
3. **追溯链完整性优于性能**：缺环节即报警（G1-G4 规划），导出前置校验
4. **多租户硬编码零容忍**：`tenantId=10` 等硬编码全量清理，配置化下发

### 3.2 大屏/可视化项目通病对策清单

| 通病 | 标准对策 | 已验证项目 |
|---|---|---|
| 定时器泄漏 | `visibilitychange` 暂停 + 单定时器管理器 | lx-mes-screen, jiateng-pc |
| ECharts 实例泄漏 | `getInstanceByDom || init` 统一工具函数 | 同上 |
| 客户端时钟漂移 | 服务器时间接口 + 本地 fallback | lx-mes-screen 已落地 |
| 接口失败空白 | 重试 3 次 + 空数据兜底组件 | 需全项目补齐 |
| 轮播配置硬编码 | 后台配置化 + DB 持久化 | jiateng-pc 已有，需推广 |

### 3.3 请求层四件套（全项目标配）

```
1. 统一拦截：Token + Tenant-ID + Factory-Code + 防缓存参数
2. Blob 错误还原：导出接口 500 时解析 JSON 错误信息
3. 分组缓存：同 groupId 30s 命中 localStorage（防弹窗重复请求）
4. 请求签名：X-Sign + X-TIMESTAMP 防篡改（X-Sign 算法统一封装）
```

---

## 四、业务功能最小闭环清单

新 MOM 项目/模块上线前必须验收的"最小闭环"：

| 域 | 必验收场景 | 备注 |
|---|---|---|
| MES | 工单全流程：创建→拆分→发布→派工→报工→完工/暂停/作废 | 含 BOM 变更联动、工序并行/串行 |
| WMS | 采购入库→质检→上架→拣货→发货 + 调拨/盘点/移库 | FIFO/批次/序列号贯穿 |
| QMS | IQC/IPQC/OQC 三检 + 不合格品处置 + 复判 | 抽样策略 + SPC（P0） |
| TPM | 点检/保养计划→工单→执行→记录 + 备件领用/退库 | 维修看板 + 知识库 |
| 追溯 | 正向（工单→工序→物料）+ 反向（成品→原料）+ Excel 导出 | 完整性校验（P0） |
| 大屏 | 30min 轮询 + 服务器时间 + OEE/达成率/不良/库存 | 自动轮播 + 遥控器交互 |

---

## 五、部署与运维守则

### 5.1 单体 Fat-Jar 构建陷阱（cwjt 血泪教训）

- **禁用** 非聚合模块的 `spring-boot-maven-plugin:repackage`
- CI 必须校验：**无嵌套 BOOT-INF**、**Main-Class 正确**、**依赖完整**
- `fat-jar > 500MB` 报警，`> 1GB` 阻断（2GB EOCD bug 前车之鉴）

### 5.2 环境隔离

| 环境 | 配置来源 | 数据库 | 备注 |
|---|---|---|---|
| dev | Namespace `dev` / 本地 yml | 独立库 | 开发自测 |
| test | Namespace `test` | 独立库 | 集成测试 |
| prod | Namespace `prod` / 环境变量 / Vault | 生产库 | **密钥严禁入仓** |

### 5.3 数据库变更流程

- 所有 DDL/DML 纳入版本控制：`db/migration/V{版本}__{描述}.sql`
- Flyway/Liquibase 强制（cwjt 已规划，其余需补）
- 变更需：备份 → 低峰执行 → 回滚脚本就绪 → 变更后核对

### 5.4 对外托管与发布流程（R-26，2026-09-12 Gitee 托管事故确立）

| 步骤 | 要点 |
|---|---|
| ① 托管前体察 | **按类目清单全扫**：明文凭据（含 SQL 式 `PASSWORD '...'`/连接串/`--password=`）、内网地址、**OS 用户目录与绝对路径**、客户企业名、**真实业务标识（单号/雪花 ID）**、内网域名与长 token、**运行时生成物** |
| ② 处置 | 生成物**移出索引 + gitignore**（不是脱敏）；脱敏说明/记录一律"**类目 + 位置**"，**绝不复述原值**；凭据**入库即视为泄露 → 轮换** |
| ③ 两条线 | **审计线**仅本地（完整历史，**不设 upstream**）；**发布线恒为 1 个无父提交**（每次 orphan 重建，**绝不叠加**） |
| ④ 发布 | 脚本化：重建 → 断言单提交/树一致 → 敏感扫描（命中即拒绝）→ 推送 → **干净克隆自动复验** |
| ⑤ 清历史 | **`git push -f` 不清服务端对象**；唯一彻底手段 = **平台删库重建**；验证必须"**干净克隆 + `git fetch <完整SHA>`**"（`ls-remote <sha>` 会误判） |
| ⑥ 护栏 | `pre-push`（`core.hooksPath`）拦"非发布线 / 非单提交 / 树内命中敏感"；`--dry-run` **测不到钩子**，须 `--force` |

> 通用工具链约束（同源）：含反斜杠的规则/载荷一律**在 Node/Python 侧 spawn 执行**（MSYS 会把参数反斜杠转成 `/` 致规则静默失效）；**禁用 bash heredoc 传含反斜杠内容**；校验器**不内嵌被校验对象的规则**、**不静默截断输出**。详见 R-26。

---

## 六、团队与流程建议

### 6.1 "交接文档 + PROGRESS.md 续接"工作流（cwjt 验证有效）

- 每会话结束更新 PROGRESS.md（勾选/备注/阻塞）
- 新会话先读 PROGRESS.md 再开工
- A/B/C 三级阻塞项：A=阻塞交付、B=影响质量、C=技术债

### 6.2 Mock 先行验收节奏

- 前端先对接 Mock（VITE_USE_MOCK），独立交付 UI/交互
- 后端就绪后切真实接口，联调仅改 `baseURL`
- 减少前后端互相等待，并行度提升 40%+

### 6.3 知识沉淀强制动作

| 时机 | 动作 | 产出 |
|---|---|---|
| 解决疑难 Bug | 写入 `.codebuddy/memory/YYYY-MM-DD.md` | 根因+复现+修复+规避 |
| 完成核心功能 | 更新项目 `PROGRESS.md` | 进度+验收标准 |
| 发现跨项目通病 | 更新本文档（全局规则） | 规则编号+适用范围 |
| 项目阶段性交付 | 更新 `project-experience-summary/projects/{项目}.md` | 经验总结 |

---

## 七、规则落地检查清单（新项目启动时核对）

```
[ ] 接入 commitlint + husky + lint-staged + pnpm catalog
[ ] git-secrets / truffleHog 预提交钩子
[ ] SonarQube 质量门禁（覆盖率/重复率/复杂度/大文件）
[ ] Flyway/Liquibase 数据库版本控制
[ ] 环境变量/配置中心方案确认，无明文密钥
[ ] CI: 构建产物自检（无嵌套 BOOT-INF、Main-Class、依赖完整）
[ ] 前端 Monorepo（pnpm + turbo）或明确副本同步机制
[ ] 请求层四件套封装完成
[ ] 核心业务状态机枚举定义完成
[ ] 大屏通病对策清单已落地
[ ] PROGRESS.md 初始化 + 交接文档模板就位
[ ] 对外托管前跑类目化脱敏体检；生成物移出索引 + gitignore（R-26）
[ ] 发布线恒为单提交快照；清历史用删库重建；验证用干净克隆 fetch（R-26）
```

---

## 八、规则编号索引（便于引用）

| 编号 | 规则名 | 适用项目 | 优先级 |
|---|---|---|---|
| R-01 | 提交信息规范化 | 全部 | P0 |
| R-02 | 核心模块双人备份 | 全部 | P0 |
| R-03 | 密钥/配置零明文 | 全部 | P0 |
| R-04 | 单体构建自检 | Java 单体 | P0 |
| R-05 | 数据库版本控制 | 全部 | P0 |
| R-06 | 前端 Monorepo/副本同步 | Vue 项目 | P0 |
| R-07 | 请求层四件套 | 全部 | P1 |
| R-08 | 大屏通病对策 | 可视化项目 | P1 |
| R-09 | 追溯完整性校验 | 追溯域 | P1 |
| R-10 | Mock 先行验收 | 前后端分离 | P1 |
| R-11 | 交接文档+PROGRESS 续接 | 多会话任务 | P2 |
| R-12 | JeecgBoot 版本锁定 | donger-mom 体系 | P1 |
| R-22 | Windows CLI 直调真身（禁 .CMD/cmd /c） | Windows 全部 | P0 |
| R-23 | 外部工具启动前校验+快速失败 | 全部 | P0 |
| R-24 | 无头链路冒烟测试+机械化验收 | LLM/CLI 调度 | P0 |
| R-25 | wscript 系脚本 GBK 编码 + WSH 退出码/管道陷阱 | Windows 脚本 | P0 |
| R-26 | 对外托管：类目化脱敏体检 + 发布线单提交 + 干净克隆复验 | 全部（推第三方/外发） | P0 |

---

> **R-13~R-26**（归档时代：复制改造纪律/VCS 唯一出处/依赖门禁/配置模板化/敏感态三形态/外部集成三件套/权限三正交面/测试资产/双源对账；多智能体时代：CLI 直调真身/启动前校验/无头冒烟+机械化验收/wscript 编码与 WSH 验证铁律；托管时代：对外托管脱敏与单提交发布）见 [LEGACY_LESSONS.md](LEGACY_LESSONS.md)——分别来自 projects-old 归档项目群、agent-hub 复盘与 2026-09-12 Gitee 托管事故，编号与本文连续。

*文档维护：发现新跨项目规律时追加至此。重大规则变更需在项目群同步。*