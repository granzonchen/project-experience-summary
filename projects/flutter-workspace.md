# flutter 工作区（充电桩/ThingsBoard/BLE 配网等 6 项目）- 项目群经验总结

> 分析对象：`D:\projects\flutter`（约 1361MB，2022-12~2023-07 活跃，无顶层 git）
> 分析方式：只读代码勘察（2026-09-05），结合各子项目 git 历史
> 敏感红线：全文零凭据/姓名/PII 复制，敏感位置只记坐标，见第六节

## 一、项目群背景

同一公司 GitLab（ogit.wffeitas.com:11091 / git.wffeitas.com）下的移动端实验/开发工作区，业务围绕 IoT 平台 ThingsBoard 与仓库 PDA 展开：

| 项目 | 业务 | 技术栈 | 规模/git |
|---|---|---|---|
| charger(evcharge) | 充电桩预约充电 App | Flutter(>=2.17.1) + GetX + google_maps | 84 dart，92 提交，MR 工作流 |
| tb_app_fj | ThingsBoard 官方 App 二开 | Flutter（README 钉 3.3.10） | ~97 dart，5 提交 |
| feng-ji / feng-ji-old | 风机设备监控（同一远端的两个克隆） | Flutter(>=2.16.2) + GetX，UI kit 模板底子 | 103/104 dart，0 tag |
| 12.觅感模块 | BLE/WiFi 配网交付包 | **React Native 0.63** + 微信小程序 + APK + PDF | 107MB，无 .git |
| hwc_pda/warehouse_pda | 仓库 PDA（Odoo 后端） | Dart>=2.7 + pda_scanner + odoo_api | 135 跟踪文件，51 提交 |
| deer_sthx | flutter_deer 学习克隆 | Flutter>=3.7 | 191 dart，2 提交 |

