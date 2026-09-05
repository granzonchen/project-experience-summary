# 佳腾 MOM 平台（jiateng-pc）- 项目经验总结

> 分析对象：`D:\projects\jiateng-pc`（Maven 多模块 Java 后端 + 9 套前端工程，git 1023 提交）
> 分析方式：只读代码勘察 + git 历史分析
> 当前阶段：生产运行中（2026-08 最新勘察），sharding 分支做读写分离/分库改造；业务进入维护优化期

## 一、项目背景

佳腾（jtyy=佳腾医药）的**东珥智能制造生产运营平台（MOM）**，由东珥科技（donger）提供 JeecgBoot 3.0 二次开发框架（`org.jeecgframework.boot:donger-mom-jeecg:3.0`）定制开发。注意：**根目录是 Maven 后端仓库，前端以 `ui/` 子目录嵌在各模块内**，根 package.json 只是安装 yarn 的占位文件。

11 个模块：MES（制造执行）、WMS（仓储）、QMS（质量）、TPM（设备）、SRM（供应商）、MDM（主数据）、PLN/APS（计划排产）、QRC、mon-retrospect（产品追溯）、jeecg（基础平台）、all（聚合部署）。

前后端分离，前端按 `/jeecg-boot/{模块前缀}` 代理多后端：mes→8080、pln→8081、srm→8082、qms→8089、tpm→8085、wms→9995、retrospect→9996。

## 二、技术栈

- **前端**：Vue 2.6（Options API）+ Vuex 3 + Vue Router 3（history）；ant-design-vue 1.7.2 为主 + element-ui 2.13 混用 + Vant 2；自研组件库 `@drcom/v2-ui`
- **框架**：JeecgBoot 官方前端 vue-antd-jeecg 3.x 深度改造版
- **构建**：Vue CLI 3.3（webpack 4）+ gzip + splitChunks 分包 + 生产去 console
- **表格**：vxe-table 3.6.6（all/mes/tpm/qms/srm）+ 2.9.x 旧版（wms/jeecg）**版本分裂**
- **图表**：echarts 5、viser-vue（antv/g2）、@jiaminghi/data-view（大屏）、highcharts 11
- **甘特/日历**：dhtmlx-gantt 7.1.8、a-gantt、fullcalendar 6.1.10
- **移动端**：uni-app 2.x + uview-ui + flyio；pad 端为 PC 精简版
- **后端**：Spring Boot 2.3.5 + MyBatis-Plus + JeecgBoot 3.0 封装，Nacos 配置中心，SonarQube 质量扫描
- **规范工具**：ESLint 5.16（standard，**大量规则被关闭**）；**无 husky/commitlint/lint-staged**

## 三、架构与核心模块

### 9 套前端工程（多副本架构）

| 前端 | 用途 |
|---|---|
| jt-mom-jeecg/ui/pc | 基础平台（用户/角色/菜单/字典/租户/定时任务） |
| jt-mom-all/ui/pc | MOM 集成门户（1366 个 .vue，含全部业务域 + 大屏） |
| jt-mom-mes/ui/pc | MES 前端（与 all 仅 66 个文件差异） |
| jt-mom-wms/ui/pc | WMS 前端（含在线表单 + 表单设计器） |
| jt-mom-qms/ui/pc / tpm/ui/pc / srm/ui/supplier | QMS / TPM / SRM 供应商门户 |
| jt-mom-all/ui/pad、jt-mom-mes/ui/pad | 车间平板端 |
| jt-mom-qms/ui/mobile、wms/ui/app、tpm/ui/app | uni-app 移动端 |

### src 结构（以 jt-mom-all/ui/pc 为例）

```
src/
├── config/            # window._CONFIG（domianURL/staticDomainURL/pdfDomainURL）
├── cas/sso.js         # CAS 单点登录
├── permission.js      # 路由守卫：token 校验 → 拉菜单 → 动态生成路由
├── api/               # 按域分目录（186 个 js）
├── components/        # jeecg 标准组件 + 自研 biz-search/biz-table/BSuperQuery/VxeTable
├── mixins/            # JeecgListMixin/JEditableTableMixin/JVxeTableMixin/WebsocketMixin
├── store/             # vuex：app/user/permission/enhance(JS增强)
└── utils/             # request 封装、hasPermission 指令、encryption(签名)、GroupRequest
```

