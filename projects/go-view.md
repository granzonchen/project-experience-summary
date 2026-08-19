# GoView 大屏可视化编辑器 - 项目经验总结

> 分析对象：`D:\projects\go-view\go-view`（master-fetch 分支，v2.2.8）
> 分析方式：只读代码勘察 + git 历史分析

## 一、项目背景

基于开源 GoView（gitee.com/dromara/go-view）二次开发的大屏可视化编辑器，采用"拖拽组件 → 配置数据/样式 → 保存 → 预览"的低代码制作流程。开源版为纯前端 demo（数据存 localStorage），**master-fetch 分支接入真实后端**（项目列表、保存/加载、登录、发布均走后端接口），二次开发改造量 111 个文件、+1818/-677 行。

核心改造点：
- 项目列表/删除/发布走后端（`src/views/project/items/components/ProjectItemsList/hooks/useData.hook.ts`）
- 保存/加载走后端，节流 3s 自动保存 + html2canvas 生成缩略图（`src/views/chart/hooks/useSync.hook.ts`）
- 预览走后端，未发布项目跳提示页（`src/views/redirect/UnPublish.vue`）
- 登录对接 + axios token 注入 + 401 跳转（`src/api/axios.ts`）

## 二、技术栈

| 依赖 | 用途 |
|---|---|
| Vue 3.2 + vue-router + pinia 2 | 基础框架，hash 路由 |
| naive-ui 2.34 | 全部 UI |
| echarts 5.3 + vue-echarts + liquidfill/wordcloud/stat | 图表渲染，按需引入 |
| monaco-editor | 代码编辑器（数据过滤器、事件函数、SQL） |
| vue3-sketch-ruler | 画布标尺 |
| vuedraggable / keymaster / html2canvas / mitt / three / gsap | 拖拽 / 快捷键 / 截图 / 事件总线 / 3D / 动画 |
| vite 4.3 + vite-plugin-compression/mock + plop | 构建、gzip、mock、代码生成 |
| husky + commitlint + eslint + prettier | 工程化规范 |

## 三、架构与核心模块

### 目录分层

```
src/
├── api/            axios 封装 + 按模块拆分的接口
├── packages/       ★ 图表组件库（核心，Charts/Decorates/Informations/Tables/Photos/Icons 六大类）
├── store/          pinia（chartEditStore 画布核心、chartHistoryStore 历史、chartLayoutStore UI 布局）
├── hooks/          组合式函数（数据获取、数据池、缩放、主题、生命周期）
├── views/          chart(编辑器) / preview(预览) / project / login
├── settings/       designSetting、chartThemes、httpSetting
└── utils/          工具（含函数序列化 JSONStringify/JSONParse）
```

### 状态管理设计（8 个 store）

- `chartEditStore`（1021 行，核心）：画布属性、组件列表、所有组件操作动作（增删改移、层级、分组、复制粘贴、撤回前进）
- `chartHistoryStore`：**操作记录式历史**（非快照式），backStack/forwardStack 双栈 + 动作类型枚举，`Object.freeze` 冻结记录优化性能
- `chartLayoutStore` / `designStore`：UI 布局态和主题，localStorage 持久化，与业务数据分离
- 保存时只导出业务数据：`getStorageInfo()` 仅取画布配置/组件列表/全局请求配置三块

## 四、设计亮点

### 4.1 图表组件配置化注册体系（本项目最核心模式）

每个图表组件 = 一个独立目录的 5 件套：

```
BarCommon/
├── index.ts    # 组件元数据 ConfigType（key/chartKey/title/category/image）
├── config.ts   # 配置类：继承 PublicConfigClass，导出默认 echarts option
├── config.vue  # 右侧配置面板（公共 SettingItem 拼表单）
├── index.vue   # 画布/预览渲染组件
└── data.json   # 默认 dataset
```

- 注册链路：`import.meta.glob` 批量扫描 → `createComponent()` 动态 import + **Map 缓存** → 运行时 `window['$vue'].component(...)` 动态注册
- `redirectComponent` 机制：图片/图标类组件复用其他目录配置类，避免重复代码
- **新增图表零注册成本**：新建目录 + 5 个文件即自动接入面板/拖拽/渲染/配置

### 4.2 ECharts 三层封装

1. `PublicConfigClass` 公共基类：统一注入 id、attr、styles、status、request、events
2. `mergeTheme`：`includes` 白名单声明"哪些配置段跟随全局主题"，`pick + merge` 浅合并
3. 渲染组件：按需 `use([...])`、canvas 模式按 devicePixelRatio 计算分辨率、`replaceMerge` 解决 dataset 变更后 series 不更新

### 4.3 拖拽/缩放（useDrag.hook.ts，392 行）

- **画布坐标与屏幕坐标分离**：所有拖拽计算 `/scale`，数据永远存画布坐标，显示层才乘 scale——缩放下不漂移的关键
- 边界约束预留 50px 防拖出画布；8 锚点缩放用 point 字符串正则判断方向
- 四象限框选 + 全包含判定（纯数学，无 DOM 依赖）
- 历史记录只在真正移动后记录（mouseup 过滤 offset 为 0 的项）

### 4.4 数据源三层模型

- 组件级请求：watch requestParams 变更自动重新请求 + 轮询
- 全局数据池：**mitt 风格 Map 订阅**（Map<id, callback[]>），请求一次广播所有订阅者，避免 N 组件 N 请求
- 请求参数动态化：支持 `javascript:` 前缀动态参数函数、URL 模板字符串插值

### 4.5 组件联动

- 事件函数存字符串，`useLifeHandler` 用 `new Function` 动态生成
- **参数改写 + deep watch 模式**：A 图表点击 → 改写 B 的 requestParams → B watch 触发自动刷新，解耦且天然支持撤销
- 用 `key in Params.value` 判断参数存在性（value 为 null 时的经典坑）

