# python 工作区（充电桩/获客机器人/APS 排产等 8 项目）- 项目群经验总结

> 分析对象：`D:\projects\python`（1610MB，2023-03~2023-06 活跃 + pg_to_mysql 2026-06 仍在用；无顶层 git）
> 分析方式：只读代码勘察 + 全量代码通读（2026-09-06，28 个 py 文件全部人工过目——体量小，未派深读代理，证据均为一手）
> 敏感红线：全文零凭据复制；处置时 pg_to_mysql 经用户指令**原样保留**（在用生产工具）

## 一、项目群背景

同一公司 GitLab（ogit.wffeitas.com，已死）生态下的 **Python 工具/机器人工作区**，全部是围绕公司业务生态（ThingsBoard / Odoo / MES / 抖音获客）的**胶水脚本与桌面自动化工具**，无独立产品。8 个子项目约 1610MB，其中 venv 虚拟环境占 ~1.5GB，**真实代码总量不足 1MB（28 个 py 文件约 2700 行）**。

| 项目 | 业务 | 代码量 | git |
|---|---|---|---|
| info_robot | TB 设备创建→Odoo 维护台账联动 + sqlite 抓取落库 | 6 文件 556 行 | 12 提交（ogit 死） |
| huoke_robot | 抖音获客机器人（FastAPI 任务接口 + selenium 抓取 + 第三方平台） | 6 文件 500 行 | 2 提交 |
| charger（py 版） | TB 充电桩遥测 MQTT 测试脚本（与 flutter/charger 同业务） | 1 文件 70 行 | 无 |
| aps_linear_program | pulp 线性规划排产测试（APS 雏形） | 6 文件 206 行 | 4 提交 |
| auto_xls_to_csv ↔ _32 | Excel→CSV 定时扫描转换（_32 为 32 位 pyinstaller 打包版），**复制对** | 2~3 文件 | 3 提交 / 无 |
| tooljit_pdf | pdfkit/pyppeteer 页面转 PDF 实验 | 1 文件 67 行 | 4 提交 |
| **pg_to_mysql** | **⚠️ cwjt 生产同步工具（PG cwjt-prod → MySQL zhihuigongchang + MQTT device/updated），2026-06 仍在改——非旧项目** | 4 文件 534 行 | 无 |

## 二、各项目关键模式

**info_robot**：tb_rest_client 建 TB 设备 → 取 device_id/token → requests 回写 Odoo maintenance.equipment（tb_create_device.py 全 25 行即完整链路）【留】"跨系统对象创建联动"模式本身可迁移，但无重试/无幂等（重复跑会重复建设备）。sqlite_db.py 用中文列名建表（课程动态id/学员姓名/联系电话）——抓取库即席建表【留】快速落地方案，代价是 SQL 内嵌中文 schema 难维护。

**huoke_robot**：FastAPI 包 selenium 抓取（dy_test.py 272 行为最大单文件）——任务模型（Task：抓取标题/时间窗/关键词/点数计费）设计完整【留】"抓取任务即服务"的接口化思路；config.py 集中配置含第三方平台与公网 MySQL 凭据【坑】；README 注明"仅限研究讨论使用"。

**charger（py 版）**：paho-mqtt 向 TB 推遥测的测试脚本，control dict 与 flutter/charger 的遥测字段（forward_energy_total/work_state/charger_id…）一一对应——**py 测试脚本 ↔ Flutter 客户端共用同一遥测契约**【留】硬件测试脚本与客户端共享契约的联调模式。

**aps_linear_program**：pulp 整数规划测试（aps_test_time_opt.py 目标函数最小化 540x+540y+510z+510w，约束产能≥M）——排产线性规划的算法试水【留】test7.lp 实例文件留存；未成产品。

**auto_xls_to_csv ↔ _32（复制对）**：pandas 定时扫描目录把 xls 转 csv（处理表头换行/引号清洗）【留】小而完整的"目录监视→格式转换"模式；`_32` 是 32 位 pyinstaller 打包版——为兼容客户 32 位环境而复制整工程【坑】R-13 副本再证。**exe 交付物三处重复**：根目录、dist/、env/Scripts/dist/ 各一份 23MB——打包产物散落无单一出处【坑】R-14 实物。

**pg_to_mysql（在用，未处置）**：PG→MySQL 设备同步 + MQTT 重发布 + SCADA 记录同步，TimedRotatingFileHandler 日志、last_id 断点文件【留】"断点续传 + 按天轮转日志"是同步脚本的正确骨架；但三套生产口令明文硬编码 + 无超时参数 + 固定 IP 配置【坑】R-17 现行违规（经用户决策原样保留，移交 cwjt 线处理）。

## 三、共性观察与教训（跨项目聚类）

