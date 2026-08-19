# jt-app（生产管理 App / wms-phone-app）- 项目经验总结

> 分析对象：`D:\projects\jt-app`（uni-app 2.x + Vue 2，git 59 提交，dev 分支）
> 分析方式：只读代码勘察 + git 历史分析
> 交付形态：Android APK 为主（原生打包 + wgt 热更新），微信小程序已弃用，H5 仅调试

## 一、项目背景

嘉腾（智能制造集团，git 命名空间 Intelligent-manufacturing-group/jtyy）的**生产管理 App**，对接 JeecgBoot 微服务（多租户），覆盖五大业务域：**WMS 仓储 + MES/MDM 生产执行 + QMS 质量 + TPM 设备 + 车间库**。与 lx-wms-app 高度同源（同 JeecgBoot、同"通知单→单据→出入库"业务模型、同内网 git 组），疑似集团下多工厂/多客户的同模板衍生 App。

关键识别特征：uni-app 工程（`pages.json`/`manifest.json`/`uni.scss`/`uni_modules/` 在根目录），**代码直接放根目录（非标准 src 布局）**。

## 二、技术栈

| 层 | 选型 |
|---|---|
| 框架 | uni-app 2.x + Vue 2.6.11（选项式 API），HBuilderX vue-cli 插件模式 |
| UI 库 | uView UI 1.4.6（easycom 自动引入） |
| 请求库 | flyio 0.6.2（`dist/npm/wx` 适配器，App/H5/小程序三端通用） |
| 状态管理 | Vuex 3.4 |
| 加密 | crypto-js 3.3.0（AES-CBC） |
| 图表 | u-charts（自封装 mes-charts/mes-column） |
| 构建 | HBuilderX 可视化打包；scripts 仅 `dev:h5` |
| 规范工具 | **完全没有**（无 eslint/prettier/husky/commitlint/.env） |
| 包管理 | npm/yarn/cnpm 混用（双 lock 文件共存） |

## 三、架构与模块

### 目录结构

```
jt-app/
├── main.js / App.vue / pages.json / manifest.json
├── config/        # url.js(host) · bootstrap.js · aesEncrypt.js(冗余)
├── utils/         # request.js(fly封装) · tools.js · util.js(AES) · checkPermission.js
├── store/         # Vuex：token/host/roles/shiftInfo/print
├── api/           # login/common/wms/mes/qms/tpm/mdm + apiConfig/config-dev.js
├── serve/         # ★ 业务服务门面层（二次封装 api，页面只调 serve）
├── mixins/        # PageMixin(分页) · FormMixin(表单+幂等) · ScanMixin(扫码)
├── components/    # 60+ 业务/通用组件
├── plugins/       # APPUpdate：wgt 热更新（plus.nativeObj 手绘弹窗）
└── pages/         # 107 个注册页面（135 个 .vue，28 个未注册死页）
```

### 业务模块（pages.json 107 页）

| 域 | 核心页面 |
|---|---|
| WMS 仓储 | 库存盘点(5页)、实时库存、移库、质检计划、采购/外协/生产出入库单（通知单→单据→出入库） |
| QMS 质量 | 采购/成品/工序三类质检 + 不合格品管理 |
| MES/MDM | 我的任务 + 报工、安灯、工艺文件 |
| TPM 设备 | 工单/维修/保养/点巡检/报修、派工、备件申领退回 |
| 车间库 | 领料出入库、退料出库 |

### 请求封装（utils/request.js）

- flyio 单例，baseURL **动态取 store 的 host**（运行时用户配置 IP:port，`http://` 前缀拦截器里拼）
- 拦截器自动加 `X-Access-Token` + `Tenant-Id`（JeecgBoot 标准）
- **错误分级**：网络错误不弹 toast 交给页面处理，HTTP 错误按码弹文案，401 清 token reLaunch 登录页，500 跳异常页
- 幂等 token 接口已实现但请求头注入被注释（防重提交未落地）