### 权限控制链路

1. 登录：账号/手机号/第三方/CAS 四种登录，token 存 vue-ls（7 天）
2. 菜单驱动动态路由：`permission.js` 拉后端菜单 → `generateIndexRouter` 转路由 → `router.addRoutes`
3. 按钮权限：`v-has` 指令支持 **`||`（或）、`&&`（与）、`!`（取反）、逗号多权限、流程节点级权限**
4. 多应用/多租户：`APP_MODE=part` + `VUE_APP_BASE_CODE` 过滤菜单 + `tenant-id` 请求头隔离

### 请求封装（src/utils/request.js）

- axios baseURL=/jeecg-boot，timeout **600000ms（10 分钟）**（大报表/导出）
- 拦截：X-Access-Token、tenant-id、GET 防缓存参数
- **Blob 响应 500 时 blobToJson 解析错误 JSON**（导出场景关键处理）
- get/post 带 **X-Sign + X-TIMESTAMP 签名**（防篡改）
- `GroupRequest.js`：请求分组缓存（同 groupId 30 秒内命中 localStorage，防弹窗高频重复请求）

### 列表页标准模式（JeecgListMixin）

声明式配置驱动：定义 `url.list/url.delete/url.exportXlsUrl` + `columns` 即获得查询/分页/批量删除/列显隐自定义/导出（兼容 IE）/导入（201 部分成功提示+错误文件下载）。

## 四、设计亮点

1. **声明式列表页体系**：JeecgListMixin + biz-search/biz-table（vxe 封装），新页面零模板代码；`views/mes/pages/exe/task/index.vue` 为典型范例（状态机驱动操作列：待拆分→已拆分→已发布→已开始→完成/暂停/作废）
2. **v-has 指令表达式能力**：布尔表达式组合权限 + 流程节点权限，远超原生 v-permission
3. **Blob 错误还原**：文件流接口出错返回 JSON，前端解析还原错误信息——导出功能必备经验
4. **请求分组缓存**：高频弹窗选择接口防重复请求
5. **请求签名**：X-Sign + X-TIMESTAMP 防篡改
6. **Token 失效统一体验**：全局弹窗 + 企微/钉钉 UA 差异化（自动重登）
7. **CAS + OAuth2（企微/钉钉）双登录**：UA 自动识别分流
8. **JS 增强（低代码）**：enhance.js 缓存 table 增强记录 + 动态执行用户 JS 增强（随机 id 防冲突）
9. **大屏体系**：factoryScreen 云工厂/wmsScreen/digitScreen + 3 车间大屏轮播，data-view + seamless-scroll + echarts 5

## 五、踩坑经验清单

| 坑 | 说明/对策 |
|---|---|
| **9 套前端副本维护灾难** | 同源复制后各自演化（all 与 mes 已差 66 个文件），同一需求需多端同步，极易漏改 |
| **硬编码密钥/密码**（严重） | application.yml 中 signatureSecret、钉钉 appSecret、MinIO/OSS 密钥、DB 密码明文；应立即外置 + 轮换 |
| **假读写分离** | sharding 配置 master 与 slave 指向同一个库，round_robin 轮询同实例，无实际分离效果 |
| **配置环境错乱** | Nacos/ES/RabbitMQ/xxl-job 地址混用生产内网 IP 与 127.0.0.1；file-view-domain 硬编码 |
| **技术栈陈旧锁定** | Vue 2.6 + webpack 4 + ESLint 5 + axios 0.18；antd 1.x 与 element-ui 双 UI 库并存（样式冲突） |
| **依赖卫生** | `moment: "latest"` 构建不可复现；vxe-table 2.9/3.6 版本分裂；node-sass 兼容坑 |
| **package.json 元数据错误** | tpm name=jt-mom-mes-pc、srm name=jt-mom-qms-pc——复制后未改 |
| **超长单文件** | `views/bigScreen/factoryScreen.vue` 3114 行 |
| **打印模板无回归测试** | 条码/流转卡打印问题反复修（打印模板需独立验收） |
| **提交规范不统一** | FEAT:/FIX:/fix:/feat: 混用、无 scope、无 husky/commitlint 兜底 |
| **ESLint 规则大面积关闭** | 15+ 条关闭（历史升级债），console.log 泛滥靠生产 drop_console 兜底 |
| **开发规范文档为空** | `开发规范/` 下 5 个 md 均为空占位 |
| **生产配置残留** | `.env.production` 里 API 地址是 localhost:8080（提交进仓库） |