对清点阶段画像的三点修正（均有实证）：① migan-app 实为 **React Native**（`觅感-app-master/migan-app-master/package.json`：react-native ~0.63.4），非 Flutter；② tb_app_fj 的 842MB build/**未入 git**（`git ls-files` 中 build/ 计数为 0，.git 仅 1MB），是磁盘残留不是仓库膨胀；③ feng-ji ↔ feng-ji-old 不是两仓库，是**同一远端的两个克隆**（remote 均为 …/flutter/feng-ji.git）。

## 二、各项目关键模式

**charger（主力）**：GetX 全家桶（34 文件 import get，GetMaterialApp + app_pages/app_routes 集中路由）；但无分层数据层——dio 与 thingsboard_client 调用直接散在 10+ 个 View 文件里，`lib/app/data/data_file.dart` 只是静态 UI 文案常量，不是仓库层【留】页面少时无碍，规模翻倍必成重复代码泥团。ThingsBoard 遥测消费是模板：charging_screen.dart:214-246 拉最新遥测（forward_energy_total/work_state/connection_state）映射 UI 字段，:54 dispose 里 unsubscribe，订阅生命周期有管【留】。git 链完整记录后端演化：3707d3b"ADD odoo服务器的地址"→ 88386aa"对接tb"→ 3ae654c"迁移至生产环境"→ 4d9448b"根据odoo变化调整"——业务库与设备库双后端真实并存，但无防腐层，odoo 一变就改 View【留】。**依赖冲突写进提交**：2d4ecab"ADD thingsboard_client，需要将dio降到4.0.6"，三方 SDK 传递约束倒逼直接依赖降级，事前无解析检查【金】。git 卫生两面性：小 MR + feature 分支是好习惯；但 .gitignore 把 ios/* 整目录忽略、pubspec.lock 列在忽略清单却实际被跟踪（死规则），首日提交即自嘲"init google map 体积很大"。

**tb_app_fj ↔ charger（同平台两条客户端路线）**：二开清单可直接从 5 个提交读出——init 官方克隆 → ec3dc9b add sp_util → 903a0b8 add url setting（新增 set_url_page.dart + 改 tb_context/app_constants）→ 5f25f2c fix tree shake icons → b9c88b1 fix login。克隆官方 App 后的标准三件事：**服务器 URL 可配、本地存储、修登录**【金】URL 配置化是二开第一刚需。风险点：flutter_inappwebview 指向 GitHub fork 且 `ref: master` 浮动引用（pubspec.yaml），上游一推即碎【金】。同平台三客户端三约束：thingsboard_client 在 charger 钉 1.0.2、tb_app_fj 钉 1.0.3、feng-ji 用 ^1.0.2，兼容矩阵靠人脑【金】。

**feng-ji ↔ feng-ji-old（副本对解剖标本）**：lib 层 diff 仅 10 处，全部集中在 device_* 觪图（device_list_view/device_edit_page/device_kanban_view 等）与 login_screen——模板部分（hotel_booking/design_course/fitness_app 骨架）原样未动，**漂移恰好只发生在唯一有业务价值的部分**【金】。feng-ji-old 停在 add_dependence 分支，头顶孤岛提交 a1a0151"添加版本说明"（2022-12-08，仅 README +4/-1），master 上没有它；工作区还有未提交改动。："版本说明"这种本该永久的文档锁死在将被遗忘的克隆里——R-14 实物：无 tag，"能跑的状态"靠整目录复制固化，孤岛提交随目录风化【金】。提交语料暴露两大反复出血点：两次"fix dependce" + "FIX 安卓真机白屏问题"；"FIXME 添加左侧箭头回退？"把待办写进提交信息，决策无处沉淀【留】。定制代码嵌在模板目录内（fitness_app/my_diary/device_*.dart）而非独立 feature 包，模板升级无法 cherry-pick【留】。

**12.觅感模块（混合交付形态）**：单目录 107MB 混五类物——RN 源码目录 + 源码 zip 双份、小程序目录 + zip 双份、32MB 成品 APK（觅感-config-app-2.0.1.apk）、3 份硬件 PDF（AT 指令 V1.4/配网指南 V1.1/规格书 V1.6）、BLE 拓扑 png。"下载即归档"使 zip 与解压目录互为影子，无单一出处【金】。双端分工：RN App（react-native-ble-manager 7.6.3 + wifi-reborn，页面 apTips→configDevice→inputWifi→resultPage）管设备侧 AP 配网，微信小程序管用户侧；README 仅"node 14/yarn/npm run usb/去 as build"四句 tribal knowledge【留】。整包无 .git，无法回答"这版 APK 对应哪个 commit"【金】。

**hwc_pda/warehouse_pda（PDA 扫码形态）**：pda_scanner ^0.2.9 只在 4 个页面启用（main.dart 注册 + fts_stock_picking_in/out、fts_stock_repair），与 jt-app 扫码三件套同构【留】。odoo_api 1.0.4 直连，api/ 层仅 3 文件，Config/user_environment.dart + fts_config_enviroment.dart 做页面级服务器切换（提交"登录页面添加切换服务器页面"）【留】。51 提交里"更新代码/修改代码"类低信息提交居多，业务语义只活在文件名（fts_repair_request/fts_inspect_item…）里——提交纪律崩塌后文件名成唯一索引【金】。

**deer_sthx**：flutter_deer 整克隆推上公司 GitLab（F001 命名空间，2 提交），design/ 连原仓设计稿 zip 一起搬，pubspec.lock 缺失。参考资产混在业务工作区即是检索噪声【留】参考仓应标注只读并物理分目录。

## 三、共性观察与教训（跨项目聚类）

1. 【金】**副本当版本管理，孤岛与漂移必然发生**。三处独立证据：feng-ji-old 的 stranded 提交 a1a0151 + 脏工作区；觅感 zip/目录双份；tb_app_fj 842MB 构建残留。同远端两克隆的 lib diff 10 处全落在业务视图。规则：能跑的状态只允许 tag/流水线一个出处，克隆必须 day-1 推回远端，副本对要有定期 diff 门禁。
2. 【金】**交付产物与源码同目录**。觅感包（APK+PDF+zip+源码）、deer_sthx/design 设计 zip、tb_app_fj build/ 三项目同犯。归档时产物、文档、源码物理分目录，且互相带版本指针（APK↔commit hash）。
3. 【金】**三方 SDK 传递约束是隐性锁，引入前无解析环节**。charger 被 dio 4.0.6 降级（提交可查）、tb_app_fj 挂浮动 fork、同平台三客户端三版 thingsboard_client。规则：新增依赖先跑依赖解析 dry-run；lock 策略统一（本工作区四种状态并存：charger 锁文件被跟踪却列在 ignore、deer 无 lock、其余跟踪）。
4. 【金】**环境基线最易失忆**。六个项目 SDK 下界五个档位（2.7/2.12/2.16/2.17/2.19）+ RN0.63/node14；全工作区唯一环境文档是 tb_app_fj README 一行"flutter：3.3.10"，charger README 还是模板默认文。规则：README 首行钉精确工具链版本是最低配。
5. 【金】**提交信息质量决定 git 历史可 mining 性**。charger 中英混合小 MR 能完整重建 odoo→TB 殖化链；hwc_pda"更新代码"把历史抹平。同批人同一年两种纪律，差异直接等于复盘价值差异。
6. 【留】**UI 模板起步 = 快起步 + 慢债务**。feng-ji（fitness UI kit）模板骨架与业务增量物理混杂，改模板即动业务；模板导入后应先移除 demo 目录、业务建独立 feature 包。

## 四、若用现代栈重做

1. **charger**：Flutter 3.x + Riverpod；强制 repository 层把 dio/TB client 收敛进 data/；地图 key 用 `--dart-define`/flavor 注入，杜绝 Manifest 与 dart 源码双处硬编码。
2. **ThingsBoard 三客户端统一**：官方 App 二开改"薄 fork + 补丁集"或主题化定制；自研端统一 thingsboard_client 基线并登记依赖来源清单；三 App 抽共享 core 包（Melos monorepo），URL/租户等环境量配置化下发。
3. **BLE 配网**：RN 0.63 已 EOL；配网流程抽成显式状态机（发现→连接→凭据下发→确认），AP/BLE 双模式可配；AT 指令 PDF 与代码实现对账（文档由协议定义生成），消灭 PDF↔代码双源。
4. **工作区治理三道 CI 门**：`git ls-files` 查构建产物入库、lock 文件一致性检查（App 必须提交 lock）、密钥扫描（AIza/wx 前缀）；feng-ji 类克隆合并回单仓。
5. **PDA 类**：pda_scanner 已停更，改厂商扫码 SDK 封装 + 事件总线；Odoo 接入用 OpenAPI 生成 client 替代手工 api 层。

## 五、证据索引（含敏感信息位置清单）

**敏感位置（只记坐标，一律未复制）**：
- Google Maps API key（AIza 开头）×2：`charger/android/app/src/main/AndroidManifest.xml:9`、`charger/lib/app/view/location/select_location.dart:91` ——**工作区已替换为 REDACT（2026-09-05）**
- 微信小程序 appid（wx 开头）：`12.觅感模块/觅感-mini-app-master/migan-mini-app-master/project.config.json:52` ——**已替换（2026-09-05）**
- 全工作区扫描基线：`D:\projects\flutter\_sanitize_report_20260905.md`（21 替换候选/4 数据产物，已 execute 并复跑归零）
- **git 历史清洗（2026-09-05）**：charger（历史 3 blob 含 Maps key）/ tb_app_fj / hwc_pda 三仓经 git filter-repo 重写——格式密钥替换 + 作者身份全部匿名化（archive@noreply.local），提交数不变（95/6/52），旧含密 blob 已清除，终验零残留；重写前三仓镜像备份于 `D:\projects\_archive\20260905-git-backups\`。feng-ji×2 / deer_sthx 未清洗（不外发）

**关键证据指针**：
- charger：`pubspec.yaml`（get/google_maps/thingsboard_client 1.0.2/dio ^4.0.6）、`lib/app/view/booking/charging_screen.dart:54,214-246`、`lib/main.dart`、`.gitignore`（ios/* 与 pubspec.lock 死规则）、git 提交 2d4ecab/3707d3b/88386aa/3ae654c/4d9448b
- tb_app_fj：git 49a6206→b9c88b1 五提交链（`git show 903a0b8 --stat`：set_url_page/tb_context/app_constants）、`pubspec.yaml`（flutter_inappwebview fork ref:master）、`README.md`（单行环境）、`git ls-files | grep -c ^build/` = 0
- feng-ji 对：`diff -rq feng-ji/lib feng-ji-old/lib`（10 处，均在 device_* 与 login_screen）、feng-ji-old `git branch`（add_dependence）、`git show a1a0151`（README +4/-1，2022-12-08）、脏工作区、`lib/fitness_app/my_diary/device_*.dart`
- 觅感：根目录清单（APK/PDF×3/png/zip×2）、`觅感-app-master/migan-app-master/package.json`（RN 0.63.4/ble-manager/wifi-reborn）、`pages/`（apTips/configDevice/inputWifi/resultPage）、整包无 .git
- hwc_pda：`warehouse_pda/pubspec.yaml`（pda_scanner ^0.2.9/odoo_api 1.0.4/dart>=2.7）、`lib/pages/fts_stock_picking_*.dart`、`lib/Config/user_environment.dart`、git log（"更新代码"类低信息提交）
- deer_sthx：git remote（ogit F001 命名空间）、无 pubspec.lock、`design/design.zip`
