# patent-disclosure-skill（专利交底书 AI Skill）- 项目经验总结

> 分析对象：`D:\projects\patent-disclosure-skill`（AgentSkill 技能包，v1.8.9，MIT）
> 分析方式：只读代码勘察 + 文档研读

## 一、项目背景

遵循 AgentSkills 规范的 **AI Agent 技能包**，核心使命："从项目文档到**可交付的技术交底书**：专利点挖掘、查新优先国知局公布公告站、脱敏成文与自检闭环"。目标用户是"有设计文档和代码、但没梳理专利点"的工程师，通过 Claude Code / Cursor 等宿主以自然语言触发。

解决的问题：
1. 有文档和代码但专利点没梳理
2. 交底书要系统框图、流程图，还要代理人能直接改的 Word
3. 定稿后多轮补材料、纠错，需要文件修改追溯
4. 国知局公布站检索要稳定爬取、精准检索

## 二、技术栈与结构

| 层 | 技术 |
|---|---|
| 语言 | Python 3.9+（工具脚本）+ Node.js（mermaid-cli 图示渲染） |
| 文档转换 | mammoth / python-pptx / python-docx |
| 公式渲染 | matplotlib mathtext |
| 查新爬虫 | playwright + Chromium（独立 requirements，不强制安装） |
| 宿主 | Claude Code / Cursor，依赖 `${CLAUDE_SKILL_DIR}` 定位技能根目录 |

### 目录结构

```
├── SKILL.md              # 唯一入口：触发条件、工具映射、8 步流程 + 迭代模式
├── prompts/              # ★ 核心：11 个分步提示词模板（intake/project_scan/patent_points_analyzer/
│                         #   prior_art_search/disclosure_builder/template_reference/self_check/merger/...）
├── tools/                # 9 个 Python 脚本 + package.json（mermaid_render/math_render/md_to_docx/
│                         #   docx_to_md/pptx_to_md/cnipa 三件套/iteration_dialog_log）
├── examples/             # 虚构案件"分布式批任务调度"，覆盖所有输入形态（验收用例兼教学材料）
├── tests/                # 3 个测试（1 个有断言）
└── outputs/              # 用户产出目录（整目录 .gitignore，涉密正确选择）
```

## 三、核心实现

### 工作流（8 步主流程 + 迭代模式）

```
用户触发 → Step1 intake(边界与输入) → Step2 project_scan(项目扫描)
→ Step3-4 专利点挖掘与融合 → Step5 联网查新(优先国知局, 降级 WebSearch)
→ Step6 摘要预览确认 → Step7 交底书全文(七章结构+mermaid 图) → Step8 自检
→ 交付 {案件名}_{YYYYMMDDHHmmss}.md + .docx
→ 迭代: merger(补材料)/correction_handler(纠错) → 新时间戳文件 + 修订对话记录
```

**关键设计：迭代模式按意图识别**——用户明显在已有交底书上工作时必须走迭代流程，**禁止**默认绕回重新挖掘专利点。针对 Agent 行为漂移的强约束。

### 输出规范（七章结构）

注意事项 → 背景/现有技术 → 技术方案（系统框图 mermaid + 模块功能 + 流程图 + 公式 + 参数表）→ 优点 → 技术关键点和欲保护点 → 其它（实施例/效果/参数示例）。

硬性规范：双格式交付（.md + .docx）、时间戳命名不覆盖旧稿、文件名去 Windows 非法字符、脱敏（业务名→通用描述、数值→范围、公司名→"某系统"）、禁止捏造 URL、禁止正文含自检清单。

### 查新契约设计（最精细的部分）

- **渠道优先级**：国知局公布公告站（官方）→ 降级 Google 学术/Patents
- **检索词工程**：2-8 个语义块（术语/名词短语/名动组合），禁止泛词、禁止无空格长句整句（极易 0 条）
- **执行约定**：每轮 Bash 只传一个词块，2-8 次独立调用（链路过长会触发宿主超时）
- **机器可解析输出契约**：stdout 仅一行 `EPUB_HITS_JSON:` + JSON；stderr 全 ASCII——针对 PowerShell 把中文 stderr 误判为 NativeCommandError 的实战妥协
- **反幻觉**：命中条目含 abstract 时必须先完整读摘要再写；URL 写入前必须浏览器核验；1.1 检索说明不得暴露内部流程元信息

## 四、设计亮点（可复用模式）

