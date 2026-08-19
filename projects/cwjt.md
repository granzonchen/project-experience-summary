# 昌威交通 2.0（cwjt）+ cwjt_front - 项目经验总结

> 分析对象：`D:\projects\cwjt`（后端 Maven 多模块 16 个）+ `D:\projects\cwjt_front`（前端 pnpm monorepo 16 应用）
> 分析方式：只读代码勘察 + git 历史 + 交接文档（docs/handover/）
> 当前阶段：生产试运行 + 验收补缺收尾（2026-07~08 密集交付）

## 一、项目背景

昌威交通 2.0（CWJT）是面向制造企业的 **MOM 云平台**，基于 pig4cloud（pigx）商业框架二次开发。业务模块矩阵：

| 后端模块 | 前端应用 | 业务域 |
|---|---|---|
| mom-mdm / mom-mes / mom-wms / mom-qms / mom-tpm / mom-plan / mom-pms / mom-iot | mom-*-ui（9995~10011 各端口） | 主数据/制造执行/仓库/质量/设备/计划/采购/物联网数采 |
| mom-common / mom-boot | mom-admin-ui（9999） | 公共服务 / 单体聚合启动器 |
| mom-screen | mom-bigscreen-ui（10010） | 大屏 BFF + 四大屏 |
| mom-sa/spm/wem/pm/eam | 对应 -ui | 成本/安环/能源/绩效/资产 |
| — | mom-pad-ui（10002） | 车间平板端 |

部署形态（生产实测）：Windows Server 单机 + WinSW 服务跑**单体 fat-jar** + 本机 PostgreSQL（372 表/17 schema）+ cnyt 数采 MySQL + Redis + nginx :80。支持双部署模式：分布式微服务（Nacos + gateway）与单体。

## 二、技术栈

### 后端
- Java 17 + Maven 多模块；Spring Boot **3.3.13**（显式覆盖父 pom 的 3.3.3——该版本有 2GB jar EOCD 偏移 bug）
- MyBatis-Plus 3.x + QueryGenerator 自动 QueryWrapper
- Druid + **dynamic-datasource 4.3.1**（多库路由核心）
- Spring Security + **OAuth2 Authorization Server**（pigx 定制：密码/短信/授权码、验证码、AES 解密过滤器、Redis 存 token）
- Nacos + Feign + Sentinel + XXL-Job；Undertow 容器；TLog 链路追踪
- springdoc-openapi + knife4j；Flowable + 钉钉审批双通道

### 前端
- **Vue 3.5 + TypeScript + Vite 6 + pnpm 9.7.1 monorepo + Turbo 2.x**（架构蓝本 vue-vben-admin 5.x）
- Element Plus + Tailwind + DaisyUI；vxe-table / el-table 混用
- Pinia 2.2 + persist、Vue Router 4（**后端下发菜单驱动**）、无界 wujie 微前端
- 自研 `@mom/request`（axios，vben 系 RequestClient）
- ESLint 8 flat + Prettier + Stylelint + commitlint + czg + husky + lint-staged（全链路规范）

## 三、架构设计

### 后端模块模板

```
mom-xxx/
├── mom-xxx-api/     # 跨模块契约：entity/dto/vo/enums/feign 接口
└── mom-xxx-biz/     # controller / service / mapper / util / batch / event / task
```

**关键事实**：upms（用户权限）、auth（认证中心）、common-security/data 等框架组件**不在本仓库**，以二进制制品发布到内网 Nexus——仓库只含业务模块 + mom-boot 聚合器 + mom-screen BFF。

### 前端结构

```
apps/mom-*-ui/           # 16 个业务应用（结构完全同构）
├── src/api/<域>/<实体>.ts    # 统一 fetchList/getObj/addObj/putObj/delObjs 命名
├── src/router/backEnd.ts    # 后端菜单动态路由（import.meta.glob 动态加载 views）
├── src/directive/authDirective.ts  # v-auth / v-auths / v-auth-all 按钮权限
packages/                  # 共享包（components 50+/biz-components 17/request/hooks/stores/effects）
internal/                  # lint-configs / vite-config / tailwind-config / tsconfig
template/                  # 新模块脚手架
```

## 四、设计亮点

