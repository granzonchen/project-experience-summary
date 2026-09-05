# cevt（Odoo 车队管理套件）- 项目经验总结

> 分析对象：`D:\projects\projects-old\cevt`（约 2.0G；代码提交止于 2022-09，目录 mtime 至 2022-12）
> 分析方式：只读代码勘察（2026-09）

## 一、项目背景与业务问题

CEVT（吉利-沃尔沃合资设计中心）用 Odoo 10→14 自建车队全生命周期平台：试验车预约与借用（fleet_booking/fleet_rental）、维修车间工单（mro 系）、车辆损伤与评估（fleet_vehicle_damage/fleet_assessment）、仪器管理（instrument）、合同电子签（contract_signature）。集成密度高：供应商 Excel 邮件自动入库（incoming_email_router）、Power BI 取数（fleet_assessment/models/assessment.py:127）、Jira、LDAP、Flutter 移动端（web/ 为其构建产物）。同一套 addon 复用服务多家公司（cevt/lotus/antai 各有配置与模块注册表）。

## 二、架构与技术决策

- **四仓分层**（14 代）：odooext14-base（平台扩展 55 个）→ odooext14-cevt（自研业务 82 个）→ odooext-cevt-geelyodoo（客户定制 9 个）；10 代是 214 个 addon 的单仓大杂烩。第三方（OCA web_*、muk_*、queue_job）直接 vendor 进仓。
- **多公司形态**：一个 venv + 每公司一份 conf（odoo14-venv/ 下 8 份，靠 dbfilter 隔离）+ 模块注册表 `{company}_modules.json`（addons10 下 cevt 156 个 / lotus 104 个）决定各公司装/更哪些 addon。
- **部署演进三层可见**：Windows venv+bat（开发）→ docker compose（odoo-utilities/docker/images，含 odoo10/12/14 三代镜像）→ k8s（每版本一套 yaml，含 emergency_restore.yaml、update_in_progress.yaml）。
- **CI 门禁**：GitLab pipeline 双卡点——pylint_odoo 评分徽章（pipeline/pylint.yml）+ 依赖检查（pipeline/dependency_check.yml，MR 时跑 compute_module_update_order.py 算 addon 更新拓扑序）。
- **测试**：自建 Selenium 框架（odooext14-test-base 含 handbook），业务 addon 内 `stests/` 目录 + RPC 层测试，conftest.py 统一挂测试库进 sys.path。

## 三、做对了什么（可迁移思路）

1. **【金】把升级 checklist 变成可执行脚本**。migration-scripts/migrate_130_140.py 将 OCA 迁移 wiki 逐条 codify 成"文本特征→grep/替换→附修复说明"规则，migrate_script_helper.py 每条规则内嵌修法文档。泛化：大版本升级/框架迁移先写 codemod 清单，机器筛完再人审。
2. **【金】迁移前钉死源仓库 commit hash**。migrate_cevt_specific.py 的 log_commit_hash() 与 baseline/commit_log.txt（2022/06/22 记录三仓 hash）让"从哪个基线迁出来的"永远可回溯。泛化：任何基线切换操作，先固化来源版本号进产物。
3. **【金】依赖即门禁**。util/dependency_checker.py 做 manifest 拓扑排序，compute_module_update_order.py 交叉"本次变更模块 ∩ 注册表模块"，CI 在 MR 上强制执行。泛化：插件体系的更新顺序不该靠人脑记，靠机器按依赖图算。
4. **【留】批量导入"收集-汇总-再抛错"**。odooext14-base/cron_handler/cron_logger.py：线程安全计数器累积所有行错误，写库完成后 throw_cron_error() 一次性抛 ValidationError——不因单行坏数据丢弃整批，也不静默吞错。
5. **【留】导入边界显式值域校验**。fleet_assessment/parsers/assessment_excel_list.py：自定义 BadExcelFile 异常、每列白名单枚举、类型即查即报、读到 "END" 行停。泛化：外部数据（Excel/邮件/上传）进门第一件事是逐列契约校验，把脏数据拦在业务层之外。
6. **【金】运维脚本 fail-fast 级联**。server-scripts/backup_production.sh：每个关键步骤 `|| exit 1`，开头逐个校验环境变量缺失即中止。泛化：自动化脚本失败要停在第一时间，而不是带病跑到底。
7. **【留】测试覆盖有台账**。odoo-utilities/selenium/find_untested_modules.py 用白名单显式声明"哪些模块不需要 UI 测试"——测什么、豁免什么都有清单可审。
8. **【留】文档贴着运行环境放**。4 份 handbook 直接放在 venv 目录（odoo14-venv/frontend_guildline_and_standard.md 等），addon README 统一"Usage/User Roles"模板（odooext14-cevt/README.md）。

## 四、栽了什么坑（模式级教训）

