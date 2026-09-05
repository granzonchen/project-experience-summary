# ltc（物流服务 Odoo + 多端前端）- 项目经验总结

> 分析对象：`D:\projects\projects-old\ltc`（+ltc-test-base、ltc备份，约 1.3G，目录最后修改 2024-07）
> 分析方式：只读代码勘察 + git 历史勘察（2026-09）

## 一、项目背景与业务问题

2020-04 ~ 2022-01 活跃（hn_service 本地 git 提交区间），面向能源/风电行业客户的备件交易与维修交付平台：三个 Odoo 业务子系统——慧能备件电子交易系统（pes）、慧能交付管理模块（pms）、维修管理（mms：工单/维修记录/出厂检验/风电场）。向上游对接 SAP 库存（接口字段全用 SAP 词表 matnr/maktx/lgort/charg/sernr/clabs，见 mms/restful/mms_api.md），向下游对接中广核物流推送与订单同步（git 提交 08a07097）。用户三类：内部运营（Odoo 后端）、维修工程师（微信小程序）、外部门户（pes/portal_website）。

## 二、架构与技术决策

- **Odoo 13 多 addon 根单体**：hn_ltc.conf 第 2 行 addons_path 挂 5 个根——hn_service（58 个子目录、约 55 个 addon、7202 提交）、mms（6 个 addon）、pms、pes，连 selenium-test-base 也挂进 addons_path。hn_service 内约半数为直拷社区模块（auditlog、queue_job 三件套、ks_dashboard_ninja、web_dialog_size 等），其余为业务模块（contract*、spare_quotation、market_information、crm_*、update_customer）。
- **移动端 uni-app(Vue2)+ThorUI**：mms-wmp 维修小程序（273 提交）+ mms-wmp-en 英文版 + mms-wmp-back 快照，共三套并存；另有 pms_applet 交付进度小程序、portal_website 门户，前端工程实际 5 个目录。
- **API 层**：mms/restful addon 做 token 鉴权的薄 REST 层（controllers/token.py + models/access_token.py），mms_api.md 接口文档随代码走；小程序端直连生产域名。
- **外部集成**：auto_backup（paramiko/SFTP 异地备份）、market_information 内嵌 Elasticsearch 客户端、base_external_dbsource、klw_office（OnlyOffice 在线文档）、oejia_wx（微信）。
- **部署**：hn_service/docker-compose.yml 双容器（自建私仓 <REGISTRY_HOST>:<PORT> 的 goldwind/ltc12:v1 + postgres:10）；开发机是 Windows 本机 Odoo 直跑（hn_ltc.conf），compose 里却写死 macOS 用户路径——多套环境并存且各自为政。
- **测试**：ltc-test-base = Selenium(Firefox) UI 测试（base.py，Singleton 化的 User/驱动管理 + screenshots 截图留证）+ odoorpc 直连测试 + LoadTests/OdooLocust 按 task 权重压 RPC。

## 三、做对了什么（可迁移思路）

1. **【留】ERP 作集成中枢、统一模型承载**：SAP 库存 → Odoo 模型 → 小程序/门户/中广核，多消费端共享一套业务模型而非点对点直连（证据：mms/restful/mms_api.md 字段表、hn_service/update_customer）。泛化：多端场景先把数据收拢到唯一权威源，再向外辐射。
2. **【留】接口文档随代码走 + 网关式薄 REST 层**：鉴权独立成 token controller，API 文档 markdown 就放在 addon 内（mms/restful/mms_api.md）。泛化：文档与实现同仓同目录，腐烂速度才追得上代码。
3. **【金】外部依赖显式超时 + 重试**：ES 客户端 timeout=30、retry_on_timeout（market_information/models/tools.py 56-59 行），SFTP 连接 timeout=10（auto_backup/models/db_backup.py:97）。git 提交 e3d5459b「ES增加超时参数」说明这是踩坑后补的——先挂过才加的。
4. **【金】N+1 查询改批量接口**：提交 6cdf0118「现有库存改为批量接口」，库存查询从逐条改批量的修复真实入库。
5. **【金】数据库自动备份 + 异地 offsite**：auto_backup 定期 dump 并经 SFTP 推外部服务器（提交 43017ebe「增加备份模块」），备份链路独立于应用宿主机。
6. **【留】三层测试意图齐备**：单元（Odoo test tags）+ Selenium UI（截图落盘 screenshots/ 供人工核验）+ Locust 按 task 权重加权压 RPC（LoadTests/loadtest.py）。层次划分思路可整体平移到现代栈。

## 四、栽了什么坑（模式级教训）

