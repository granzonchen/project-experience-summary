# lx-mes（MES 制造执行系统）+ lx-mes-screen（大屏） - 项目经验总结

> 分析对象：`D:\projects\lx-mes`（后端 9 Maven 子模块，约 5800+ Java 文件）+ `D:\projects\lx-mes-screen`（前端 Vue2 大屏）
> 分析方式：只读代码勘察 + git 历史分析

## 一、项目背景

力翔集团（锂电池结构件制造）的 MOM/MES 制造运营管理系统，多工厂多租户（安徽/合肥/庐江/宜春/安庆力翔等），2023-11 初始化，Gitee 托管多分支并行开发。lx-mes-screen 是从 PC 前端拆分出的独立大屏监控系统（2025-06 起），部署于车间电视，含 10 个看板页面。

### 业务模块（后端 9 模块）

| 模块 | Java 文件数 | 职责 |
|---|---|---|
| donger-mom-jeecg | 720 | 框架底座（基于 JeecgBoot 3.0 二次封装） |
| donger-mom-mdm | 739 | 主数据（物料/车间/设备/模具/班次） |
| donger-mom-mes | 1683 | 制造执行核心（工单/派工/报工/线边库/安灯/看板） |
| donger-mom-plan | 607 | 生产计划（排产/MRP/销售采购对接） |
| donger-mom-qms | 422 | 质量管理（IQC/IPQC 首件/IPQC 巡检/OQC） |
| donger-mom-tpm | 553 | 设备管理（点检/保养/维修/备件） |
| donger-mom-wms | 832 | 仓库/条码（解析/容器流转/库存/FIFO） |
| donger-mom-lx | 243 | 力翔定制（能源水电 Kafka 采集/绩效/钉钉/用友 U8） |

核心业务闭环：**工单 → 派工 → 报工 → 入库 → 交付**（`MesProduceTaskServiceImpl.java` 全流程 + `MesTaskReportController.java` 开工/首检/报工/完工接口）。

## 二、技术栈

### 后端
- Spring Boot 2.3.5 + Spring Cloud Hoxton.SR8 + Alibaba（OpenFeign + Nacos 配置中心，各服务独立端口 8090~8096）
- MyBatis-Plus 3.5.3 + actable（DO 注解自动建表）+ 自研 IDao
- MySQL 8 + 动态数据源；Redis + Redisson 3.16.1 分布式锁
- Shiro 1.7.1 + JWT + Shiro-Redis（X-Access-Token）
- XXL-Job 2.2.0（30+ 定时任务）、Kafka（水电表采集）、Spring 事务事件
- Knife4j 接口文档、EasyExcel 导入导出、Minio、Netty、cola 状态机

### 前端（lx-mes-screen）
- Vue 2.6 + Vue Router 3.6 + Vuex 3.1
- Ant Design Vue **和** Element UI 双 UI 库并存（历史迁移遗留）
- ECharts 5.4 + echarts-gl/liquidfill + DataV（@jiaminghi/data-view）+ autofit.js
- vue-seamless-scroll + 自研虚拟滚动组件（`components/listArray/index.vue`）
- vue-cli 3.x，多环境，代理 9 个后端服务

## 三、架构设计

### 后端 DDD 风格四层（按开发规范分包）

```
com.donger.mom.xxx
├── api            # Controller（按客户端分组：pc/pad/pln/screen/kanban/xxljob）
├── app            # Service（按业务域二级分包：exe/andon/salary/schedule/warehouse）
├── domain         # 领域模型
└── infrastructure # mysql 实体/mapper/dao、feign、外部服务
```

### 服务间通信
- Feign：对接 IoT 数采平台（OEE 数据）、TPM、WMS
- HTTP 内部接口：总部模块带 token + tenant-id 轮询各分厂
- 外部系统：用友 U8、钉钉（审批流/宜搭/消息）

### 大屏数据加载方式（重点）
- **聚合接口一次拉取**：`/mes/decision/board/collect` 一个接口拉回 12 类数据（销售/物料/采购/生产总览/OEE 等）
- **30 分钟轮询**：`setInterval` + beforeDestroy 清理
- **服务器时间**：每 5 分钟调接口同步（避免电视本地时钟不准），失败 fallback 本地时间
- **轮播**：Swiper 动态加载后台配置的页面列表

## 四、设计亮点

### 后端
1. **防重复提交三件套**：`@RepeatSubmit`（报工 15s/首检 10s/开工 3s）+ Redisson 逐 key 分布式锁（`ProductInBillNoticeController.java:96-151`，成品入库防重入）+ 事务事件解耦
2. **事务事件驱动**：`@TransactionalEventListener(phase = BEFORE_COMMIT)` 把报工主流程与库存联动解耦
3. **大屏聚合接口 + CompletableFuture 并行**：`MesDecisionShowServiceImpl.java:644-685` 5 个统计 `supplyAsync + allOf().join()` 并行
4. **看板数据缓存**：`buildKanbanDataCache()` 一次查出计划/报工/不良/安灯/设备等 7 类基础数据，OEE/良率/趋势全部派生，避免 N 次重复 SQL
5. **质量超时通知（DelayQueue）**：`QmsDelayedConfig.java` 延时队列 + 守护线程，IQC/IPQC/OQC 超时未检自动钉钉催办，不引重型 MQ
6. **总部跨厂聚合**：独立 screen_* 表 + 7 个 XxlJob 定时从各分厂 HTTP 拉数据
7. **null 字段序列化**：`call-setters-on-nulls: true`，Map 返回 null 字段也序列化（前端取值不 undefined）
8. **代码生成/自动建表**：actable + MyBatis-Plus 雪花 ID