### 4.6 其他

- **函数字符串序列化**：JSON replacer/reviver 处理 function，配置可完整存后端、可导入导出
- 预览 4 种缩放模式（等比留白/横向滚动/纵向滚动/拉伸）拆成独立 hook，统一 `calcRate + windowResize + unWindowResize` 三件套
- 右键菜单声明式定义、快捷键双平台键位表（⌘/ctrl）、类 BEM 的 SCSS mixin 作用域隔离

## 五、踩坑经验清单

| # | 坑 | 修复方案 |
|---|---|---|
| 1 | 画布宽高用 `width*2`，低于 1920px 拖不动；改宽高滚动条不变 | 宽用 `window.innerWidth * 2` 动态计算、高度独立，scale watch 统一 `canvasPosCenter()` |
| 2 | 动态返回 dataset 字段数变化时 series 不自动适配 | watch option.dataset 计算 dimensions 差值，动态 splice/push series + `replaceMerge: ['series']` |
| 3 | 拖组件到配置面板后编辑器卡死 | `@dragend` 没加括号，Vue 把 event 当函数调用；改 `dragendHandle()` |
| 4 | 拖拽未移动也记入历史 | mouseup 过滤 offsetX===0 && offsetY===0 的项 |
| 5 | window.opener 非 window 时 addEventListener 报错 | 先判断 opener 类型再挂监听 |
| 6 | 交互 value 为 null 时参数永远更新不了 | 用 `key in Params.value` 替代值判断 |
| 7 | 数据池订阅项是 ref，直接使用是 undefined | 取 `.value` |
| 8 | 请求初始化会请求两次 | watch requestParams 控制 immediate 与 fetchFn 调用时机 |
| 9 | 旧版本配置缺字段时 setOption 报错 | merge 前判空/补默认值 |
| 10 | 缩放画布时标尺重绘报错 | reDraw 用 throttle 20ms + v-if 重建 |
| 11 | 三维地球无法被 html2canvas 截图（WebGL 跨域污染） | 截图时单独处理 |
| 12 | 保存时异步组件注册未完成导致数据不完整 | updateComponent 按 percentage===100 完成标记 |
| 13 | 语言切换导致 dataSyncFetch 重复执行、图层重复 | 重进编辑器先清空 componentList |
| 14 | 弹窗打开时快捷键误触复制/删除 | setCopy 判断 modal body 存在则跳过 |
| 15 | vue3-sketch-ruler 无 Vue3 官方版 SCSS 报错 | 样式全部用原生 CSS 覆盖 |
| 16 | iconify 影子组件编译报错 | vite vue 插件 `isCustomElement: tag => tag.startsWith('iconify-icon')` |

## 六、可复用经验

1. **配置化组件注册体系**（元数据 + 配置类 + 配置面板 + 渲染组件 + glob 自动扫描 + Map 缓存 + 运行时注册）——任何"物料/可视化搭建"类产品的模板，`redirectComponent` 消除重复
2. **操作记录式撤销/重做**：存"动作 + 操作对象"而非整页快照，配合 `Object.freeze` 防篡改、历史上限截断，比快照式省内存
3. **数据池发布订阅**：请求一次广播多次，避免重复请求
4. **跨组件"参数改写 + deep watch"联动模式**：不改对方数据，改请求参数触发对方自刷新
5. **函数字符串序列化**：JSON replacer/reviver 处理 function（注意 XSS 风险）
6. **echarts 主题白名单合并**：`includes` 声明哪些段跟随主题，避免深合并覆盖引用
7. **画布/屏幕坐标分离**：数据存画布坐标，显示层 CSS transform，缩放不污染数据
8. **store 拆分粒度**：UI 布局态 / 业务数据 / 历史记录分离，持久化只选业务数据
9. **vite 构建期坑**：`build.brotliSize` 在 vite4 废弃改 `reportCompressedSize`；vue-i18n alias 替换 cjs 消除警告

## 七、改进建议

- **架构**：`new Function` 执行用户代码无沙箱，XSS 风险高，建议白名单校验 + CSP；`chartEditStore` 1021 行过重，按领域拆 composables；`window['$vue']` 全局挂载类型安全弱，建议 provide/inject
- **性能**：画布整树响应式更新，组件 >50 会卡，建议 position 高频变更 rAF 合并 + shallowRef；`updateComponent` 串行 await 逐个 import 慢，建议并发加载；html2canvas 主线程截图可能白屏，考虑分块
- **工程化**：多处 `@ts-ignore`，建议 zod 校验后端返回结构；依赖版本陈旧（vite4/TS4.6），Vue3.4+ defineModel 可简化 config.vue；无单元测试，至少为 useDrag 坐标计算/分组逻辑补单测；plop 增加图表组件模板（一键生成 5 件套）

## 关键文件速查

| 关注点 | 文件 |
|---|---|
| 组件注册体系 | `src/packages/index.ts` |
| 组件公共基类 | `src/packages/public/publicConfig.ts` |
| echarts 封装 | `src/packages/public/chart.ts` |
| 拖拽/缩放 | `src/views/chart/ContentEdit/hooks/useDrag.hook.ts` |
| 历史记录 | `src/store/modules/chartHistoryStore/` |
| 数据请求 | `src/api/http.ts`、`src/hooks/useChartDataFetch.hook.ts` |
| 组件联动 | `src/hooks/useChartInteract.hook.ts` |
| 保存/加载 | `src/views/chart/hooks/useSync.hook.ts` |
| 预览缩放 | `src/hooks/usePreviewScale.hook.ts` |