### 后端
1. **单体多数据源 AOP 路由**（`mom-boot/.../datasource/PackagePathDataSourceAspect.java`）：拦截 `cn.com.tltim.mom..service/mapper/impl` 按**包前缀最长匹配**切数据源，优先尊重 `@DS` 注解，处理 JDK/CGLIB 代理类名还原——"微服务转单体不重构业务"的教科书实现
2. **策略工厂模式**：`FlowFactory.getHandler(billType)` 按 `support()` 分发；`BarcodePlugin` 条码规则插件
3. **编码规则中心化**：`MdmSequenceHandler + DbSeqBuilder`，业务号由序列表 + 日重置 + 前缀/位长配置驱动，Feign 跨模块复用
4. **统一三件套**：`R<T>` 统一包装 + `@SysLog` 操作日志 + `@PreAuthorize("@pms.hasPermission('xxx:yyy')")` 权限码，配合前端 v-auth 按钮级权限闭环
5. **安灯状态机 + 延迟消息**：AndonStateEnum + DelayQueue 延迟通知（超时未处理升级提醒）
6. **大屏 BFF 专用 DTO**：每个大屏建专用 DTO（20 个），SQL 直查 PG 多 schema，避免通用 DTO 丢字段

### 前端
1. **`@mom/request` 请求封装**（`packages/effects/request/`）：自动注入 Authorization/TENANT-ID/factory-code 头、AES 报文加密（Enc-Flag）、**424 令牌过期统一弹窗**、**401 刷新令牌队列**（isRefreshing 锁 + 等待队列，避免并发重复刷新）
2. **`useTable` 表格 Hook**：88+ 页面复用，分页/排序/加载/错误兜底/导出一体化，页面平均 150 行完成 CRUD
3. **后端驱动路由**：菜单接口 → 动态组件映射 → tagsView/面包屑缓存，刷新不丢路由；meta 约定覆盖外链/内嵌/缓存场景
4. **大屏数据配置中心 v2**：schema 驱动 → localStorage 持久化 → **storage 事件跨标签页同步** → withTransient 瞬态标记隔离接口数据与人工配置（防 v1 的"接口数据污染配置"）
5. **验收 Mock 工作流**：VITE_USE_MOCK 开关 + src/mock/，新页面先 Mock 交付、后端就绪切真实接口
6. **monorepo 依赖治理**：pnpm catalog 统一版本 + turbo 缓存 + exports 直指源码（dev 免构建）

## 五、踩坑经验清单

### 后端
| 坑 | 根因 | 修复 |
|---|---|---|
| 单体打包后 33 个页面 404 | 12 个 biz 模块误启用 spring-boot repackage，controller 被塞进嵌套 BOOT-INF | 禁用 repackage（skip + phase none） |
| fat-jar 启动 NoSuchFieldError: mdcAdapter | tlog-adapter 反射 logback mdcAdapter，Spring Boot 3.3.13 升 logback 1.5 类结构变动 | Python 脚本以 ZipInputStream 顺序流重打 jar 剔除（不能用 unzip→zip，会破坏 loader 偏移） |
| 2GB 大 jar EOCD 偏移 bug | pigx 父 pom 的 spring-boot 3.3.3 | 覆盖升级 3.3.13 |
| 高并发错误率 16-61% | cnyt 数采库不可达时连接阻塞拖垮线程池 | 不可达时禁用数据源（CNYT_DATASOURCE_ENABLED） |
| 大屏字段丢失/空白行 | PG 行接口 SQL 别名未加引号被折叠小写；DTO 字段不全 | 专用 DTO + 双引号别名 |
| 登录 500 | bigscreen OAuth 客户端提交 additionalInformation 被存成空对象 | 字段平铺由后端自拼 |
| 角色菜单绑定被覆盖 | /admin/role/menu PUT 是整体替换 | 先 GET 取并集再提交 |
| pg_dump -j 4 与 -Fc 冲突 | 备份脚本 bug | 改 -Fc -Z5 + SHA256 校验 |
| 运行的是旧构建 | 代码提交了但服务未重建 | 重建重启即修复一批契约问题 |
| nginx 无 /admin/ 代理 | 大屏经 80 端口不可达 | 补代理规则 |