1. **【金】按语言整仓复制做国际化**：mms-wmp-en 与 mms-wmp 全树仅 49 个文件不同，全部是逐字符串手工替换（对比 src/pages/Login/Login.vue：「维修平台→Repair platform」式 diff），无任何 i18n 框架。触发条件：业务临时要英文版、工期紧。后果：每个业务修复必须双写，两版必然漂移。防范：文案键值化进资源文件，语言是构建产物不是仓库副本。
2. **【金】目录快照代替版本管理**：hn_service 有 7202 提交却 **0 个 tag**，于是"能跑的状态"只能靠文件系统固化——mms-wmp-back（与本体仅 2 文件差 + unpackage 构建产物）、pms_wewqe（pms 的整仓二次克隆，工作树已漂移 60+ 文件）、ltc备份、归档时打的 mms-wmp.zip（69MB，2024-06）。副本即分叉，备份越多真相越少。防范：tag/发布流水线是"可运行状态"的唯一出处。
3. **【金】测试资产跨项目复制**：ltc-test-base 的 rpc_test_for_hil.py 与 LoadTests 引用的是另一项目（cevt）的模型（fleet.vehicle/mro.order）和三套环境地址+凭据——测试基线对本项目零守护作用，还把他人的生产密钥搬了家。防范：测试基线随项目走，复制前先删干净历史与环境。
4. **【金】注释当开关**：git log 连续出现「注掉物流信息」→「解开物流的注释」→「注释物流进度」，外部同步/推送逻辑靠注释行启停，无 feature flag。多人多分支下这种"开关"必然互相冲掉。
5. **【金】环境配置与运行时产物入库**：hn_ltc.conf 含明文 db 口令与口令提示串、ltc-workspace.code-workspace 含明文 pg 连接、compose 内嵌私仓 IP 与个人 macOS 路径；sessions/*.sess、.pyc、node_modules（212M）、dist、geckodriver.log 全在工作树——1.3G 体量大半与源码无关。同名模式：小程序 API 层把数据库名写死并留注释切换（httpRequest.js），环境切换靠改代码。
6. **【留】分支治理失控**：209 个分支、命名混乱——工单号（47098/99860）、人名缩写+日期（CXL20220526、fix_202111_ylx）、中文（添加了portal地图）并存。合并全是 Merge person X into develop 的人肉操作，无命名规范、无生命周期。
7. **【留】vendored 依赖无清单**：社区 addon 直拷进业务仓，自研/三方边界不可见、升不了级；queue_job 引入后业务模块零引用（仅自身 tests）——引而未用的死重徒增理解成本。

## 五、若用现代栈重做

1. **单代码库 i18n**：前端保 uni-app 或迁 Taro/Vue3，文案全走 vue-i18n 资源文件；英文版是构建目标（locale bundle），不是第二个仓库。
2. **monorepo + 依赖门禁**：pnpm workspace 收编全部前端，ThorUI 等价组件库发私有 npm 包；后端 addon 拆 self/custom 两个来源并在清单里锁基线版本，安装前机器校验依赖（对应坑 7）。
3. **外部系统对接抽 adapter 服务**：SAP/中广核同步做成独立 adapter + 消息队列（Outbox + 重试 + 死信，把引入未用的 queue_job 思路真落地），超时/重试/熔断统一封装，业务侧 safeList 兜底（对应坑 4 与亮点 3/4）。
4. **配置与秘密出库**：.env 模板 + secrets 管理；compose 用 profiles 区分环境；备份交给 pgBackRest/WAL-G，不再手写 paramiko 脚本（对应坑 5、亮点 5 的现代化）。
5. **CI/CD 兜住版本**：自建 GitLab（当时已有 git.kalway.cn）加分保护、tag 发布、产物归档；Selenium→Playwright 保留截图留证，Locust 压测进夜间流水线——三层测试意图原样平移（对应坑 2/3、坑 6）。

## 六、证据索引（含敏感信息位置清单）

- 结构总览：ltc\hn_ltc.conf（addons_path 五根）、ltc\ltc-workspace.code-workspace（工程组织）、ltc\hn_service\（58 子目录/7202 提交/209 分支/0 tag）、ltc\mms\、ltc\pms\、ltc\pes\portal_website\
- 前端三副本：ltc\mms-wmp\src\ vs mms-wmp-en\src\（49 文件 diff）、vs mms-wmp-back\src\（2 文件 diff）；API 层 ltc\mms-wmp\src\odoo_api\httpRequest.js
- 接口与集成：ltc\mms\restful\mms_api.md、restful\controllers\token.py；ltc\hn_service\market_information\models\tools.py（ES）、auto_backup\models\db_backup.py（paramiko）、klw_office\（OnlyOffice）
- 修复记录（hn_service git）：e3d5459b（ES 超时）、6cdf0118（批量接口）、08a07097（中广核物流推送乙方编号为空）、「注掉物流信息」注释往返系列
- 测试：D:\projects\projects-old\ltc-test-base\base.py、rpc_test_for_hil.py、LoadTests\OdooLocust\；副本 ltc\selenium-test-base\（被挂进 addons_path）
- 部署：ltc\hn_service\docker-compose.yml（私仓地址 + macOS 路径）
- **敏感信息位置（仅记位置，复盘不复制内容）**：ltc\hn_2021-07-01_09-56-41.zip（53MB PostgreSQL 库导出，含生产数据）；ltc备份\hn_service（51MB PG custom dump，无扩展名易误当目录）、ltc备份\odoo14（tar 包）；ltc\hn_ltc.conf 第 3-4 行（admin_passwd 哈希与口令提示串）、第 10 行（db 口令）；ltc-test-base\base.py 第 21-23 行（注释中的真实口令，其下已被示例值替换）；ltc-test-base\rpc_test_for_hil.py（他项目生产/QA/开发三套地址+口令）；ltc\ltc-workspace.code-workspace（pg 明文连接）；ltc\sessions\*.sess（运行时会话残留）；auto_backup 的 sftp_password 为明文 Char 字段设计（口令落库）
