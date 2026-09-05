# dawei + dw（Django 复制改造样本）- 项目经验总结

> 分析对象：`D:\projects\projects-old\dawei`（业务全量版，apps 下 514 个 py）、`D:\projects\projects-old\dw`（精简副本，apps 下 190 个 py）
> 分析方式：只读代码勘察 + 两树 diff 对照（2026-09；dw 有 git：2022-01-18/19 共 4 次提交）

## 一、项目背景与业务问题

大卫国际建筑设计公司的内部综合管理系统（证据：`dawei\README.md`、`ts_web_sys\.env.development` 的系统名）。基于 dvadmin（django-vue-admin）模板二开：Django 2.2 + DRF + `apps/vadmin` 框架层 + Celery/Redis + Vue2 前端 + MySQL，依赖里还拖着 mongoengine。业务覆盖合同、招投标、财务、招聘、薪酬、EHR、会议、审批流等约 19 条业务线（`application/settings.py` 的 INSTALLED_APPS 即清单）。

dw 是 2022-01 一次 commit（"提交gitignore→提交项目→数据库文件"）落成的精简版：只保留 vadmin 框架 + base/utils + ehr，删掉其余 19 个业务 app——本质是"从项目里裁出框架+EHR 样板"。

## 二、架构与技术决策

- **分层**：`apps/vadmin`（权限/系统/监控/op_drf 基座）为框架层，业务以独立 app 平铺于 `apps/`，统一继承 `vadmin.op_drf.models.CoreModel`（证据：`apps/contract/models/contract_collection.py` 头部 import）。
- **Celery 接入**：broker=Redis（`settings.py` L397-401），beat 用 `django_celery_beat.DatabaseScheduler`（调度存 DB），独立 celery 容器 `docker_celery.sh`（`worker -B` 单容器带 beat）。
- **RBAC 初始化**：`apps/vadmin/scripts/permission|system/*.sql` + `manage.py init`（`apps/vadmin/permission/management/commands/init.py`）：truncate 前计数确认、`SET foreign_key_checks` 开关、按表回放 SQL。菜单初始化 SQL 见 dw 侧 `apps/vadmin/scripts/permission/permission_menu.sql`。
- **部署**：docker-compose 四容器（mysql/redis/django/celery，`dawei\docker-compose.yml`），入口实际是 daphne+ASGI（`docker_start.sh`）；另有 uwsgi.ini 一套未用配置。
- **数据库交付**：44MB 全量 mysqldump 进仓库（`ts_project_sys/sql/ts_project_sys.sql`），且 `.gitignore` 忽略全部 migrations——表结构靠 dump 不靠迁移（`ts_project_sys/.gitignore`）。

## 三、做对了什么（可迁移思路）

- **【金】删减自洽做到了"机械可验证"**：dw 删 19 个 app 后，settings.py、urls.py 同步清理，全库 grep 被删 app 名残留引用为 **0**（本勘察实测）。泛化：复制裁剪不是删目录，是"删目录 + 清注册点 + grep 复验"三步，第三步是验收标准。
- **【金】框架二开纪律：业务进扩展层，框架零污染**：`apps/vadmin` 全目录 grep 不到任何业务词；dawei↔dw 的 vadmin 框架文件 diff 全是 black/isort 格式化差异（如 `op_drf/viewsets.py`），逻辑未动。二开 = 新增 app + 继承 CoreModel，不动框架——这是"改框架还是建扩展层"的正面样本。
- **【金】复制落地时统一格式化**：dw 对整树跑了格式化工具再提交，使后续 diff 只剩真逻辑差异。泛化：复制品首次提交前先格式化 + 重命名，把"与上游的噪音 diff"一次性清零。
- **【留】RBAC 菜单表三合一**：`permission_menu` 一张表同时承载前端路由（web_path）、页面组件（component_path）、后端接口（interface_path + interface_method + perms），配 role 多对多 + dept/post 组织维度（dw `scripts/permission/permission_menu.sql` 建表段）。泛化：权限点"页面/接口/菜单"单源登记，前后端权限同出一表。
- **【留】幂等初始化器**：init 命令 truncate 前统计并交互确认、关外键检查回放、按 AUTH_USER_MODEL 做表名替换（`scripts/__init__.py` getSql）。幂等 + 确认的思想可迁移；但"每行一条 SQL"的文本协议是反面注脚。
- **【留】环境配置模板化**：`conf/env.example.py` → env.py，容器间用环境变量注入主机名（docker-compose environment 段）。

## 四、栽了什么坑（模式级教训）