## 六、可复用经验

1. **列表页三件套**：JeecgListMixin + biz-search + biz-table 的声明式 CRUD 模式，可提炼为团队前端模板
2. **权限指令表达式**：|| && ! 组合 + 流程节点权限，MES 类复杂按钮权限的成熟方案
3. **请求层四件套**：统一拦截 + blob 错误还原 + 分组缓存（GroupRequest）+ 签名（X-Sign）
4. **多端多应用路由**：菜单驱动动态路由 + appCode 过滤 + tenant-id 隔离，适合集团级多租户 SaaS
5. **Token 失效体验 + CAS/OAuth2 UA 分流**方案
6. **大屏组件选型**：data-view + seamless-scroll + echarts 5 + 轮播模式

## 七、改进建议（按优先级）

1. **密钥治理**：立即外置所有凭据（Nacos/环境变量/Vault），signatureSecret 与 DB 密码轮换
2. **前端收敛 Monorepo**：以 jt-mom-all/ui/pc 为基座业务域拆包（或私有 npm 包共享 jeecg 基础层），消灭 9 副本；至少建立"all 为源、其余为壳"的同步流水线
3. **修复假读写分离**：为 slave 配置真实从库；补充分片键与绑定表配置
4. **统一依赖**：锁定 moment、统一 vxe-table 版本、统一包管理器（pnpm + lockfile 入库）
5. **工程化补课**：接入 husky + commitlint + lint-staged；CI 构建 + 产物归档；对 mixin/request 层补单测
6. **质量门禁**：SonarQube 接入 MR 门禁；拆分 3000+ 行大文件
7. **规范落地**：补全 `开发规范/` 文档；规范提交信息
8. **环境治理**：清理提交内 localhost 生产配置；Nacos namespace 按环境隔离

## 与其他项目的关系

- **与 lx-mes / card-mode / hcmom 同族**：同为东珥科技 donger-mom-* 体系（包名 com.donger.*），框架底座相同，踩坑经验可互相印证
- **前端架构异于 cwjt**：cwjt 用 Vue3 + pnpm monorepo 重写了同业务域，jiateng-pc 是 JeecgBoot 系经典 Vue2 架构，二者形成"新旧两代架构"对照

## 八、业务画像与现状（2026-08 补充勘察）

### 8.1 业务画像

- **主体**：佳腾/嘉腾（git 组 `Intelligent-manufacturing-group/jtyy`），东珥科技（donger）以 JeecgBoot 3.0 定制交付，生产库直连 `donger.zapto.org:22222/jtyy-prod`（MySQL 8）
- **业务闭环**：销售订单 → PLN 计划排产（订单池/周月计划/预测/评审/MRP 自制·采购·外协/齐套分析）→ MES 工单（待拆分→已拆分→已发布→已开始→完成/暂停/作废，7 态状态机）→ 派工/执行（拉动领料、报工、报损）→ WMS 出入库（通知单→单据→出入库，覆盖采购/外协/成品/研发/内部/其他 6 类）→ QMS 检验（采购/工序/成品 + 抽样策略）→ mon-retrospect 全链路追溯（工单/工序/物料/设备/库存，正反向 + Excel 导出）
- **特色域**：QRC 快速响应中心（签到/任务/会议/测量区域/大屏统计/延迟提醒 Job）、TPM 设备全生命周期（点检/保养/维修看板/备件/知识库）、SRM 供应商门户（协同/对账/发票/评价/消息）、3 套大屏（factoryScreen 云工厂 / wmsScreen / digitScreen + 车间轮播）
- **前端业务面**：all 门户 1366 .vue（20 个业务目录），WMS 目录最重（通知单→单据→出入库全链路 10 组业务类型）

### 8.2 现状判断（生命周期：上线后维护期）

