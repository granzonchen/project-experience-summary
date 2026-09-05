# 模板化移动端集群：维修/配件/商城/砍价/Flutter/BLE

> 分析对象：`D:\projects\projects-old\` 下 maintenance、parts_maintenance、hn_mall→hn_mall_ext、bargain_shop、feng-ji、bluetooth\BluetoothLeGatt（2020~2022 归档）
> 分析方式：只读代码勘察（2026-09）

## 一、项目群背景

六个移动端小项目：两个维修/配件业务 app（uni-app）、一对原生小程序商城、一个砍价商城模板、一个 Flutter 学习拼盘、一对 BLE 学习代码。共性：模板起步、单人短周期、无长期维护。

## 二、各项目关键模式

- **maintenance**（uni-app+ThorUI 维修工单）：真实业务仅 3 页（待维修/维修中/我的），后端是 Odoo（`common/odooApi.js`，git 提交"完善odoo api"×3）；ThorUI demo 页骑在生产包里。【留】业务薄壳 + 通用后端 API 封装的组合是模板项目里唯一可迁移的骨架。
- **parts_maintenance**（ColorUI 配件商城）：README 自述"电商模板"，全流程页面（首页/购物车/结算/收银台）齐备，git 历史全是"修改了XX页面"级修补——按页补丁而非抽组件。【弃】无可迁移增量。
- **hn_mall→hn_mall_ext**（原生小程序商城迭代对）：两仓结构完全同构，diff 仅 10 个文件——ext 删除 `common/odooApi.js/odooResponse.js`（后端从 Odoo 迁走）+ 分类页改版 + 换 AppID。迭代方式=整仓复制，两仓都只有 "Initial Commit" 一个提交。【金】反例：无增量提交的复制迭代，演进决策（换后端）无法追溯、改动不可合并。
- **bargain_shop**（it120/fire-shop-lite 系砍价商城）：README 即"快速预览/扫码体验"，SaaS 后端全托管，纯模板无自有沉淀。【弃】一句话：SaaS 模板试玩，无代码层价值。
- **feng-ji**："风机物联网"名义，实际 100 个 dart 文件是多个 Flutter UI kit 拼盘（hotel_booking/fitness_app/design_course 并存）。【弃】学习代码。
- **bluetooth/BluetoothLeGatt**：微信原生 BLE demo 页 + Android 官方 BLE sample 拷贝。【弃】官方示例，无增量。

## 三、共性观察与教训

- **模板起步快，同质化真发生**：6 个中 5 个是模板/示例；且 ThorUI demo 页混入生产 app 在 maintenance、zhsq_app、community_ext 三处重复出现（≥2 证据，可入跨项目规则候选）。
- **真正被复用的是后端封装，不是前端组件**：`odooApi.js` 同名文件在 maintenance 与 hn_mall 间复制传播；而 ThorUI/ColorUI 各被整包复制多份，从未收敛为自有组件库——当年值得沉淀的恰是 API 封装层与电商页面组。
- **复制迭代的代价**：hn_mall→ext 与 zhsq 大屏"副本"文件是同一模式（副本当版本管理）在小程序与 Web 两端的重复，符合"≥2 项目重复"的规则准入条件。

## 四、若用现代栈重做（从简）

统一脚手架（请求层+鉴权+组件库模板包）+ 单仓多端（Tauri/uni-app x 或 Flutter）即可消掉本集群 80% 的复制；Odoo 后端换标准 REST/OpenAPI 生成客户端。

## 五、证据索引（含敏感信息位置清单）

- `D:\projects\projects-old\maintenance\common\odooApi.js`、`hn_mall\common\odooApi.js`（跨项目复制证据）；`hn_mall` vs `hn_mall_ext` diff≈10 文件
- `D:\projects\projects-old\maintenance\manifest.json`：微信 AppID 明文（ARCHIVE_INDEX.md §3 已登记，需轮换）
- `D:\projects\projects-old\parts_maintenance\README.md`（"电商模板"自述）；`feng-ji\lib\`（UI kit 拼盘）；`bluetooth\pages\`、`BluetoothLeGatt\`（官方示例）
- 未发现新增 PII/密钥泄露点（bargain_shop 的 SaaS key 走运行时 `getAccountInfoSync`，无明文）。
