# 复制改造与大屏 —— antai / antaidaping 合并简评（对照 ltc、hn_mall）

> 分析对象：`D:\projects\projects-old\antai\antai`（Odoo14 制造报工/设备/模具，18 addon，无 git，快照+2022-10 zip）；`D:\projects\projects-old\antaidaping`（uni-app 大屏：daping 源码 + antai 静态构建 + videos）；对照：`D:\projects\projects-old\ltc`（多前端副本）、`D:\projects\projects-old\hn_mall` ↔ `hn_mall_ext`（小程序克隆链）
> 分析方式：只读代码勘察（2026-09）

## 一、项目群背景

antai 为工厂场景 Odoo 二开：设备维护 antai_maintenance → 模具 antai_mould → 车间终端 antai_ccd → 大屏数据 antai_data。antaidaping 是其可视化大屏：**后端仓库零改动复用，前端新起 uni-app**（Vue2+echarts5+vue-seamless-scroll），经 restful 插件的 /api 访问 Odoo。大屏最后一次提交 2021-09。

## 二、各项目关键模式

**antai（后端）**
- _ext 叠层：antai_maintenance_ext 仅以 _inherit 追加 qr_code 等小字段（models/equipment.py）。【留】
- 聚合层有名无实：antai_data\controllers\main.py 提供 /adc/dingdan|chanliang|plan 大屏聚合端点，但 daping 前端绕开它，直接 searchRead 明细模型（pages/index/index.vue）——双轨并行。【坑】
- 运维底座意识强：auditlog、password_security、auth_session_timeout、auto_backup、app_script_cron_failure（继承 ir.cron 捕获失败并发通知，models/logs_scheduled_actions.py）。【留】
- 认证三姿势并存：MES 对接 XML-RPC+ir.config_parameter 凭证（antai_maintenance\models\product.py `_get_rpc_info`，CONFIGURATION.md 明言"代码中不含硬编码密码"）vs CCD 端点全部 auth="none" csrf=False cors="*"（antai_ccd\controller\main.py）vs 大屏前端 mounted 里硬编码管理员账密。【坑】【金】对内接口也要有默认拒绝的认证策略。

**antaidaping（大屏前端）**
- 分工范式：后端复用 + 前端新仓，仓库自含源码、静态构建产物（antai/）、演示录像（videos/）。【留】交付三件套。
- odoo_api/ 统一封装 authenticate/searchRead（src\odoo_api\odooApi.js）。
- 大屏基础三缺：5s setInterval 无在飞守卫、无超时、全项目 grep 不到 clearInterval/onUnload/beforeDestroy（pages\ccd\ccd.vue：208 起），时钟 ticker 与业务轮询混同组件；echarts 用 document.getElementById 初始化（components\index.vue:92）。【坑】——正是 R7 三件套的原始病灶。

## 三、共性观察与教训（复制改造纪律）

- **同名为 ext，两种语义**：Odoo 的模块级叠层（antai_maintenance_ext、odoo14addons 的 module_auto_update_ext）有依赖图兜底、可追溯；hn_mall_ext 是 1182 文件整库克隆、排除 .git 后仅 4 处差异（删除 common\odooApi.js/odooResponse.js、改 classify.js 与 project.config.json），且两侧 git 都只有 Initial Commit——复制即分叉、漂移不可追溯。【金】复制改造点必须清单化，副本用 diff 门禁保持自洽。
- **ltc 放大整库克隆代价**：mms-wmp / mms-wmp-back / mms-wmp-en 三份小程序副本并存（另加 pms/pes/pms_applet/pms_wewqe 多前端），多角色多语言需求被做成 N 份整库。【坑】
- antai/antaidaping 双仓分工是本批最成熟的协作，但前端绕开聚合接口说明：分工之外还要**契约管理**——大屏数据契约应收敛在 antai_data 一侧。

## 四、若用现代栈重做

- 大屏：聚合接口 + WebSocket/SSE 推送替代 5s 全量轮询；定时器随生命周期管理；图表实例 ref 化。
- 多端多语言：monorepo + 构建期变量换肤，不做整库克隆。
- 终端认证：设备令牌/短时票据替代硬编码账密；无认证端点至少加来源白名单 + 签名。

## 五、证据索引（敏感信息只记位置）

- antai\antai_data\controllers\main.py；antai_ccd\controller\main.py；antai_maintenance\models\product.py（ICP 'mes.password'）；CONFIGURATION.md；app_script_cron_failure\models\logs_scheduled_actions.py
- antaidaping\daping\src\pages\index\index.vue（mounted 硬编码管理员凭据）【敏感】；src\odoo_api\httpRequest.js（内网 IP 硬编码）；src\pages\ccd\ccd.vue（5s 轮询）
- ltc：mms-wmp、mms-wmp-back、mms-wmp-en 目录对照；hn_service\docker-compose.yml（POSTGRES_PASSWORD 明文）【敏感】，ARCHIVE_INDEX.md §3 已登记
- hn_mall / hn_mall_ext：`diff -rq -x .git` 仅 4 处；双方 git log 均仅 Initial Commit
