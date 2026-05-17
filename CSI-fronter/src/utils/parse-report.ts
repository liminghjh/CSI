/**
 * Parse Python repr strings from backend into proper markdown.
 *
 * Backend returns str(report) which is a Python repr like:
 *   FullSecurityReport(report_title='...', target_info=TargetInfo(ip='..',..), ...)
 *   FlagCaptureResult(flag='flag{...}', challenge_type='Web', attack_path='...')
 *
 * This module extracts fields, converts literal \n to real newlines,
 * and builds formatted markdown for rendering.
 */

function unescape(str: string): string {
  return str.replace(/\\n/g, '\n').replace(/\\'/g, "'").replace(/\\"/g, '"')
}

/** Extract a quoted string value for a given key from Python repr (handles both single and double quotes) */
function extractStr(repr: string, key: string): string | null {
  const sqRe = new RegExp(`${escapeRe(key)}=('(?:[^'\\\\]|\\\\.)*')`)
  const sqm = repr.match(sqRe)
  if (sqm && sqm[1]) return unescape(sqm[1].slice(1, -1))

  const dqRe = new RegExp(`${escapeRe(key)}=("(?:[^"\\\\]|\\\\.)*")`)
  const dqm = repr.match(dqRe)
  if (dqm && dqm[1]) return unescape(dqm[1].slice(1, -1))

  return null
}

function extractInt(repr: string, key: string): number | null {
  const re = new RegExp(`${escapeRe(key)}=(\\d+)`)
  const m = repr.match(re)
  if (!m || !m[1]) return null
  return parseInt(m[1], 10)
}

function extractNested(repr: string, key: string): string | null {
  const simpleRe = new RegExp(`${escapeRe(key)}=([A-Z][a-zA-Z]*\\([^)]*(?:\\([^)]*\\)[^)]*)*\\))`)
  const m = repr.match(simpleRe)
  if (!m || !m[1]) return null
  return m[1]
}

function extractList(repr: string, key: string): string[] {
  const re = new RegExp(`${escapeRe(key)}=\\[(.*?)\\]`, 's')
  const m = repr.match(re)
  if (!m || !m[1]) return []
  const content = m[1]
  const items: string[] = []
  let depth = 0
  let start = 0
  for (let i = 0; i < content.length; i++) {
    if (content[i] === '(') depth++
    else if (content[i] === ')') depth--
    else if (content[i] === ',' && depth === 0) {
      items.push(content.slice(start, i).trim())
      start = i + 1
    }
  }
  const last = content.slice(start).trim()
  if (last) items.push(last)
  return items
}

function escapeRe(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// ---- Formatting ----

function formatReport(repr: string): string {
  const title = extractStr(repr, 'report_title') || '安全检测报告'
  const target = extractNested(repr, 'target_info')
  const exec = extractNested(repr, 'executive_summary')
  const vulnItems = extractList(repr, 'vulnerabilities')
  const summary = extractStr(repr, 'summary') || ''

  const lines: string[] = []
  lines.push(`# ${title}`, '')

  // Target info
  if (target) {
    const ip = extractStr(target, 'ip') || '-'
    const domain = extractStr(target, 'domain') || '-'
    const scan = extractStr(target, 'scan_range') || '-'
    lines.push('## 目标信息', '')
    lines.push(`| IP | 域名 | 检测范围 |`)
    lines.push(`|---|---|---|`)
    lines.push(`| ${ip} | ${domain} | ${scan} |`)
    lines.push('')
  }

  // Executive summary
  if (exec) {
    const risk = extractStr(exec, 'risk_level') || '-'
    const total = extractInt(exec, 'total_vulnerabilities') ?? '-'
    const assessment = extractStr(exec, 'overall_assessment') || ''
    lines.push('## 执行摘要', '')
    lines.push(`| 风险等级 | 漏洞总数 |`)
    lines.push(`|---|---|`)
    lines.push(`| ${risk} | ${total} |`)
    lines.push('')
    if (assessment) {
      lines.push(`**总体评估**: ${assessment}`, '')
    }
  }

  // Vulnerabilities
  if (vulnItems.length > 0) {
    lines.push('## 漏洞详情', '')
    for (const item of vulnItems) {
      const id = extractStr(item, 'id') || '-'
      const name = extractStr(item, 'name') || '-'
      const desc = extractStr(item, 'description') || '-'
      const remediation = extractStr(item, 'remediation') || '-'
      lines.push(`### ${id}: ${name}`, '')
      lines.push(`**描述**: ${desc}`, '')
      lines.push(`**修复建议**: ${remediation}`, '')
    }
  }

  // Summary
  if (summary) {
    lines.push('## 报告总结', '')
    lines.push(summary, '')
  }

  return lines.join('\n')
}

function formatFlag(repr: string): string {
  const flag = extractStr(repr, 'flag') || '-'
  const type = extractStr(repr, 'challenge_type') || '-'
  const path = extractStr(repr, 'attack_path') || '-'

  const lines: string[] = []
  lines.push('# Flag 夺取结果', '')
  lines.push(`| Flag | 赛题类型 |`)
  lines.push(`|---|---|`)
  lines.push(`| \`${flag}\` | ${type} |`)
  lines.push('')
  lines.push(`**攻击路径**: ${path}`, '')

  return lines.join('\n')
}

export function parseAndFormat(text: string): string {
  if (!text) return '*暂无内容*'

  const s = text.trim()

  if (s.includes('report_title=')) {
    return formatReport(s)
  }
  if (s.includes('flag=') && s.includes('attack_path=')) {
    return formatFlag(s)
  }

  // Fallback: unknown format, treat as-is but unescape newlines
  return unescape(s)
}