1. **单仓大爆炸**：10 代把自研/OCA/muk 混装 214 个 addon 于一个仓库，边界消失；14 代被迫拆三层重付迁移成本。模式：二开平台起步时不按"所有权/层级"分仓，两三年后必然用大迁移来还债。防范：第一天就分 platform/business/customer 三层。
2. **注册表与磁盘漂移**：compute_module_update_order.py 里有"注册表声明使用但目录不存在"的对账分支——说明漂移真实发生过。模式：任何"清单文件"一旦靠手维护，就和现实分叉。防范：注册表由 CI 从目录树自动生成，或 MR 时双向校验。
3. **配置复制扩散**：8 份公司 conf 互为拷贝手工漂移（odoo14-venv/），同一改动要改 N 处。模式：环境配置靠"复制上一份改改"必然发散。防范：模板 + 变量注入，一处定义。
4. **vendor 进仓后打补丁**：geelyodoo 里 geely_mail_fixed 直接以 fork 方式修第三方邮件模块。模式：不记录对上游的修改，下轮升级补丁即丢。防范：第三方改动 patch 文件化 + 升级时重放。
5. **邮件即集成总线的脆弱性**：incoming_email_router/models/route_email.py 在代码里硬编码供应商发件人地址白名单——供应商改地址即静默断流。模式：把外部系统的"身份约定"写死在代码里，变化时无告警。防范：路由规则配置化 + 无匹配路由时显式告警。
6. **密钥随仓库分发**：k8s secrets.yaml（db 密码、Azure 存储密钥）、8 份 conf 的 admin_passwd/db_password、docker images 下 conf/env 均提交进 git。模式：早期图省事，后期换密钥 = 全历史泄漏。防范：secret 外置（Vault/ExternalSecrets），仓库只留引用。
7. **环境双轨制**：Windows 侧 nginx.exe/bat/geckodriver.exe 与 Linux docker/k8s 并存，同一逻辑两套写法（nginx.conf 只服务 Flutter 静态 QA 包）。模式：开发机栈与生产栈不同构，问题总在差异处爆发。防范：容器即开发环境，消灭双轨。
8. **工具链版本碎片**：selenium/find_untested_modules.py 还是 python2.7 + gb18030 编码头，与新仓 py3 并存。模式：小工具不跟着大部队升级，多年后无人敢动。防范：工具与主代码同仓同 lint 同版本。

## 五、若用现代栈重做

1. **addon 分层 → monorepo 分层包**：platform/business/customer overlay 用 pnpm workspace / Maven 多模块表达，依赖门禁（三-3）直接由构建工具承担。
2. **Excel/邮件导入 → 统一摄入管道**：队列 + schema 校验（Zod/pydantic）+ 行级错误收集 + 校验报告回传用户，替代散落在各 parser 的手写白名单（三-4/5 思路保留，基建统一）。
3. **CronLogger → 作业结构化报告**：批处理作业（Temporal/BullMQ）天然输出 processed/failed 明细，失败汇总告警，替代手写日志聚合器。
4. **迁移 codify → codemod 流水线**：jscodeshift/OpenRewrite + 升级 playbook 进 CI，升级成本从"人月"降为"机器跑一遍 + 人审 diff"。
5. **多公司 conf → 配置中心 + secret manager**：一份模板 + 环境变量/ExternalSecrets 注入，多租户隔离交给中间件而非 dbfilter 约定。
6. **Power BI 直连 ORM → 只读副本/CDC 进仓**：报表取数与业务库物理隔离，别在业务模型上开"公开接口"。

## 六、证据索引（含敏感信息位置清单）

- 结构：`D:\projects\projects-old\cevt\`（odooext14-base 55 / odooext14-cevt 82 / odooext-cevt-geelyodoo 9 / odooext-cevt-addons10 214 个 addon 目录；git log 统计见三、四节）
- 手册：`odoo14-venv\frontend_guildline_and_standard.md`、`frontend_qweb_handbook.md`、`gantt_handbook.md`、`website_handbook.md`；`odooext14-test-base\README.md`
- 迁移：`odoo-utilities\migration-scripts\migrate_130_140.py`、`migrate_script_helper.py`、`migrate_cevt_specific.py`、`odooext14-cevt\baseline\commit_log.txt`
- 门禁/工具：`odoo-utilities\pipeline\dependency_check.yml`、`pipeline\pylint.yml`、`util\dependency_checker.py`、`util\compute_module_update_order.py`、`odooext-cevt-addons10\cevt_modules.json`、`lotus_modules.json`
- 防御性写法：`odooext14-base\cron_handler\cron_logger.py`、`odooext14-cevt\fleet_assessment\parsers\assessment_excel_list.py`、`odooext14-cevt\incoming_email_router\models\route_email.py`
- 运维：`odoo-utilities\server-scripts\backup_production.sh`、`deploy_mobile.sh`、`kubernetes\odoo14\`、`ansible\deploy_playbook.yaml`、`nginx-1.22.0\conf\nginx.conf`
- **敏感信息位置（需脱敏，内容未复制）**：`odoo-utilities\kubernetes\odoo10\secrets.yaml` 与 `odoo14\secrets.yaml`（db 凭据、Azure 存储密钥）；`odoo14-venv\` 下 8 份 `*.conf`（admin_passwd/db_password）；`odoo-utilities\docker\images\` 各代 `prod.conf`/`dev.conf`/`in_container.env`/`entrypoint.sh`；`odoo-utilities\server-scripts\cron_dump_container`、`migrate_db_data_to_filestore.py`；`route_email.py` 含供应商真实邮箱地址。
