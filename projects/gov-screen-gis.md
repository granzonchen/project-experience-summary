# 政务大屏与 GIS：zhsq 智慧社区项目群 + gis 单文件大屏

> 分析对象：`D:\projects\projects-old\zhsq`（268M，2021 年归档：Yii2 后端 + bigData 大屏 + uni-app 移动端 + 微信原生端）；`D:\projects\projects-old\gis.htm` + `gis_files\` + `api.md`（2021-09）
> 分析方式：只读代码勘察（2026-09）

## 一、项目群背景

网格化社会治理一体化交付（综治/党建/人口/民生/城管）：PC 管理端为 Yii2 advanced 应用（9 个业务模块），5 个数据大屏与 GIS 图层页同属后端模块视图；移动端是 uni-app + ThorUI（`community_1` 与 `zhsq_app` 两个同源仓库、不同微信 AppID）。根目录 `gis.htm` + `gis_files\` + `api.md` 是 GIS 大屏的浏览器"另存为"快照交付物（4216 行 HTML + 2.9M 资产 + 53 条接口抓包）。

## 二、各项目关键模式

1. **一个业务四种端，服务端单点复用【留】**：大屏与 PC 端共用同一 Yii2 渲染管线（大屏即 `backend/modules/bigDataAnalysis` 等模块视图，bigData 目录是渲染后另存的结果）；移动端独立两仓，微信原生端实为 ThorUI demo。前端四端互不复用、无共享请求层/组件层。
2. **"树节点=图层=接口参数"的极简图层管理【留】**：整个 GIS 大屏只有 1 个控制器 + 1 个 1040 行视图（`zhsq\community\backend\modules\gis\`）；jstree 节点 id 直接映射 `get-map-info?type=N`（网格/党建/建筑/事件四类图层），`addPolygon/removeMarkerOrPolygon` 按节点 id 增删。数据刷新全部按需 `$.ajax`，无轮询（gis.htm 0 个 setInterval，bigData 的 setInterval 仅用于跑马灯）——交互型大屏不需要定时器自愈，按需拉取即可。
3. **"另存为"快照交付形态【留】**：利——零部署演示、可离线归档、接口契约顺带留档；弊——5 个大屏各自另存为，echarts.js（952K）被复制 5 份共约 10M（`zhsq\bigData\*\echarts.js`）；快照（4216 行）与源视图（1040 行）彻底脱节，无法 diff 追溯改动。
4. **【金】敏感数据随交付物滞留**：真实居民数据进入前端目录的根因不是漏洞，而是"交付/排错产物与代码同目录归档"——接口抓包（含居民信息响应、生产服务器地址、地图服务 key 明文）、带真实数据的页面快照、UI 素材混合存放，随项目目录整体流转多年。泛化：**抓包、导出、快照类产物一律不得入代码库/归档目录；归档前必须过"脱敏+密钥清理"清单**。这与硬编码密码是同一类事故（敏感态与代码同生命周期）。

## 三、共性观察与教训

- **副本当版本管理**（≥2 处）：bigData 每屏都有"- 副本.htm"，gis.htm 与 zhsq\GIS地图.htm 两版本共存（148K vs 158K），`community_1`/`zhsq_app` 整仓复制分叉 git 历史。政务项目普遍缺 VCS 纪律。
- **组件库整包进生产**：ThorUI demo 页（基础组件/更新日志/Color）直接骑在生产 app 页面表里（`zhsq_app\pages.json`、`maintenance` 同款），包体积与审计面双输。
- **移动端薄、服务端厚**：`zhsq_app` 仅 2 个提交（init/workmgmt），业务重心全在 Yii2 端——"多端"里移动端只是薄壳，复用应发生在接口契约层而非前端代码层。

## 四、若用现代栈重做

- 大屏：ECharts/AntV + 独立前端工程，图层树用配置驱动（图层元数据 JSON 化下发）；快照需求用构建产物 + mock 数据满足，而非浏览器另存为。
- GIS：地理围栏数据（网格/建筑多边形）入库为 GeoJSON 服务化，前端按图层 id 惰性加载；交互型大屏保持按需拉取，仅热点指标配轮询+在飞守卫。
- 交付铁律：演示环境用脱敏数据集；抓包文件、真实数据导出与代码库物理隔离。

## 五、证据索引（含敏感信息位置清单）

- 四端结构：`D:\projects\projects-old\zhsq\`（community / bigData / zhsq_app / community_1 / community_ext / ThorUI-extend-uni）
- GIS 单控制器+巨型视图：`D:\projects\projects-old\zhsq\community\backend\modules\gis\views\index\index.php`（1040 行）
- 大屏资产 5 倍复制：`D:\projects\projects-old\zhsq\bigData\{index,city-management,comprehensive-control,people-livelihood,population}\echarts.js`；"副本"文件同目录
- 快照交付：`D:\projects\projects-old\gis.htm`（156K，4216 行，引用 `gis_files\`，0 setInterval）+ `D:\projects\projects-old\gis_files\`（2.9M，含 maps\）
- **敏感信息位置清单（只记位置，内容禁引用/需脱敏）**：
  - `D:\projects\projects-old\api.md`：接口抓包落盘，含**真实居民 PII**（姓名、证件类检索结果响应）、生产服务器地址与端口、第三方地图服务 key 明文——最高优先级脱敏对象；
  - `D:\projects\projects-old\gis.htm`：含"姓名/证件号"检索交互与人员信息渲染模板（前端代码层面，未发现内联 PII 数据）；
  - `D:\projects\projects-old\zhsq\bigData\`：各屏快照含真实社区统计渲染数据，归档前需评估脱敏；
  - `D:\projects\projects-old\zhsq\community_1\manifest.json` / `zhsq_app\manifest.json`：微信 AppID 明文（见 `ARCHIVE_INDEX.md` §3 统一建议：轮换）。