### 权限控制（三层）

1. 登录态：token 存 storage + Vuex
2. 按钮/菜单：`$checkPermission(key)` + v-if 控制
3. **模块级（租户级）**：`getAppIndexShow` 返回当前租户启用模块（wms/mes/qms/tpm/mdm），首页过滤菜单并动态改导航栏标题（生产管理/仓储管理/生产执行管理）

## 四、设计亮点

### 4.1 PDA 双通道扫码体系（项目灵魂）

- **硬件激光**：`scanCode.vue` 用 `plus.android` 注册 BroadcastReceiver 监听厂商广播，收到码后 `uni.$emit('scan')` 全局分发，**150ms 防抖**
- **相机扫码**：`uni.scanCode({onlyFromCamera:true})`（ScanMixin/FormMixin/业务页）
- **解耦模式**：页面 `onShow` 时先 `uni.$off('scan')` 再 `uni.$on('scan')`，onHide 再 off——避免多页面同时响应
- **参数可配置化**：系统设置页可改 4 个 PDA 参数（开始/停止广播、action、数据标签），适配不同厂商 PDA（优博讯/东集等）

### 4.2 盘点 UX（check.vue 标杆页）

- 已盘列表"未盘在前"排序
- 库位/物料弹层搜索 + 无限滚动 + 下拉刷新三件套
- 提交成功自动清空进入下一单（连续盘点）

### 4.3 其他

- **JeecgBoot Online 报表驱动查询**：先 `onlineGetRpColumns` 拿报表配置 id 再 `onlineGetData` 取数据，页面零写死列
- **PageMixin 列表页模板**：loadmore/loading/nomore 三态状态机 + onShow 自动刷新 + onPullDownRefresh 重置 + stopFresh 钩子，30+ 页面复用
- **serve 门面层**：api（URL 映射）与 serve（业务编排）分层，接口变更隔离
- **多租户动态菜单 + 动态标题**：一套 App 多客户复用
- **wgt 热更新**：版本检查 → plus.downloader → plus.runtime.install，弹窗全部 plus.nativeObj 手绘（含文字换行 drawtext）；iOS 走 App Store
- **环境切换 UI**：登录页齿轮弹层改 IP 一键切换（测试/生产），适合工厂实施场景

## 五、踩坑经验清单

### 明确 bug（可复现风险）
| 问题 | 位置 |
|---|---|
| Logout 引用未定义常量 ACCESS_TOKEN（登出必崩） | store/index.js |
| Login SET_NAME 传参与 mutation 解构不匹配（state.name 永远 undefined） | store/index.js |
| 盘点已盘列表上拉拼错数组 + 状态值写死字符串 | check.vue |
| 首页 showable 权限数组不按 card 重置，跨模块累积 | pages/index/index.vue |
| util.js 加密 Base64 分支引用未定义变量（死代码必崩） | utils/util.js |
| 登录返回码 0/200 三套判断并存（后端码不统一是根源） | request.js/login.vue/store |
| matPurchase 8 个页面未注册 pages.json（死代码） | pages/wms/matPurchase/ |
| 登录页默认账号密码硬编码（安全隐患） | login.vue |

### git log 真实踩坑
- **服务器 IP 持久化**："只有首次打开时需要设置 ip"——早期每次启动重设 IP，改为 onLoad 判断无 host 才 setIP
- **扫码值必须结合上下文校验**："新增扫描库位时根据仓库进行校验，属于该仓库则赋值，否则提示"——PDA 业务通用坑
- **扫码→库位赋值链路**曾因全局 scan 事件时序问题失败（onShow 先 off 再 on 是解）
- **报工数量与完成态联动**是反复修的业务痛点（2025-02 仍"调整报工逻辑"）
- uni-app 里 uView 表单校验/异步赋值时序问题（"异步修改"提交）