1. **提示词与代码解耦，prompt 即文档**：`prompts/` 既是 Agent 运行时指令也是人读的规格文档；SKILL.md 只做编排与索引
2. **执行门禁（gate）**：merger/correction_handler 文首强制"先读上下文、先读当前定稿、结果必须落新时间戳文件"，标注"优先执行，不可跳过"
3. **强制输出锚点**：必须输出固定标题「## 合并摘要（留档）」，"若未输出本节，视为未完成本 prompt"
4. **Agent 自用检查清单**：6 条自查项与正文交付物解耦，纯内部约束
5. **失败降级哲学**："不中断、保留原文、给出人工补跑命令"贯穿所有脚本——mermaid 失败保留围栏、公式失败保留 LaTeX、Word 失败提示手动命令、查新失败降级 WebSearch
6. **幂等可重跑**：已带处理标记的围栏跳过不重渲染
7. **格式约定防御 Windows 生态**：stdout 单行 JSON + stderr ASCII + UTF-8 环境兜底，把"工具输出解析可靠性"当一等公民
8. **版本追溯零基础设施**：时间戳文件名并存 + 追加式修订对话记录，明确不需要子目录或快照脚本
9. **跨文件编号引用**：§7.3/§7.6/§7.7 多文件交叉引用，单一事实源 + 引用体系

### 工具脚本技术点

- `mermaid_render.py`：三级查找 mmdc（node_modules → PATH → npx），Windows 上 npx 是 .ps1 需 `shell=True`；`-s 2` 双倍像素密度；Markdown 保留源码 + HTML 注释插图（预览/交付双轨制）
- `md_to_docx.py`（1007 行，纯 python-docx）：**手写 PNG/GIF/JPEG 二进制头解析像素尺寸**实现等比缩放；表格解析器专门处理 `\(...\)`/`$...$`/`\|` 内竖线不拆列（有测试覆盖）
- `math_render.py`：mathtext 简写归一化表（`\ge`→`\geq` 等）
- 国知局三件套：Playwright 轮询等 `#searchStr`（最长 180s）+ 真实浏览器指纹过 WAF + 导航竞态重试（最多 10 次）；解析三套布局兼容 + 多重降级

## 五、踩坑经验

| 坑 | 解法 |
|---|---|
| 国知局站点 WAF/JS 渲染高失败率 | Playwright 轮询 + 桌面 UA + `--disable-blink-features=AutomationControlled` |
| 单个 Bash 链路过长触发宿主超时 | 强制"每词一次调用"拆分进程 |
| mathtext 不识别 `\ge`/`\le`/`\text{且}` | 归一化映射表 |
| puppeteer 23+ 不自动下载浏览器 | 手动 `npx puppeteer browsers install chrome-headless-shell` |
| PowerShell 把中文 stderr 误判 NativeCommandError | stderr 全 ASCII + stdout 单行 JSON 契约 |
| mammoth Markdown 输出已 deprecated、复杂排版弱 | 建议先导出 PDF/纯文本 |
| 站点验证码启用 | 无破解逻辑，预留 `PLAYWRIGHT_HEADED=1` 人工辅助 |

## 六、改进建议

- **测试体系**：2/3 测试无断言且依赖外部环境会静默跳过；建议 pytest + skipif 显式标记；`cnipa_epub_parse.py` 用 fixtures HTML 离线测试（不依赖网络）
- **提示词维护性**：交叉引用规则散布 6+ 文件易漏改，建议 template_reference.md 沉淀单一事实源；SKILL.md 超长单行可拆分小节
- **爬虫健壮性**：解析 0 条且 HTML 正常时应结构化告警；README 明确合规边界
- **工程化**：无 CI、依赖未锁定（requirements 用 `>=`）；建议 tools/selfcheck 一键验证脚本

## 结论

工程质量明显高于一般 AI 提示词仓库的 AgentSkill 项目——形成了"编排（SKILL.md）+ 分步指令（prompts/）+ 工具链（tools/）+ 示例验证（examples/）+ 自检闭环"的完整产品。核心经验：

1. **Agent 流程用"门禁 + 强制输出锚点 + 检查清单"对抗行为漂移**
2. **工具输出为 Agent 解析设计契约**（单行 JSON、ASCII stderr、幂等可重跑）
3. **反幻觉约束落在具体规则上**（abstract 必用、URL 必核验、禁止捏造偏向），而非泛泛"不要编造"
4. **降级路径是 Agent 流程的保命绳**，每个外部依赖都要有失败兜底
5. **版本追溯用时间戳文件 + 追加日志**，零基础设施