### 大屏前端
1. **autofit 按比例缩放**：`autofit.init({dh:1080, dw:1920, resize:true})`，字号按 `clientHeight / 957` 系数
2. **自研虚拟滚动**：`listArray/index.vue` 仅渲染可视区域 + translate3d + requestAnimationFrame 无缝循环
3. **echarts 组件化 + 防泄漏**：17 个图表组件，`getInstanceByDom + dispose` 防实例泄漏
4. **阈值色阶配置化**：OEE/计划完成率红黄绿蓝配色由后端接口下发，车间可配不硬编码
5. **数据变化感知**：lastDataHash 对比数据 hash 才重渲染
6. **电视遥控器交互**：TVMixin 方向键/回车 → pointer 索引 → 模拟点击切换 Tab

## 五、踩坑经验清单

### git 历史真实修复
| 坑 | 修复 |
|---|---|
| 条码改造后表结构变更导致字段截断 | 表结构同步调整 |
| 同一条码可重复配料 | 配料时校验条码 |
| 报工无限制导致数量超报 | 最大报工数量限制 + 重复报工提示 |
| 调整工艺路线工序后工位任务缺失 | 工艺变更时联动工位任务 |
| 领料入库批次号被赋成流水号 | 批次号/流水号赋值修正 |
| 计划达成报表包含"通过式报工" | 报工数据过滤排除 |
| 实验任务创建无防抖 | 添加防抖 |
| 大屏日期显示为昨天（多次） | 统一后端 `getServerTime` 下发（含 today2 业务日字段） |
| 导出数量超限 | 物料上机导出控制数量 1w |

### 代码中发现的遗留问题（注意点）
1. `MesDecisionShowServiceImpl.java:919-921` OEE 数组重复补零 bug：`kdlList` 填充后又执行一次 add(0.0)，长度是 dateList 的 2 倍，与 powerOnRates 错位
2. 大屏多定时器并发：单页 2~3 个 setInterval 叠加，30 分钟空转定时器存在
3. 早期页面无 visibilitychange 检测，长期挂机内存/请求堆积（新页面已补暂停/恢复）
4. `factoryScreen.vue:972` 直接 `echarts.init` 未先 getInstanceByDom，轮询会重复创建实例
5. 请求失败无重试兜底（新页面已加 maxRetryCount: 3 + withTimeout）
6. 租户硬编码：`factoryScreen.vue:752-757` tenantId: 2023
7. moment 与 dayjs 双时间库并存
8. vue.config.js 代理顺序：具体前缀必须排在通用代理之前

### 数据库/框架层共性坑
- MySQL → PostgreSQL 迁移：DATE_FORMAT/IFNULL/GROUP_CONCAT/反引号是重灾区
- VARCHAR 超 255 需 2 字节保存长度降性能，按实际 64/128/500 设置
- 商业计算用 BigDecimal，比率统一 `divide(...,4, HALF_UP)`
- 报工并发更新 5 张聚合表无乐观锁，高并发存在丢失更新（靠 @RepeatSubmit 限流缓解）

## 六、可复用经验

1. **大屏聚合接口模式**：12 个散接口合并 1 个 collect 接口，前端单定时器轮询，后端 CompletableFuture 并行——大屏项目最值得抄的设计
2. **看板数据缓存 DTO**：一次取基础数据、多次派生图表数据
3. **服务器时间 Mixin**：大屏/电视场景时间显示必须走后端接口 + 本地 fallback
4. **自研虚拟滚动组件**：约 180 行，可独立抽出（含 rAF 循环、悬停暂停、数据变更自动重启）
5. **阈值色阶配置化**：接口下发配色，避免发版
6. **DelayQueue 超时催办**：轻量级任务超时通知方案
7. **后端开发规范文档**：分包/DO/Dao/Controller 四篇规范可直接作为新人培训材料

## 七、改进建议

**高优先级**
1. 修复 OEE 数组重复补零 bug（已造成数据错位）
2. 报工聚合数更新加乐观锁，杜绝高并发超报/漏报
3. 统一前端定时器管理：抽出 refreshMixin（防重入 + AbortController + visibilitychange + 单定时器）

**中优先级**
4. 统一 moment/dayjs、统一 axios 双实例
5. echarts 初始化统一走 `getInstanceByDom || init` 工具函数
6. 大屏接口统一错误兜底（空数据占位 + 重试退避）
7. 租户 ID 等业务参数从配置中心下发，去除硬编码

**低优先级**
8. 单文件 2000+ 行页面按区块拆子组件
9. 清理 `*_copy.vue` 副本文件
10. 多工厂分支定期合回 dev 主线

## 沉淀建议

- git log 修复清单可整理为《MES 已知问题与修复手册》（导出/条码/重复报工/工艺变更四类高频坑区）
- 大屏开发 Checklist：服务器时间、30 分钟轮询、visibility 暂停、echarts dispose、虚拟滚动、autofit 缩放、空数据兜底、遥控器按键
