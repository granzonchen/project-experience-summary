#!/usr/bin/env node
/**
 * publish-audit.mjs —— 推送前敏感体检（本仓专用）
 *
 * 本仓是**有意公开**的项目经验仓库，因此：
 *   · 采集：明文凭据、内网/部署地址、内网域名（这些都不该出现在公开可见的提交里）
 *   · 不采集：客户/企业名、项目技术细节（本仓的内容本体，已确认可公开）
 *
 * 用法：node scripts/publish-audit.mjs [ref]     # 默认 HEAD；命中则退出码 1
 *
 * 设计约定（经验教训）：
 *   · 规则不内嵌被校验对象的规则（本文件自身已加入排除，避免自我命中）
 *   · 报告全量计数，不静默截断
 *   · 在 Node 侧执行（不经 shell）——MSYS 会把参数里的反斜杠转成 "/"，使规则静默失效
 */
import { spawnSync } from 'node:child_process';

const REF = process.argv[2] || 'HEAD';
const SELF = ['scripts/publish-audit.mjs', '.githooks/pre-push'];

const RULES = [
  { name: 'sk- 类密钥', pat: 'sk-[A-Za-z0-9_-]{16,}' },
  { name: 'GitHub PAT', pat: 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}' },
  { name: 'AWS AK', pat: 'AKIA[0-9A-Z]{16}' },
  { name: '私钥块', pat: 'BEGIN [A-Z ]*PRIVATE KEY' },
  { name: '连接串带账号', pat: '://[^/[:space:]]+:[^/@[:space:]]+@' },
  { name: '口令/密钥赋值', pat: '(?i)(password|passwd|pwd|secret|token|api[_-]?key)["\']?[[:space:]]*[:=][[:space:]]*["\']?[A-Za-z0-9_/-]{12,}' },
  { name: 'RFC1918 内网 IP', pat: '192\\.168\\.[0-9]+\\.[0-9]+|(^|[^0-9])10\\.[0-9]+\\.[0-9]+\\.[0-9]+|172\\.(1[6-9]|2[0-9]|3[01])\\.[0-9]+\\.[0-9]+' },
  { name: '非回环 IP:端口', pat: '[0-9]{1,3}(\\.[0-9]{1,3}){3}:[0-9]{2,5}', ignore: /^(127\.0\.0\.1|0\.0\.0\.0):/ },
  { name: '内网域名', pat: 'tltim\\.com\\.cn' },
];

function git(args) {
  const r = spawnSync('git', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  return { ok: r.status === 0, out: (r.stdout || '').trim() };
}

function scan(ref) {
  const hits = [];
  for (const rule of RULES) {
    const args = ['-c', 'core.quotepath=false', 'grep', '-nIE', rule.pat, ref, '--', '.'];
    SELF.forEach((s) => args.push(`:(exclude)${s}`));
    const r = git(args);
    if (!r.ok || !r.out) continue;
    const re = rule.ignore ? new RegExp(rule.pat, 'g') : null;
    const all = r.out.split('\n').filter(Boolean).filter((line) => {
      if (!re) return true;
      return (line.match(re) || []).some((v) => !rule.ignore.test(v));
    });
    if (all.length) hits.push({ name: rule.name, count: all.length, lines: all });
  }
  return hits;
}

const hits = scan(REF);
if (!hits.length) {
  console.log(`[publish-audit] ${REF} 体检通过：0 命中（${RULES.length} 条规则）`);
  process.exit(0);
}
console.error(`[publish-audit] ${REF} 体检发现 ${hits.length} 类命中，已拒绝推送：`);
for (const h of hits) {
  console.error(`  [${h.name}] 共 ${h.count} 行`);
  h.lines.slice(0, 6).forEach((l) => console.error(`      ${l.slice(0, 180)}`));
  if (h.count > 6) console.error(`      …（另有 ${h.count - 6} 行未列出）`);
}
console.error('\n处理：改为占位符（如 <DB_HOST>:<DB_PORT>）或用环境变量注入；不要复述原值。');
process.exit(1);