- **路径寄生的复制脚本（最典型）**：`docker_start.sh` `cd /dvadmin-backend`（上游 dvadmin 的目录名），而 compose 挂载点是 `/ts_project_sys`；注释里还有更上游项目 `azcrm` 的 uwsgi 路径；`uwsgi.ini` 又是第三套 `/www/ts_project`。`run-docker.sh` 调用的 `manage.py initialization` 命令**不存在**（实际叫 init，实际命令清单见 `apps/*/management/commands/`），且其 stop/restart 分支是空操作、echo 还写着 "start"（复制分支没改全）。模式：脚本随上游一路复制，每换一个宿主改一半路径；防范 = 复制后做"脚本-真实路径-真实命令"对账清单。
- **初始化器路径与交付物错位，用手工文档补偿**：init 写死读 `scripts/system_t/`，仓库交付的是 `scripts/system/`，解法是 README 教人"复制目录改名 system_t"；且 dawei 缺 `system_dictdetails.sql`，按 README 走 init 也必缺文件——dw 补了该文件（推断：复制者跑 init 缺文件后回头补的），但 `system_t` 路径两版都没修。模式：初始化故障用"文档手工步骤"打补丁，每个新环境重付一遍手工税。
- **版本控制三重失守**：①dawei 归档丢 .git，git 历史只残存在根目录一个 72KB 误重定向文件里（文件名 `et --soft 2a3e152c...`，内容是彩色 git log）；②`.gitignore` 连 `.git` 自身和全部 migrations 都忽略，表结构改由 44MB dump 进库；③dw 的 git 是复制完成后 4 条一次性提交，改造过程零记录；另有 `ehr/models_before.py`、`views_before.py` 这类"_before"整文件备份 = 手工拷贝当 VCS。模式：复制/归档动作天然游离于 VCS 之外，改造期恰恰是最需要提交粒度的时期。
- **拼写错误被两端固化成契约**：前端 API 目录 `custmoer`、`projproject`、视图目录 `from`（JS 关键字做目录名，`ts_web_sys/src/views`）；后端路由前缀同步使用后，改任何一方即断链。模式：错别字一旦"前后端对齐"就升级为接口契约，成本随两端绑定递增。
- **模板基础设施照单全收、业务零使用**：Celery 全家桶接入（beat+DB 调度+独立容器+celery_log 模型）但业务 app 中 `shared_task` 使用数为 0（`contract/tasks.py` 是空文件）；daphne+channels 作为入口但全库无 websocket consumer；mongoengine 在依赖和 op_drf filters 里但主库是 MySQL。模式：复制模板自带设施时没有"用不上就删"的对账，死设施被后续维护者当活代码读。
- **注释漂移 + 半截修复**：JWT 过期 `6000*60*4`≈16.7 天、注释写 24h（`settings.py`）；dw 复制时改值成 `60*60*4`（4h）却仍留 24h 注释。模式：数值与注释双源，修一个不改另一个，漂移跨项目遗传。
- **追加式路由膨胀**：salary 一个 app 挂 4 个 urls 前缀（urls_salary/urls_summary/urls_salary_delete/urls_voucher，`application/urls.py`），`vehicle/` 前缀注册两次。模式：新功能 = 新前缀 + 新 urls 文件，永不收敛。
- **删减"能跑 ≠ 干净"**：dw 后端自洽，但前端 `src/views` 残留 contract/customer/project/workflow/evaluation 目录、`router/index.js` 仍引用 workflow、package.json 仍叫 "dvadmin" v1.1.1——死代码留给下一个读者判断生死。

## 五、若用现代栈重做

- Django 4/5+DRF（或 FastAPI）+Vue3：保留"框架层/业务 app 分离 + 统一 CoreModel（creator/modifier/create_datetime/update_datetime 审计字段基类）"的骨架——该设计跨栈成立【留】；业务按领域拆服务而非 19 个平铺 app。
- 权限：菜单表三合一拆开——前端路由权限进路由 meta，接口权限用声明式 scope/权限类，菜单只管导航；初始化数据用 fixtures/数据迁移代替手写 SQL，初始化器读路径写单测（杜绝 system_t 错位）。
- 任务队列：第一个真实异步需求出现才引入 broker；beat 调度仍可存 DB 但要有"任务清单对账"——Celery 容器在跑却没有一个任务，就是反面基线。
- 复制改造 SOP（本文档最大可迁移结论【金】）：①新仓库先建、原始拷贝即首次提交；②格式化+重命名清噪；③删减三步 = 删目录+清注册点（INSTALLED_APPS/urls/菜单 SQL/前端路由）+grep 复验零残留；④脚本路径对账清单；⑤敏感信息（conf/env.py、.env.production）一律出库。
- 数据库：迁移进 VCS，dump 只做种子不做结构源；44MB SQL 进 git 的做法直接否决。

## 六、证据索引（含敏感信息位置清单）

- 同源对照：`diff -qr dawei/ts_project_sys dw/ts_project_sys`（本勘察记录）；dw 删 19 app 见 `dw\ts_project_sys\application\settings.py` INSTALLED_APPS、`application\urls.py`。
- 坑证据：`dawei\ts_project_sys\docker_start.sh`（/dvadmin-backend、azcrm、env.py 覆盖、daphne）；`dawei\run-docker.sh`（stop/restart 空操作、initialization 命令不存在）；`ts_project_sys\uwsgi.ini`（/www/ts_project）；`apps\vadmin\permission\management\commands\init.py` L86-96（system_t）；`apps\vadmin\scripts\__init__.py`（每行一条 SQL 协议）；`application\settings.py`（JWT L334、BROKER L397）；`apps\ehr\models_before.py`。
- 亮点证据：`dw\ts_project_sys\.git`（4 提交）；`apps\contract\models\contract_collection.py`（CoreModel 继承）；dw 新增 `apps\vadmin\scripts\permission\permission_menu.sql`、`system\system_dictdetails.sql`；RBAC 表结构见该 SQL 建表注释段。
- **敏感信息位置（只记位置，不复制内容）**：①`dawei\ts_project_sys\conf\env.py` 与 `env.example.py`（DB/Redis 密钥类配置）；②`dawei\docker-compose.yml`（MYSQL_ROOT_PASSWORD 明文、注释含内网域名映射）；③`dawei\ts_web_sys\.env.production`（真实公网域名）、`dw\ts_web_sys\.env.production`（内网 IP:端口）；④dawei 根目录怪文件 `et --soft 2a3e152c...`（72KB git log 残片，含作者真实姓名+QQ 邮箱）；⑤源码头注释/docstring 遍布作者真名（如 `apps\contract\models\contract_collection.py`、`apps\ehr\models_before.py`）；⑥`dw\大卫国际系统需求.docx`（业务需求文档，外发前需脱敏审阅）。