1. **开发强度断崖**：git 提交 2023-11 立项 → 2024 年 738 次（主开发期）→ 2025 年 46 次 → 2026 年至今仅 7 次（截至 08-19）；分支 dev(1360)/sharding(1476) 为活跃线，master(806) 滞后
2. **sharding 改造未落地**：mes/qms/wms 三模块 `application-sharding.yml` 中 master 与 slave **均指向同一库**（假读写分离），round_robin 轮询同实例；dev 分支 2024-10 起即存在"主从读写分离事务"提交，至今未完成
3. **近期工作性质**：全部为修补型（流转卡样式、条码 33-37 行显示、库存预警、领料清单导出按库位拆分、大屏查询条件）→ 业务已稳定运行，进入按需优化阶段
4. **生产偶发问题**：2026-08-19 流转卡下载 500（AWT `NoClassDefFoundError`），重启自愈；已确认该链路（Aspose.Words PDF 渲染）**架构上绑定 Java2D**，只能保证 AWT 健康 + 诊断日志（详见 `.codebuddy/memory/2026-08-19.md`）
5. **部署形态**：all 聚合 jar（mes+qms+retrospect）+ 多服务内网 IP（MySQL <DB_HOST>:<DB_PORT> / Redis <REDIS_HOST> / RabbitMQ <MQ_HOST> / ES <ES_HOST>）；存在 docker-compose 与 k8s 清单，但生产为 Windows Server 裸机 java -jar

### 8.3 业务侧风险

| 风险 | 说明 |
|---|---|
| 数据安全 | 生产库公网映射 + root 明文密码（Donger!@#456）+ 无备份脚本证据；假读写分离下压力全在主库 |
| 回归无保障 | 全仓库 0 个测试文件；报工/库存/追溯等核心链路任何改动靠人工回归 |
| 追溯数据质量 | 医药/制造合规核心卖点是追溯，但依赖一线人工录入，缺防错与完整性校验（比对/缺卡提醒） |
| 人才断层 | 23 个 committer 账号（含乱码/重复），Vue2+Spring Boot 2.3 栈 2026 年招聘/升级双难 |
| 依赖单一厂商 | 框架层 donger-mom-jeecg 为商业封闭底座，升级与修复节奏受制于东珥科技 |

### 8.4 后续发展建议（业务视角）

**短期（1-3 月，维稳）**
1. 密钥治理：DB/钉钉/MinIO 密码全部外置 Nacos 或环境变量并轮换（已在改进清单首位）
2. 读写分离二选一：配置真实从库，或删除 sharding 配置消除"假分离"假象
3. 补数据库备份/恢复演练 + 主从一致性核对
4. 打印/条码（流转卡、物料标签）建回归清单：该链路已 2 次生产事故

**中期（半年，增效）**
5. 以 QRC + 追溯 + 车间大屏为拳头做"数字化透明车间"运营闭环：大屏数据反哺日报例会（pln 已有生产例会模块），报表深化 OEE/达成率
6. 追溯链补防错：录入校验 + 缺失卡预警 + 导出前置完整性检查（防"追溯断链"）
7. 前端收敛：以 all 为源建立同步流水线，或按 cwjt 经验迁移 Vue3 monorepo（cwjt 已验证同业务域可行）

**长期（1 年+，演进）**
8. 平台产品化：本仓库与 lx-mes/hexconn/card-mode 同源，可提炼"donger MOM 行业套件"（权限表达式、列表三件套、扫码三件套、大屏组件），新客户不再复制 9 副本
9. 技术债换代：Spring Boot 3 + Vue3（参考 cwjt 迁移路径）分模块灰度迁移，先迁报表/大屏等低耦合域

## 九、透明车间运营闭环实施方案（2026-08 规划）

> 落地于 8.4 中期建议第 5、6 条，实施跟踪见 `D:\projects\jiateng-pc\PROGRESS.md`
> 方案定位：不新建平台，用现有 5 个域（追溯/QRC/大屏/例会/提醒）的接口与数据模型打通闭环

### 9.1 现状盘点：已有资产与四个断点

| 环节 | 现状 | 关键接口/组件 |
|---|---|---|
| 数据发现（大屏） | 30+ 接口覆盖达成率/延迟 5 维分析/不良/在制品/库存预警/客户订单 | `ScreenController`（/mes/screen）、factoryScreen/wmsScreen/digitScreen |
| 数据溯源（追溯） | 正/反向全链路：工单/工序/物料/设备/人员/库存 + Excel 导出 + 批次对比 | `RetrospectCommonQueryController`（9 个 page 接口） |
| 问题处置（QRC） | 完整方法论：special_issue → 5WHY/根因 → 纠正 → 验证 → 关闭 + 审批/评审/督办任务 | `SpecialIssueController`、fastReversePanel |
| 管理跟进（例会） | 计划未达成 → 原因 → 责任人 → 跟踪（meeting/tracking 双页） | `PlnProduceMeetingController` |
| 提醒通道 | 延迟提醒 Job 已有 | `DelayReminderJob` |

