# django-vue-admin-pro（Django+Vue 全栈脚手架）- 项目经验总结

> 分析对象：`D:\projects\projects-old\django-vue-admin-pro`（798M；git 历史 387 提交，2021-05~2022-01，remote 指向上游开源仓库 dvadmin-pro；部分文件 2025-09 有过脱敏整改痕迹）
> 分析方式：只读代码勘察 + git log 勘察（2026-09）

## 一、项目背景与业务问题

本目录是开源 RBAC 快速开发平台 dvadmin-pro 的工作副本（git remote 为 gitee 上游），定位是"clone 后十分钟得到一个带权限体系的后台管理系统"脚手架。业务闭环：用户/角色/部门/岗位 + 菜单/按钮/接口权限 + 数据范围 + 字典/附件/操作日志，前端开箱即用，Docker Compose 一键起。它在这批旧项目中的价值在于：唯一一个"完整前后端 + 容器化 + 完整 RBAC"的生产级参考实现，权限模型值得拆解沉淀。

## 二、架构与技术决策

- **后端两层自研分层**：`backend/dvadmin/system/`（RBAC 业务 app：14 个 resource 一资源一视图文件）+ `backend/dvadmin/utils/`（框架层：CustomModelViewSet、CustomPermission、统一响应、数据权限过滤器、日志中间件）。业务代码只写 model/serializer，横切能力全部收在基类。
- **认证链路**：SimpleJWT（access/refresh 各 1 天、ROTATE_REFRESH_TOKENS、登录响应附 userId/name 自定义 claim），登录时数学图形验证码（一次性、5 分钟过期），`AUTHENTICATION_BACKENDS` 换成自定义 CustomBackend（settings.py + backends.py + login.py）。
- **配置分环境方式**：单一 settings.py 不拆 dev/prod，环境差异靠 `conf/env.py` 覆盖 + `DEBUG = locals().get('DEBUG', True)` 兜底；容器内走 env_file。插件机制：`plugins/config.json`（git 地址+开关+优先级）→ urls.py 尾部 **exec 动态注册路由** → settings 尾部 `from plugins import *` 注入配置。
- **前端**：Vue2 + element-ui 的 d2-admin（实际 package 名是 d2-crud-plus starter）二开；菜单/路由完全由后端 `/api/system/menu/web_router/` 下发，`component` 字符串在运行期映射到本地文件动态 import，扁平表用 xe-utils 转树（web/src/menu/index.js）。
- **部署**：三容器 compose（nginx web / mysql:5.7 / daphne ASGI），固定子网 <DOCKER_SUBNET>/16 内静态 IP 互指，node/python 基础镜像预构建推阿里云 registry（docker_env/README.md）。

## 三、做对了什么（可迁移思路）

1. **【金】权限三正交面分表建模**：路由可见（Menu 树，含 component/图标/排序）、接口可调（MenuButton：api 路径+HTTP method，角色 M2M 绑定）、数据行可见（Role.data_range 0~4 枚举 + 自定部门 M2M），三张表各管一件事、超管短路。泛化：任何系统的"页面可见、按钮可点、数据可见"是三种独立权限，混在一张表里迟早返工。（backend/dvadmin/system/models.py）
2. **【金】鉴权只信任服务端**：CustomPermission 每请求把用户角色权限编译成 `api:method` 集合精确匹配（UUID 路径段正则归一化 + DB 白名单短路），前端菜单仅是展示过滤。泛化：前端权限控制只是 UX，不是安全边界。（backend/dvadmin/utils/permission.py）
3. **【金】数据权限做成可插拔 Filter**：DataLevelPermissionsFilter 挂在基类视图 `extra_filter_backends`，业务模型声明 `dept_belong_id` 字段即自动获得行级过滤，多角色取最大范围；未声明字段的模型自动豁免。泛化：行级权限应做成"声明即生效"的查询层横切，而非散在业务代码。（filters.py + viewset.py）
4. **【留】统一视图基类收敛协议**：统一响应包 `{code,msg,data}`（2000=成功）、create/update/list 分序列化器（含 `{action}_serializer_class` 动态解析约定）、`multiple_delete` 批删 action、过滤字段前缀语法（`^` `=` `~`）。新资源 = 写 model + serializer + 三行注册，成本极低。（dvadmin/utils/viewset.py、json_response.py）
5. **【留】幂等种子数据**：固定 UUID + `get_or_create(id=...)` + INITIALIZE_LIST 钩子，插件自带 initialize.py 继承同一基类，`manage.py init` 可重复执行不炸。（dvadmin/utils/core_initialize.py、system/initialize.py）
6. **【留】操作日志双阶段中间件**：process_view 先建记录拿 id，响应回填结果，敏感字段打码，按 method 白名单开关。（dvadmin/utils/middleware.py）
7. **【金】依赖与镜像锁版本**：requirements.txt 48 项全部 `==` 精确锁定；node/python 基础镜像预构建推私有 registry，业务镜像只 COPY 代码，构建快且可复现。

## 四、栽了什么坑（模式级教训）