### 前端
| 坑 | 根因 | 修复 |
|---|---|---|
| pnpm 8.15 读不了 lockfile v9 | 全局 pnpm 低于项目要求的 9.7.1 | corepack/升 pnpm@9 |
| mes 与 qms 端口同为 10001 | 配置复制未改 | 不能同时 dev |
| 菜单点击跳错 URL | admin 的 backEndComponent() 缺 matchBigscreenMenu 分支；router.resolve() 落到 admin 的 base | 逻辑对称搬到 admin，isLink 显式拼前缀 |
| 后端 500 变前端 JS 崩溃 | err.data?.msg 对 err.data=null 无保护 | 可选链 |
| null 数据展开崩溃 | 后端返回 null 时 res.data ?? [] 缺失 | 35 处加固 |
| 大屏首屏显示旧缓存值 | v1 配置 key 期间接口数据被持久化污染配置 | 换 v2 key + withTransient 瞬态标记 |
| 认证接口必须 form 编码 | OAuth2 协议 4.3.1 要求 form 而非 JSON | FORM_CONTENT_TYPE 常量 + 注释引用 RFC 6749 |

## 六、可复用经验

1. **"交接文档 + PROGRESS.md 续接"工作流**：任务化 + 每会话回填 + A/B/C 三类阻塞项分级，多会话智能体协作范本
2. **数据库脚本日期目录规范**：`initialization/` + `YYYY-MM-DD/` 可重复执行脚本，规避环境漂移
3. **Mock 先行 → 真接口切换**的验收节奏：前后端并行交付
4. **请求层"三头一密"**：Token + Tenant + FactoryCode 自动注入、AES 加密、424/401 统一处理
5. **入口应用行为一致性检查清单**：影响菜单渲染的逻辑必须在所有入口 app 同步（对比"菜单点击 URL"与"直开 URL"）
6. **单体多库 AOP 路由**：包前缀→库映射 + 注解优先 + 代理类名还原
7. **构建产物自检**：CI 增加"无嵌套 BOOT-INF"断言（repackage 事故教训）

## 七、改进建议

| 优先级 | 建议 | 理由 |
|---|---|---|
| 高 | 引入 Flyway/Liquibase 替代手写日期目录 SQL | 已有 2 处 schema 漂移，人工执行靠不住 |
| 高 | 前后端契约测试/共享 DTO | 大屏对接反复出现字段名不一致、结构错位 |
| 高 | 构建产物自检纳入 CI | 2026-08-18 repackage 事故 |
| 中 | 补单元/集成测试 | 16 模块几乎无测试 |
| 中 | Redis 持久化 + 主从 | 生产无持久化且与潍坊单体共用，单点风险 |
| 中 | 统一 useTable 与 vxe 两套表格体系 | 混用增加维护成本 |
| 中 | 修复前端 engines 声明 + 补 .nvmrc | node >=16 是过时信息 |
| 低 | 环境变量去敏 | .env 提交了加密 key 和 OAuth 客户端密钥 |
| 低 | k8s 清单重写或废弃 | 文档与实际部署（WinSW 单机）严重不符 |
| 低 | 补全 lint-staged 配置 | husky 调用了但仓库无配置文件 |

## 关键文件索引

| 关注点 | 路径 |
|---|---|
| 多数据源路由 | `cwjt/mom-boot/src/main/java/cn/com/tltim/datasource/PackagePathDataSourceAspect.java` |
| 单体安全配置 | `mom-boot/.../bootstrap/MomBootSecurityServerConfiguration.java` |
| 公共服务（序列/消息/流程/条码） | `mom-common/mom-common-biz/src/main/java/cn/com/tltim/mom/common/{seq,message,flow,barcode}/` |
| 前端请求封装 | `cwjt_front/packages/effects/request/src/request-client/defaultRequest.ts` |
| 表格 Hook | `cwjt_front/packages/effects/hooks/src/table.ts` |
| 后端驱动路由 | `cwjt_front/apps/mom-mdm-ui/src/router/backEnd.ts` |
| 大屏配置中心 | `cwjt_front/apps/mom-bigscreen-ui/src/bigscreen-data/index.js` |
| 交接文档中心 | `cwjt/docs/handover/README.md` |
| 进度跟踪 | `cwjt/PROGRESS.md` |