### 工程坑
- **JVM 崩溃日志入仓**：hs_err_pid*.log / replay_*.log（HBuilderX 开发期崩溃残留）
- **双 lock 文件 + 多包管理器**：依赖一致性无保障
- **config/aesEncrypt.js 内嵌 2000 行 crypto-js 源码**：冗余无人维护
- **环境地址混乱**：config/url.js 残留 127.0.0.1 地址，真实地址靠用户手输 IP，配置散落多处互相覆盖
- **request.js baseURL 硬拼 `http://`**：换 https/域名需改代码
- **无 keep-alive**：onShow 每次都重置分页重拉，弱网体验差
- **幂等防重未闭环**：token 拿了没注入
- **uni.$on('scan') 漏 off** 会重复触发（双监听场景需小心）

## 六、可复用经验

1. **PDA 扫码三件套**：可配置广播参数（storage 持久化）+ 全局 scan 事件（emit/on/off 成对）+ 150ms 防抖——可直接复制到任何 PDA 项目
2. **扫描上下文校验**：扫码结果立即按业务上下文（仓库/单据）校验归属，不通过即提示
3. **PageMixin 分页状态机**：uni-app 列表页标准答案
4. **serve 门面层**：api 与业务编排分层，接口变更有隔离层
5. **Online 报表驱动下拉**：后端可配置查询项，前端免开发
6. **多租户动态菜单 + 动态标题**：`getAppIndexShow` 模式
7. **wgt 热更新插件**：整套（版本检查/进度弹窗/强制更新/重启）可提取为通用插件
8. **环境切换 UI**：登录页改 IP 弹层，比 .env 更适合工厂实施场景

## 七、改进建议

**优先修复**：Logout 登出必崩（P0）→ SET_NAME 不匹配（P0）→ 盘点数组/状态值（P1）→ 权限数组累积（P1）→ 死代码清理（P1）→ 返回码统一（P1）→ 移除默认账号（P2）→ 清 JVM 日志/双锁/内嵌 crypto-js（P2）

**工程化**：
1. 迁移 uni-app 3.x（Vite）：2.0 + node-sass 栈 2026 年难维护（node-sass 4.x 在新 Node 装不上）；至少固定 Node 版本提交 .nvmrc
2. 建立规范链：eslint（uni 插件）+ prettier + husky + commitlint
3. 统一环境配置：.env 系列 + VITE_API_HOST，登录页 IP 覆盖仅兜底
4. 防重提交闭环：放开 IDEMPOTENT-TOKEN 头注入（骨架已有）
5. 扫码能力收敛：三套并一套 composable（含防抖/空码/重复码过滤/震动反馈）
6. **离线容错**：盘点等高频提交加"本地草稿 + 重试队列"，仓库现场弱网是常态
7. 路由守卫：onLaunch 登录态检查（现在靠 401 兜底首屏会闪）
8. 版本管理：versionCode 已 138，建议 CI 自动 +1 并管理 wgt 包

## 关键文件速查

| 用途 | 文件 |
|---|---|
| 请求封装 | `utils/request.js` |
| PDA 扫码 | `components/scanCode/scanCode.vue`、`pages/my/setting/setting.vue`、`mixins/ScanMixin.js` |
| 列表模板 | `mixins/PageMixin.js` |
| 更新机制 | `plugins/APPUpdate/index-new.js` |
| 盘点标杆页 | `pages/wms/warehouseIn/inventoryCheck/check.vue` |
| 首页多租户菜单 | `pages/index/index.vue` |
| 搜索组件 | `components/top-search/top-search.vue`（声明式 queryObjs） |

## 与其他项目的关系

- **与 lx-wms-app / lx-wms-app-dev / vue_app(mom-app) 同源**：wms-phone-app 模板系，多工厂/多客户衍生；本仓库含大量可逆向复用的 PDA 经验
- **与 jiateng-pc 同属嘉腾（jtyy）集团**：jiateng-pc 是 PC 端（JeecgBoot 系），jt-app 是其移动端（uni-app），业务模型"通知单→单据→出入库"同构