**四个断点**（闭环要补的连接）：
1. 追溯无防错——数据可信度无保障，缺卡/断链无人知
2. 大屏异常只能"看"，不能一键转 QRC 问题
3. QRC 问题不自动进例会，跟踪靠手工
4. 问题关闭后是否改善，无效果回归度量

### 9.2 闭环设计（数据流）

```
[数据可信层] 追溯补防错 ──保障──> [发现层] 车间大屏/快速响应面板
                                        │ 一键转问题（带工单/批次/不良上下文）
                                        ▼
[回归层] 月度度量报表 <── 关闭状态回写 <── [处置层] QRC 问题闭环（5WHY→纠正→验证→关闭）
                                        ▲
                          [跟进层] 生产例会（自动汇总未关闭问题+计划偏差，责任到人）
```

核心原则：**异常从大屏产生，问题在 QRC 闭环，责任在例会跟进，效果用数据回归**——每条记录带 ID 关联，不靠人工搬运。

### 9.3 三阶段实施

**阶段一：追溯补防错（约 1 个月，先保数据可信）**
1. 完整性校验服务（jt-mon-retrospect 新增 `RetrospectIntegrityService`）：按工单/批次定义"环节检查清单"（投料→工序→检验→入库→发运），逐环节核对 `retro_mark_log` 记录，输出缺失清单
2. 缺卡预警 Job：复用 `DelayReminderJob` 模式，每日扫断链批次 → 钉钉/企微通知责任人（负责人可配置）
3. 录入防错增强：扫码上下文校验、重复扫码提示、关键字段必填（PDA 端 jt-app 已有 ScanMixin，PC 端补）
4. 导出前置检查：导出 Excel 前先跑完整性校验，断链时提示并附缺失清单
5. 前端：追溯页顶部加"完整性状态条"（绿/黄/红 + 缺失明细弹窗）

**阶段二：大屏→QRC 联动 + 例会反哺（约 2 个月，打通闭环）**
- 后端：
  1. `ScreenController` 异常点（延迟工单/不良批次/达成率低）新增"一键转问题"：自动创建 `special_issue`，预填 issueName/issueIntro（含工单号/批次/工序/不良项/截图 URL）、responsiblePerson 候选
  2. `PlnProduceMeetingController` 扩展：`/meeting/queryPage` 增加"待办问题"维度——自动拉取未关闭且责任部门匹配的 QRC 问题作为会议议程项；会议条目可与问题 ID 关联
  3. QRC 问题状态变化（关闭/挂起）→ 通知例会跟踪页刷新
- 前端：
  1. 大屏异常点点击 → 弹窗"转问题"（预填上下文，可编辑后提交）
  2. 例会页面嵌入"未关闭问题清单"tab（扩展原 tracking 页）
  3. 快速响应面板（fastReversePanel）新增追溯缺失/延迟 TOP 数据块

**阶段三：运营度量（约 3 个月，效果回归）**
1. 闭环看板（新大屏页或并入 digitScreen）：问题关闭率、平均关闭时长、复发率（同不良项/同工单二次发生）、追溯完整率
2. 月度经营分析报表（MesAnalysis 系列扩展）：延误原因 TOP 趋势、问题分布（部门/工序）、闭环前后达成率对比
3. 大屏轮播加入"问题督办"页（未关闭问题 + 责任人 + 超期天数）

### 9.4 技术要点

- **复用不新建**：DelayReminderJob（提醒）、WebsocketMixin（状态实时推送）、X-Sign 签名、v-has 权限、JeecgListMixin 声明式列表——全部沿用现有模式
- **后端改动分布**：追溯完整性校验 + Job（retrospect 模块）；大屏转问题（mes 模块，Feign 调 qrc 或直连）；例会扩展（plan 模块）
- **跨模块关联**：`special_issue` 加冗余字段（taskId/batchNo/matId/issueType），便于大屏和例会直接过滤，避免跨库 join
- **0 测试现状风险**：三处核心改动（完整性校验/转问题/例会汇总）各补 1 个 Service 层单测 + 1 个接口联调用例