1. 【金】**活跃工具与归档工作区混放是治理事故的温床**。pg_to_mysql（2026-06 在改、连生产库）混在 2023 死项目堆里，若按"旧项目瘦身"流程一刀切，生产同步链路会被直接清掉。规则：工作区清点第一件事是**按 mtime + 连通性甄别在用物**，在用工具必须摘出处置范围（本次由 sanitize 复验残留 3 候选反查发现）。
2. 【金】**共享代码靠复制传播，三项目三个同名文件**。dy_test.py / convert_json_file.py / init_header.py 在 huoke_robot 与 info_robot 间同名复制（与 miniapp-cluster"真正复用的是 API 封装层"结论互相印证）。规则：胶水脚本群的公共部分（抓取器/API 封装/JSON 转换）应抽共享包。
3. 【金】**venv 占工作区 93% 体积**。8 座 env 共 ~1.5GB vs 代码 <1MB，且 requirements.txt 仅 2/8 项目存在。规则：venv 永不入工作区备份/归档范围；requirements.txt/lock 是环境唯一出处（R-14/R-15 延伸）。
4. 【金】**git-less 工具的"能跑状态"是 exe**。auto_xls_to_csv 无 git，其可交付状态=pyinstaller 产物 exe（三处重复）。规则：无源码仓的桌面工具，exe+源码应一起进一个最小 git 仓（R-14 延伸）。
5. 【留】**全部工具 = 业务生态胶水层**。TB/Odoo/MES 三件套的 glue 脚本群——这类代码的复盘价值不在架构（没有架构），而在"某类集成怎么做"的配方（建设备/推遥测/格式转换/页面转 PDF），适合沉淀为配方库而非文档库。
6. 【坑】**凭据硬编码是全工作区默认状态**。7 个死项目 + 1 个在用工具共 16 处（已清死项目 13 处；pg_to_mysql 3 处经用户决策保留）。

## 四、若用现代栈重做

1. **胶水脚本模板化**：typer CLI + pydantic-settings（凭据全环境变量）+ structlog——一个模板复用到全部 8 个工具，配置注入杜绝硬编码。
2. **同步类**（pg_to_mysql）：加 requests/pymysql 超时与重试（R-18）、断点状态进 sqlite 而非 txt、口令走 keyring/env。
3. **抓取类**（huoke/info_robot）：selenium → Playwright；抓取任务接口保留 FastAPI 但任务状态进 sqlite；公共抓取层抽共享包（melos 式 monorepo 或 pip 可编辑安装）。
4. **打包类**（auto_xls_to_csv）：pyinstaller 进 CI，exe 单一出处挂 tag；32 位需求改用 embedding 精简发行。
5. **工作区治理**：在用工具与归档分目录（active/ vs archive/），mtime 连通性双条件甄别。

## 五、证据索引（含敏感信息位置清单）

**敏感位置（只记坐标与类型，零复制）**：
- `pg_to_mysql/mes_device_sync.py`（PG/MySQL 口令）、`mes_mqtt_publisher.py`（MQTT 口令）——**在用生产凭据，经用户决策原样保留，建议移交 cwjt 线做注入化+轮换**
- `huoke_robot/config.py`（第三方平台账密 + 公网 MySQL 口令）——**已替换 REDACT_20260906**
- `charger/tb_test_charger.py`（TB ACCESS_TOKEN）——**已替换**
- 全工作区扫描基线：`D:\projects\_archive\20260906-python-评估\sanitize_report_20260906.md`

**关键证据指针**：
- info_robot：`tb_create_device.py`（TB→Odoo 全链路 25 行）、`sqlite_db.py`（中文列名建表）
- huoke_robot：`main.py`（Task 模型）、`config.py`（30 行内含两类凭据）、`dy_test.py`（272 行抓取主体）
- charger：`tb_test_charger.py`（control dict 遥测契约）
- aps_linear_program：`aps_test_time_opt.py`（pulp 目标函数/约束）、`test7.lp`
- auto_xls_to_csv：`xls_to_csv.py` vs `_32/xls_to_csv.py`（74 行 vs 50 行差异）、exe 三处：根/dist/envScripts（本勘察记录）
- pg_to_mysql：`mes_device_sync.py`（PG_CONFIG/MYSQL_CONFIG 明文块）、`mes_mqtt_publisher.py`（MQTT 配置块）、`last_device_id.txt`（断点文件）
- 同名复制传播：`huoke_robot/{dy_test,convert_json_file,init_header}.py` ↔ `info_robot/{dy_test,convert_json_file,init_header}.py`

## 六、处置记录（2026-09-06）

- B2：7 个死项目凭据 execute 替换（复跑归零，pg_to_mysql 3 处生产凭据经用户决策保留）
- E1：6+1 座 venv（含 tooljit_pdf/env 漏网补收）+ 2 个 build + 2 个 __pycache__ 经 recycle.py 入回收站，**释放 ~1.43GB**（1610→178MB）；exe 三份与 pg_to_mysql 全程未动
- 复验：site-packages/env 归零；回收入站清单见回收站（用户检查后手动清空）
