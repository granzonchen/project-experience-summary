# 行业二开与依赖治理 —— 4 个 Odoo 项目合并简评

> 分析对象：`D:\projects\projects-old\lims`（Odoo14 LIMS，32 addon，git 4513 提交至 2021-06）；`D:\projects\projects-old\xinyi\createx`（Odoo14 校服行业二开，138 addon，至 2022-11）；`D:\projects\projects-old\odoo14addons`（21 个通用模块，至 2022-10）；`D:\projects\projects-old\rfmt`（煤炭进销存，5 模块，至 2021-08）
> 分析方式：只读代码勘察（2026-09）

## 一、项目群背景

同属 Odoo 14 时代的行业二开：实验室 LIMS、校服产供销、质量/知识通用件、煤炭购销。业务各异，但正好覆盖生态二开三大开放题：**依赖治理、通用件复用、行业建模**。

## 二、各项目关键模式

**lims —— 审批配置化 + 全局拦截**
- 自研 web_approval 把审批流做成可配置模型（model_id + condition 域 + 节点 + 动作，models/approval_flow.py），并用猴子补丁接管 BaseModel.write/create/unlink 施加审批约束（models/model_write.py：`write_origin = models.BaseModel.write`）。【金】"对象生命周期约束配置化"换栈成立；【坑】全局补丁让一切 write 付费、升级高危。
- 按单据链分模块：car_entrust→car_outsource→car_test_report，service_lims 聚合（各 `__manifest__.py` depends）。【留】
- 表头冻结等 UX 打补丁独立成模块且反复返工（max_web_freeze_list_view_header；git：`[fix] 表头固定问题修复`、`[fix]表格首列冻结及滚动条优化`）——UX 微调是二开成本大头。

**xinyi —— 混装失控样本**
- 138 addon 四源混装：企业版移植（account_accountant、stock_barcode、theme_clarico_vega）、OCA（base_tier_validation 系列）、商业主题（emipro_theme_* 15 个）、自研（oscg_xy_* 报表、delivery_kdn 六承运商族）。
- 版本字段漂移铁证：auth_signup_sms "15.0.1"、chatter_position_cqt "13.0.1.0.0"、xmlrpc_log "15.0.1.0" 混在 14 仓库 → version 不可作基线。【金】依赖清单是第一道门禁，混装必须自建来源清单。
- 核心行为修正独立成 fix 模块（stock_procurement_fix、mrp_procurement_fix，被 xinyi_customized 依赖）。【留】叠层不改上游。
- wms_sync 在 create 内联同步外部 WMS 且 ownerUserId='2301' 硬编码（models/product.py）。【坑】外部写进主事务。

**odoo14addons —— 包裹不改上游**
- OCA 原样引入（mgmtsystem 全套、quality_control_oca，git 仅单条 add 提交）；自研需求以 _ext 依赖包裹（module_auto_update_ext→module_auto_update，按 checksum 自动升级，models/auto_update.py）。【金】上游治理正解，与 xinyi 形成同代对照。

**rfmt —— 行业模块空壳化**
- coal_mrp / coal_sjb / coal_stock 的 models/purchase.py 三份字节级相同（md5 1fd70c0a…），均为对 api-test.test027.com 的 33 行 stub（注释停在"认证参数缺失"）。【坑】脚手架批量复制把"未完成"伪装成"已建三模块"；真模型只在 coal_purchase。行业深度在配置与流程，代码量/模块数均不可见（推断，依据实测薄码）。

## 三、共性观察与教训

1. **依赖治理三级分化**：混装无清单（xinyi）→ 原样+_ext（odoo14addons）→ 复制成三胞胎（rfmt）。【金】任何插件生态，先机器校验来源/版本/depends，再谈安装。
2. **通用件"各找各的"**：甘特图三套并存（xinyi web_gantt、odoo14addons micat_web_gantt_view、lims web_gantt_native）；审批两条路线（xinyi 复用 OCA tier_validation vs lims 自研引擎）。沉淀一次内部登记，胜过每项目重新选型。
3. **行业建模三种姿态**：lims 单据链完整（值得抽【留】）、xinyi 靠核心+fix 层+集成族、rfmt 空壳——工作量被"外部对接+UX 补丁"吃掉（xinyi 快递/SMS/微信/WMS 全家桶、lims 表头冻结多轮返工）。

## 四、若用现代栈重做

- 依赖：lockfile + 私有源 + CI 校验 depends 与来源清单，装前门禁。
- 审批：独立工作流服务/状态机，永不全局补丁 ORM 基类。
- 集成：防腐层 + 超时重试（rfmt stub 的 timeout=3 是唯一做对的点）+ 凭证全走配置（create 内联同步改 outbox/事件）。

## 五、证据索引（敏感信息只记位置）

- lims\web_approval\models\{approval_flow,model_write}.py；lims_open_interface\controllers\eim_api.py（凭证走 config_parameter）；selenium_tests\；git log fix 系列
- xinyi\createx\xy.conf（admin_passwd 哈希、db_password 明文）【敏感】；createx\test_webs.py（内含凭据文本）【敏感】；createx\sms_zhutong\controllers\_utils.py（密码在系统参数）；wms_sync\models\product.py；各模块 `__manifest__.py` version 字段
- odoo14addons：git log；module_auto_update_ext\models\auto_update.py
- rfmt：coal_mrp|coal_sjb|coal_stock\models\purchase.py（md5 相同三份）