### 9.5 度量 KPI

| 指标 | 目标 |
|---|---|
| 追溯完整率（按批次） | ≥95% |
| 大屏异常 → QRC 问题转化率 | ≥80% |
| 例会问题按期关闭率 | ≥90% |
| 同类问题复发率 | 环比下降 |

## 十、MOM 产品能力差距与产品规划（2026-08 勘察）

> 方法：以 ISA-95 / MESA MOM 能力模型为基准，对照本仓库 11 模块 + 前端 1366 页实测能力
> 重要修正：git log 出现"电镀排产页面"、前端 ownerName="嘉腾"、有绩效工资模块——**企业实为金属表面处理/五金制造（智能制造集团），非医药**，早期"佳腾医药"为误判；合规体系对标 ISO9001/IATF16949/ISO14001（电镀行业环保强监管），而非 GMP

### 10.1 能力矩阵（已有 vs MOM 标准模型）

| MOM 能力域 | 标准能力 | 本项目现状 | 评级 |
|---|---|---|---|
| 计划排产 | 需求预测/订单承诺/主排产/MRP/产能约束排产/齐套 | 订单池/预测/评审/周月计划/MRP（自制采购外协）/齐套/电镀排产；**无自动排产算法**（手工甘特为主） | ★★★★ |
| 制造执行 | 工单管理/派工/执行跟踪/报工/数据采集/安灯 | 工单 7 态状态机/派工/拉动领料/报工报损/安灯（Pad+大屏 9 接口）；**数据采集缺失**（报工靠人工，无设备参数自动采集） | ★★★★ |
| 仓储物流 | 出入库/库位/库存/盘点/FIFO/批次 | 通知单→单据→出入库 6 类/FIFO/库位设计/实时库存/预警/调拨/盘点计划/在制品库位 | ★★★★★ |
| 质量管理 | IQC/IPQC/OQC/不合格品/SPC/量具/审核/文档 | 采购/工序/成品检验+抽样策略/不合格品/可疑品判定；**无 SPC 控制图/CPK、无量具校准、无审核管理** | ★★★ |
| 设备管理 | 资产台账/点检/保养/维修/备件/知识库/OEE | 点检/保养/维修工单+看板/备件/知识库/盘点；**OEE 前端展示为假数据**（summarize.vue 接口注释 + `item.oee || 51.9` 硬编码），无真实计算（缺数采） | ★★★★ |
| 追溯 | 批次谱系/正反向追溯/防错 | 全链路正反向（工单/工序/物料/设备/人员/库存）+批次对比+导出；**无完整性防错**（第九章正在补） | ★★★★ |
| 问题闭环 | 异常上报/CAPA/8D/趋势分析 | QRC 快速响应中心：5WHY/根因/纠正/验证/关闭+审批评审督办任务+签到面板；**缺有效性验证/再发预防/趋势分析** | ★★★★ |
| 供应商协同 | 门户/询报价/对账/评价 | SRM 门户：协同/对账/发票/评价/消息；缺询报价与合同管理 | ★★★ |
| 绩效人力 | 报工工时/绩效/技能矩阵/考勤 | 绩效工资（SalaryConfig/SalaryReport）；缺工时归集分析与技能矩阵 | ★★★ |
| 能源环保 | 水电气采集/能耗分析/环保监测 | **无**（lx-mes 有 donger-mom-lx 能源采集可借鉴） | ★ |
| 成本 | 报损/订单成本/质量成本 | 今日成本/报损（ScreenController getTodayCost）；缺标准成本对比/COQ | ★★ |
| 文档控制 | 图纸/SOP 版本管理+审批流+生效发布 | MdmDrawing 图纸分类+挂载；**无版本审批流** | ★★ |
| 报表分析 | KPI 驾驶舱/OEE 分析/BI | 大屏 3 套+汇总页+日报月报年度报表；**OEE 假数据**、无 BI 驾驶舱 | ★★★ |

### 10.2 差距清单与优先级（P0 合规底线 / P1 运营提效 / P2 行业纵深）