1. **防御性代码没兜住自己人：字段名漂移让权限静默收窄**。`get_dept` 递归取下级部门时查的是 `values('parent')`、比较的是 `ele.get('parentId')`，永不相等 → data_range=1"本部门及以下"悄悄退化为仅本部门（filters.py:32-38，代码级推断；git 有多条"修复权限过滤bug"提交，如 eed7263）。教训：权限过滤的回归测试要断言"可见行数"，只测"不报错"测不出收窄。
2. **配置修在错误的缩进层 = 等于没修**。docker-compose.yml 中 django 服务的 `environment:` 块缩进掉到顶层（56 行），PYTHONUNBUFFERED/DATABASE_HOST 实际从未进容器——而 git 有两次"解决docker无日志打印"提交（8b39408/27629e4）说明修过；另外 env_file 指向的 `backend/.env` 在现场根本不存在，compose 直接起不来（缩进成因是否为后期整改误伤：推断）。教训：部署文件改动必须用 `compose config` 渲染校验 + 真实起容器验证，改过 ≠ 生效。
3. **exec 拼代码是框架级风格债**。路由注册（urls.py 尾部 exec 模板）、种子数据 M2M 绑定（core_initialize.py:42-47）都靠 f-string 生成 Python 源码再 exec——报错栈错乱、注入面扩大、IDE 全盲。动态性应优先用注册表/entry-points 等声明式机制。
4. **安全为兼容让步，代价被埋进哈希函数**。Users.set_password 先 MD5 再交 Django hasher（models.py:32-33），MD5 预哈希大幅降低离线爆破成本；配合 CORS 全放开+带凭证、swagger AllowAny。教训：兼容性妥协必须留注释与到期计划，否则会被当"正常实现"一直复制。
5. **审计日志反成泄露面**。操作日志存全量 request_body/response，打码只覆盖顶层 `password` 键（middleware.py:36-37），嵌套字段、token 类字段全裸奔；permission 热路径还残留调试 print。教训：日志脱敏要维护"敏感字段清单"而不是逐点 if。
6. **README 承诺与代码漂移**：定时任务、应用商店已划线弃用但 README 未删；celery.py 存在而 celery 根本不在 requirements.txt；compose 用 MySQL5.7、README 要求 8.0；docker_env/README.md 容器名与 compose 不一致。教训：归档/接手项目先按 README 跑一遍，跑不通处就是债务清单。
7. **跨端布尔/整型契约漂移**：后端 BooleanField、前端判 `cache === 1`，git 有专门提交"将部分int字段改为bool字段"（3df9286）。教训：API 布尔语义一次定死（true/false 还是 1/0），写进接口约定。

## 五、若用现代栈重做

1. **RBAC 照搬三正交表**（菜单/接口/数据范围），Django 5+DRF 或 NestJS+CASL 落地；数据范围实现为 query-scope 中间件，"模型声明字段即生效"的模式原样保留。
2. **动态路由改为构建期路由表**：前端全量打包路由 + `meta.permission` 标识，DB 只存权限位不做 `component` 字符串到文件路径的运行期映射，消灭"菜单路径写错=页面静默失踪"这一整类坑（checkRouter 只能 console 报错，web/src/menu/index.js:86-99）。
3. **配置分层现代化**：pydantic-settings/env 校验启动即失败、settings 按环境拆文件、`docker compose config` 纳入 CI；secrets 走 secret 管理而非镜像层/仓库文件。
4. **插件机制换声明式**：包管理 entry-points / 模块约定导出 + 显式注册，杜绝 exec；插件启用失败要 fail-fast 而非 print 后 pass。
5. **操作日志外移**：结构化 JSON 日志 + 统一脱敏清单，走日志管道而非业务库大 TextField（该表现场就是全量 body 存库）。

## 六、证据索引（含敏感信息位置清单）

**敏感信息位置清单（只记位置与类型，未复制任何值）**：
- `backend/conf/env.py` — 真实数据库口令与 SECRET（未入 git，磁盘明文；2025-09 已改为 getenv 读取但文件内仍留有真实值）
- `docker_env/mysql/launch.sh:5` — 硬编码 MySQL root 口令（已入 git 历史）
- `docker-compose.yml:30` — MYSQL_ROOT_PASSWORD 带弱默认值回退
- `README.md`、`docker_env/README.md` — 内置演示账号明文口令
- `backend/dvadmin/system/initialize.py:241-261` — 种子用户口令哈希（pbkdf2 串）
- `backend/dvadmin/utils/string_util.py:30` — 硬编码默认盐值
- `web/.env.test` — 测试环境后端公网 IP 硬编码
- `web/src/install.js:136-138` — 腾讯云 COS accessKey 占位（空值，非泄露）

**关键证据文件**（前缀 `D:\projects\projects-old\django-vue-admin-pro\`）：`backend\dvadmin\system\models.py`（RBAC 三表+MD5 预哈希）、`backend\dvadmin\utils\permission.py`、`filters.py`（数据权限递归 bug）、`viewset.py`、`middleware.py`、`backend\application\settings.py`、`backend\application\urls.py`（exec 插件路由）、`backend\conf\env.example.py`、`docker-compose.yml`、`docker_env\nginx\my.conf`、`docker_env\django\Dockerfile`、`web\src\menu\index.js`、`web\src\router\index.js`、`web\package.json`；git 修复提交：eed7263/3df9286/8b39408/c8de391（权限过滤 bug、int→bool 契约、docker 日志、部门级联删除）。
