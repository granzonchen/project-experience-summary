# 其余项目概况清单（39 个项目）

> 本清单为快速摸底结果（基于目录结构与包配置文件，未逐行深挖）。深度的技术栈/架构/踩坑分析见对应深度文档。

## 一、低代码 / MOM 制造运营系（JeecgBoot 体系）

| 项目 | 概况 | 技术栈 |
|---|---|---|
| JeecgBoot | JeecgBoot 开源低代码开发平台源码（jeecg-boot），常作为 MOM 类项目框架底座 | Java / Spring Boot / JeecgBoot |
| hcmom | MOM 项目（hc = 华辰?），目录含 graphify-out（知识图谱分析产物）、docx_out（文档导出），为 lx-mes/cwjt 同族 MOM 平台 | Vue / JeecgBoot 系 |
| hexconn | hksk-mom-all + hksk-mom-jeecg + hksk-mom-mdm 多模块，Hexconn（鸿晟康?）MOM 平台 | Vue / JeecgBoot 系 |
| hexconn-project-delivery | hexconn 的交付版（hksk-mom-all + hksk-mom-jeecg），含交付环境配置 | Vue / JeecgBoot 系 |
| device-job-management-pc-end | hksk-mom-all + hksk-mom-jeecg，设备任务管理 PC 端 | Vue / JeecgBoot 系 |
| card-mode | donger-mom-all（与 lx-mes 的 donger-mom-* 同源），卡片模式改造版 | Vue / JeecgBoot 系 |
| changwei | 昌威交通 MOM（cwjt 的前身/同源项目），含 .codebuddy/.agnes 配置 | Vue / Java |
| baorun | baorun_end（后端）+ baorun_front（mom-cloud-ui，Vue3+Vite+ECharts），宝润 MOM 云平台 | Vue3 / Java |

## 二、移动端 H5 / 小程序（wms-phone-app 系，Vue）

| 项目 | 概况 |
|---|---|
| jt-app | 精特/交通? WMS 移动端 H5 应用（wms-phone-app） |
| lx-wms-app | 力翔 WMS 移动端 H5（wms-phone-app） |
| lx-wms-app-dev | lx-wms-app 的开发分支版本 |
| vue_app | mom-app / jt-app / npl_survey_app 多个移动端 H5 应用聚合 |
| vue_front_project | AI_CITY / app1 / app_demo（app_demo_basic）等移动端示例项目 |
| app | cwjt_apk（昌威 APK 打包产物?）+ mom-cloud-app（uni-app 移动端） |
| uniapp | uni-app 项目（odoo 相关，含钉钉小程序/支付宝小程序配置） |

## 三、数据可视化 / 管理后台

| 项目 | 概况 | 技术栈 |
|---|---|---|
| qdkj-operate-master-master | shihua（石化行业运营管理后台） | Vue + Ant Design Vue + ECharts |
| medical-ui | 医疗行业管理后台（vben-admin 架构） | Vue3 + Vite + Ant Design Vue + ECharts |
| jiateng-pc | 佳腾? PC 端管理后台（含 arthas-output 诊断产物） | Vue / Java |

## 四、电商

| 项目 | 概况 |
|---|---|
| hengyi-mall | DongerShop 商城（donger-plus 后端 + donger-plus-app 移动端） |

## 五、原生 / 跨端移动开发

| 项目 | 概况 |
|---|---|
| flutter | 多个 Flutter 应用（charger 充电桩、deer_sthx 等） |
| hw_test | HarmonyOS 鸿蒙应用（entry + hvigor 工程） |

## 六、学习 / 实验 / 工具类

| 项目 | 概况 |
|---|---|
| java | springboot-bucket-master（Spring Boot 学习示例合集） |
| js | gantt（甘特图）、rabbitmq-web-mqtt-examples（RabbitMQ/Web/MQTT 示例）、examples |
| python | aps_linear_program（线性规划）、auto_xls_to_csv（Excel 转 CSV 工具）、charger、huoke_robot |
| R | maize_analysis（玉米数据分析）、BIO2010 lab（生物信息学练习） |
| react | crm / nextjs-blog（Next.js 博客）/ react_to_pdf（PDF 生成）/ rn（React Native） |
| go | java_test / python_test 等跨语言实验目录 |
| cwjt_repository | antlr / avalon-framework 等第三方依赖库源码（Maven 仓库下载物） |
| ecloud | data / locales 数据与语言资源目录 |
| smart | env 环境配置目录 |
| projects-old | 旧项目归档目录（未分析） |

## 经验归类速查

- **大屏可视化类**（图表/轮询/缩放）：go-view、lx-mes-screen、qdkj-operate、medical-ui
- **MOM/MES 制造运营类**（JeecgBoot 体系）：lx-mes、cwjt、hcmom、hexconn、card-mode、changwei、baorun、device-job-management-pc-end
- **WMS 仓储移动端**（wms-phone-app 系）：jt-app、lx-wms-app、lx-wms-app-dev、vue_app
- **AI/Agent 类**：patent-disclosure-skill
- **商城类**：hengyi-mall