**P0（客户审核必查项，与营收直接相关）**
| # | 功能 | 现状 | 价值与验收 |
|---|---|---|---|
| G1 | SPC 统计过程控制 | 抽样检验有、控制图无 | IATF 客户 SQE 高频要求：X-bar-R/p-chart + CPK + Nelson 异常规则；验收：任意检验项生成控制图 |
| G2 | 量具管理（MSA） | 完全缺失 | IATF 强制：量具台账/校准计划/到期提醒；验收：校准到期自动提醒 |
| G3 | 文档控制 DCC | 图纸无版本/审批 | 体系审核必查：图纸/SOP 版本管理+审批流+生效发布+作废归档；验收：换版走审批、现场只看到生效版 |
| G4 | OEE 真实化（第一步：手工录入 OEE 参数） | 前端假数据 | 先用手工报工数据算 OEE（可用率×性能×良率），不依赖数采即可上线；验收：大屏 OEE 与报工数据一致 |

**P1（运营提效，ROI 高）**
| # | 功能 | 说明 |
|---|---|---|
| G5 | 设备数采平台（IoT） | 时序数据底座（PLC/Modbus/网关），OEE/SPC/安灯/能耗共同底座；借鉴 cwjt mom-iot、lx-mes 数采平台架构 |
| G6 | 统一预警中心 | 聚合延迟提醒/缺卡预警/库存预警/校准到期/安灯升级，企微钉钉短信订阅制；复用 DelayReminderJob |
| G7 | 安灯升级机制 | 超时逐级上报（班组长→车间主任→厂长）+ 消息联动（lx-mes 有 DelayQueue 方案可抄） |
| G8 | APS 自动排产 | 产能约束/换型优化/拖期最小化；先做"自动排产建议+人工确认"半自动模式 |
| G9 | 成本深化 | 标准成本对比/订单成本归集/质量成本 COQ 报表 |
| G10 | CAPA 增强 | 有效性验证节点+再发预防记录+问题趋势分析（与第九章闭环联动） |

**P2（行业纵深，差异化）**
| # | 功能 | 说明 |
|---|---|---|
| G11 | 能源环保（电镀行业刚需） | 水电气采集+能耗单耗分析+废水危废管理（ISO14001）；借鉴 lx-mes 能源模块 |
| G12 | 外协工序协同 | 外协进度回传/质量数据回传（SRM 门户扩展） |
| G13 | 标签模板中心 | 条码/标签模板集中管理+打印防错（当前 BarcodeGenerator 硬编码） |
| G14 | BI 经营驾驶舱 | OEE 趋势/产能利用率/质量趋势/问题复发多维分析（与闭环阶段三合并推进） |
| G15 | 内部物流调度 | 线边库配送任务+拉动看板（与 MES 拉动领料联动） |

### 10.3 规划方法论与路线图

**依赖关系**（先底座后应用）：
```
设备数采平台 G5 ─┬─> OEE 真实化 G4（自动模式）
                 ├─> SPC G1（自动数据源）
                 └─> 安灯升级 G7（设备状态联动）
预警中心 G6 <── 依赖 DelayReminderJob/缺卡预警/校准提醒（G2）先行
文档控制 G3 / 量具 G2 ── 独立，可立即开工
```

**排序原则**：合规先于效率（G1-G4 先做，直接服务于客户审核）；底座先于应用（G5 服务 G4/G1/G7/G11）；数据可信先于分析（第九章追溯防错是 G14 的前提）。

**建议里程碑**：
- M1（1-2 月）：G2 量具 + G3 文档控制（独立快赢，体系审核速效）+ G4 OEE 手工版
- M2（3-4 月）：G5 数采试点（1 条电镀线）+ G6 预警中心 + G1 SPC 手工录入版
- M3（半年+）：G1/G4 自动数据源切换 + G7 安灯升级 + G9 成本 + G14 BI
- 远期：G8 APS、G11 能源环保、G12 外协协同、G13 标签中心、G15 物流调度

**投入产出视角**：G2/G3 是"过审刚需"（无它丢订单）；G4/G5/G1 是"数字化说服力"（让老板在车间大屏看到真实 OEE/CPK）；G6/G7/G10 是"管理抓手"（问题不落地、责任不清）；G8/G11-G15 是"行业竞争力"（电镀行业差异化）。
