# 佳腾 MOM 平台（jiateng-pc）- 项目经验总结

> 分析对象：`D:\projects\jiateng-pc`（Maven 多模块 Java 后端 + 9 套前端工程，git 1023 提交）
> 分析方式：只读代码勘察 + git 历史分析
> 当前阶段：生产运行中，sharding 分支做读写分离/分库改造

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
