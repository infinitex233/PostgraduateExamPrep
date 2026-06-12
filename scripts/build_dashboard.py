#!/usr/bin/env python3
"""Build a self-contained HTML study dashboard from daily-log frontmatter.

Scans StudyProgress/DailyLogs/**/*.md, reads the YAML frontmatter block at the
top of each log, aggregates the structured data, and renders it into a single
zero-dependency HTML file (StudyProgress/dashboard.html) with all data, CSS and
JS inlined. Double-click the HTML to open it in any browser — no server needed.

The visual layout follows the frontend-slides skill conventions: a fixed
1920x1080 16:9 stage scaled to the viewport, slide navigation, print support.

Usage:
    python scripts/build_dashboard.py
"""

import json
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "StudyProgress" / "DailyLogs"
OUT_PATH = ROOT / "StudyProgress" / "dashboard.html"

# Subject -> display group / color. Keeps the dashboard palette stable.
SUBJECT_COLORS = {
    "数学-高数": "#e8590c",
    "数学-线代": "#f08c00",
    "数学-概率": "#f4b400",
    "专业课-数据结构": "#1971c2",
    "专业课-组成原理": "#1098ad",
    "专业课-操作系统": "#0c8599",
    "专业课-计算机网络": "#3b5bdb",
    "英语": "#2f9e44",
    "政治": "#c2255c",
}
DEFAULT_COLOR = "#868e96"


def parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter dict from a markdown file, or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip()
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as e:
        print(f"  [WARN] YAML parse error: {e}", file=sys.stderr)
        return None
    return data if isinstance(data, dict) else None


def load_logs() -> list[dict]:
    """Collect frontmatter from every daily log, sorted by date."""
    logs = []
    for md in sorted(LOGS_DIR.rglob("*.md")):
        if md.name.startswith("_"):
            continue  # skip _template.md
        fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        if not fm or not fm.get("date"):
            continue
        fm["_file"] = str(md.relative_to(ROOT)).replace("\\", "/")
        logs.append(fm)
    logs.sort(key=lambda x: str(x.get("date")))
    return logs


def aggregate(logs: list[dict]) -> dict:
    """Turn raw log dicts into the data object the dashboard consumes."""
    daily = []
    subject_totals: dict[str, int] = {}
    subject_days: dict[str, int] = {}
    progress_rows: list[dict] = []
    timeline: list[dict] = []
    total_minutes = 0
    studied_days = 0

    for log in logs:
        d = str(log.get("date"))
        subjects = log.get("subjects") or []
        per_subject = {}
        day_minutes = 0
        for s in subjects:
            if not isinstance(s, dict):
                continue
            name = s.get("name") or "未分类"
            t = s.get("time_min")
            t = int(t) if isinstance(t, (int, float)) else 0
            per_subject[name] = per_subject.get(name, 0) + t
            subject_totals[name] = subject_totals.get(name, 0) + t
            subject_days[name] = subject_days.get(name, 0) + 1
            day_minutes += t

        # Prefer explicit total_minutes; fall back to sum of subjects.
        tm = log.get("total_minutes")
        tm = int(tm) if isinstance(tm, (int, float)) else day_minutes
        total_minutes += tm
        if tm > 0:
            studied_days += 1

        daily.append({
            "date": d,
            "total": tm,
            "subjects": per_subject,
            "mood": log.get("mood") or "",
            "tags": log.get("tags") or [],
        })

        for p in (log.get("progress") or []):
            if isinstance(p, dict) and p.get("chapter"):
                progress_rows.append({
                    "date": d,
                    "subject": p.get("subject", ""),
                    "chapter": p.get("chapter", ""),
                    "status": p.get("status", ""),
                })

        tags = log.get("tags") or []
        if tags:
            timeline.append({"date": d, "tags": tags, "mood": log.get("mood") or ""})

    # Latest chapter per subject (most recent progress row wins).
    latest_chapter: dict[str, dict] = {}
    for row in progress_rows:
        latest_chapter[row["subject"]] = row

    return {
        "generated": date.today().isoformat(),
        "daily": daily,
        "subject_totals": subject_totals,
        "subject_days": subject_days,
        "progress_rows": progress_rows,
        "latest_chapter": latest_chapter,
        "timeline": timeline,
        "summary": {
            "total_minutes": total_minutes,
            "studied_days": studied_days,
            "log_count": len(logs),
            "first_date": daily[0]["date"] if daily else None,
            "last_date": daily[-1]["date"] if daily else None,
            "avg_minutes": round(total_minutes / studied_days) if studied_days else 0,
        },
    }


# --- viewport-base.css (from frontend-slides skill, inlined for zero deps) ---
VIEWPORT_CSS = """
html,body{width:100%;height:100%;margin:0;overflow:hidden;background:var(--stage-bg,#000);}
.deck-viewport{position:fixed;inset:0;overflow:hidden;background:var(--stage-bg,#000);}
.deck-stage{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;transform-origin:0 0;background:var(--slide-bg,#fff);}
.slide{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;display:block;visibility:hidden;opacity:0;pointer-events:none;background:var(--slide-bg,#fff);}
.slide.active{visibility:visible;opacity:1;pointer-events:auto;z-index:1;}
img,video,canvas,svg{max-width:100%;max-height:100%;}
@media print{html,body{width:1920px;height:auto;overflow:visible;background:#fff;}.deck-viewport{position:static;overflow:visible;}.deck-stage{position:static;width:auto;height:auto;transform:none!important;}.slide{position:relative;display:block!important;visibility:visible!important;opacity:1!important;width:1920px;height:1080px;break-after:page;page-break-after:always;}.slide:last-child{break-after:auto;}.deck-controls{display:none!important;}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.2s!important;}}
"""


def build_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    colors = json.dumps(SUBJECT_COLORS, ensure_ascii=False)
    default_color = DEFAULT_COLOR
    return HTML_TEMPLATE.format(
        viewport_css=VIEWPORT_CSS,
        payload=payload,
        colors=colors,
        default_color=default_color,
    )


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>考研备考 · 学习看板</title>
<style>
{viewport_css}

:root {{
  --stage-bg: #0a0e14;
  --ink: #1a1d24;
  --paper: #f5f1e8;
  --paper-2: #ebe4d6;
  --accent: #e8590c;
  --muted: #6b7280;
  --line: #d8cfbe;
}}

* {{ box-sizing: border-box; }}

.deck-stage, .slide {{ --slide-bg: var(--paper); }}

.slide {{
  font-family: "Georgia", "Songti SC", "STSong", "SimSun", serif;
  color: var(--ink);
  padding: 90px 110px;
}}

/* Grain / paper texture via layered gradients */
.slide::before {{
  content: "";
  position: absolute; inset: 0;
  background:
    radial-gradient(circle at 12% 18%, rgba(232,89,12,.05), transparent 40%),
    radial-gradient(circle at 88% 82%, rgba(16,152,173,.05), transparent 42%);
  pointer-events: none;
}}

.kicker {{
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 22px; letter-spacing: .5em;
  color: var(--accent); text-transform: uppercase;
  margin-bottom: 14px; font-weight: 700;
}}
h1.title {{ font-size: 96px; line-height: 1.05; margin: 0 0 8px; letter-spacing: -.01em; }}
h2.head {{
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 52px; font-weight: 800; margin: 0 0 36px;
  display: flex; align-items: center; gap: 20px;
}}
h2.head::before {{
  content: ""; width: 14px; height: 52px; background: var(--accent);
  border-radius: 3px; display: inline-block;
}}
.sub {{ font-family: "PingFang SC","Microsoft YaHei",sans-serif; color: var(--muted); font-size: 26px; }}

/* Cover */
.cover {{ display: flex; flex-direction: column; justify-content: center; height: 100%; }}
.cover .meta {{ margin-top: 60px; display: flex; gap: 70px; font-family: "PingFang SC",sans-serif; }}
.cover .meta .num {{ font-size: 84px; font-weight: 800; color: var(--accent); line-height: 1; }}
.cover .meta .lbl {{ font-size: 24px; color: var(--muted); margin-top: 10px; }}

/* Stat cards row */
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 28px; margin-bottom: 50px; }}
.stat {{
  background: var(--paper-2); border: 1px solid var(--line);
  border-radius: 16px; padding: 32px 34px;
  font-family: "PingFang SC","Microsoft YaHei",sans-serif;
}}
.stat .v {{ font-size: 64px; font-weight: 800; color: var(--ink); line-height: 1; }}
.stat .v small {{ font-size: 28px; color: var(--muted); font-weight: 600; }}
.stat .k {{ font-size: 24px; color: var(--muted); margin-top: 14px; }}

/* Bar chart (daily minutes) */
.chart {{ display: flex; align-items: flex-end; gap: 26px; height: 400px; padding: 0 10px; }}
.bar-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }}
.bar-stack {{ width: 78%; display: flex; flex-direction: column-reverse; border-radius: 8px 8px 0 0; overflow: hidden; box-shadow: 0 6px 18px rgba(0,0,0,.12); }}
.bar-seg {{ width: 100%; }}
.bar-total {{
  font-family: "PingFang SC",sans-serif; font-size: 22px; font-weight: 700;
  margin-bottom: 12px; color: var(--ink);
}}
.bar-date {{ font-family: "PingFang SC",sans-serif; font-size: 20px; color: var(--muted); margin-top: 16px; }}
.bar-tag {{ font-size: 18px; }}

.legend {{ display: flex; flex-wrap: wrap; gap: 18px 32px; margin-top: 40px; font-family: "PingFang SC",sans-serif; font-size: 24px; }}
.legend .item {{ display: flex; align-items: center; gap: 10px; color: var(--ink); }}
.legend .dot {{ width: 18px; height: 18px; border-radius: 4px; }}

/* Subject progress list */
.prog {{ display: flex; flex-direction: column; gap: 26px; font-family: "PingFang SC","Microsoft YaHei",sans-serif; }}
.prow {{ display: grid; grid-template-columns: 360px 1fr 200px; align-items: center; gap: 30px; }}
.prow .name {{ font-size: 34px; font-weight: 700; display: flex; align-items: center; gap: 16px; }}
.prow .name .dot {{ width: 22px; height: 22px; border-radius: 6px; }}
.prow .chap {{ font-size: 30px; color: var(--ink); }}
.prow .time {{ font-size: 28px; color: var(--muted); text-align: right; }}
.track {{ height: 22px; background: var(--paper-2); border-radius: 11px; overflow: hidden; border: 1px solid var(--line); }}
.track > div {{ height: 100%; border-radius: 11px; }}

.badge {{ font-size: 22px; padding: 4px 16px; border-radius: 999px; font-weight: 700; }}
.badge.完结 {{ background: #2f9e4422; color: #2f9e44; }}
.badge.进行中 {{ background: #f08c0022; color: #e8590c; }}
.badge.起步 {{ background: #1971c222; color: #1971c2; }}

/* Timeline */
.tl {{ font-family: "PingFang SC","Microsoft YaHei",sans-serif; display: flex; flex-direction: column; gap: 28px; }}
.tl .ev {{ display: flex; align-items: baseline; gap: 28px; border-left: 4px solid var(--line); padding: 6px 0 6px 32px; position: relative; }}
.tl .ev::before {{ content: ""; position: absolute; left: -11px; top: 14px; width: 18px; height: 18px; border-radius: 50%; background: var(--accent); }}
.tl .ev .d {{ font-size: 30px; font-weight: 800; color: var(--ink); min-width: 200px; }}
.tl .ev .body {{ font-size: 28px; color: var(--ink); }}
.tl .chip {{ display: inline-block; font-size: 22px; padding: 3px 14px; border-radius: 999px; background: var(--paper-2); border: 1px solid var(--line); margin-right: 10px; color: var(--ink); }}

.foot {{ position: absolute; bottom: 46px; right: 110px; font-family: "PingFang SC",sans-serif; font-size: 20px; color: var(--muted); }}
.foot-l {{ position: absolute; bottom: 46px; left: 110px; font-family: "PingFang SC",sans-serif; font-size: 20px; color: var(--muted); letter-spacing: .2em; }}

.controls {{
  position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%);
  z-index: 1000; display: flex; gap: 8px; align-items: center;
  background: rgba(10,14,20,.82); padding: 8px 14px; border-radius: 999px;
  font-family: "PingFang SC",sans-serif; color: #fff; font-size: 16px; backdrop-filter: blur(8px);
}}
.controls button {{ background: rgba(255,255,255,.12); color: #fff; border: 0; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; font-size: 18px; }}
.controls button:hover {{ background: rgba(255,255,255,.25); }}
.controls .pg {{ min-width: 56px; text-align: center; font-variant-numeric: tabular-nums; }}
</style>
</head>
<body>
<div class="deck-viewport">
  <div class="deck-stage" id="stage"></div>
</div>
<div class="controls">
  <button id="prev">‹</button>
  <span class="pg"><span id="cur">1</span> / <span id="tot">1</span></span>
  <button id="next">›</button>
</div>

<script id="data" type="application/json">{payload}</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const COLORS = {colors};
const DEFAULT_COLOR = "{default_color}";
const colorFor = s => COLORS[s] || DEFAULT_COLOR;
const fmtH = m => {{
  if (!m) return '0';
  const h = Math.floor(m/60), mm = m%60;
  return h ? (mm ? `${{h}}h${{mm}}m` : `${{h}}h`) : `${{mm}}m`;
}};
const mmdd = d => (d||'').slice(5);

function el(tag, cls, html) {{
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}}

// ---- Slide builders ----
function coverSlide() {{
  const s = DATA.summary;
  const sl = el('section', 'slide cover');
  sl.innerHTML = `
    <div class="kicker">11408 · 考研备考</div>
    <h1 class="title">学习看板</h1>
    <div class="sub">${{s.first_date || ''}} — ${{s.last_date || ''}} · 持续记录中</div>
    <div class="meta">
      <div><div class="num">${{s.log_count}}</div><div class="lbl">记录天数</div></div>
      <div><div class="num">${{(s.total_minutes/60).toFixed(1)}}</div><div class="lbl">累计学时</div></div>
      <div><div class="num">${{fmtH(s.avg_minutes)}}</div><div class="lbl">日均学时</div></div>
    </div>
    <div class="foot-l">STUDY DASHBOARD</div>`;
  return sl;
}}

function trendSlide() {{
  const sl = el('section', 'slide');
  sl.appendChild(el('div', 'kicker', '投入趋势'));
  sl.appendChild(el('h2', 'head', '每日学习时长'));

  // stat cards
  const s = DATA.summary;
  const maxDay = DATA.daily.reduce((a,b)=>b.total>a.total?b:a, {{total:0,date:''}});
  const stats = el('div', 'stats');
  stats.innerHTML = `
    <div class="stat"><div class="v">${{(s.total_minutes/60).toFixed(1)}}<small> h</small></div><div class="k">累计学时</div></div>
    <div class="stat"><div class="v">${{fmtH(s.avg_minutes)}}</div><div class="k">日均（学习日）</div></div>
    <div class="stat"><div class="v">${{fmtH(maxDay.total)}}</div><div class="k">单日最高 · ${{mmdd(maxDay.date)}}</div></div>
    <div class="stat"><div class="v">${{s.studied_days}}<small> 天</small></div><div class="k">有效学习日</div></div>`;
  sl.appendChild(stats);

  // chart
  const allSubs = Object.keys(DATA.subject_totals);
  const maxT = Math.max(...DATA.daily.map(d=>d.total), 1);
  const chart = el('div', 'chart');
  DATA.daily.forEach(day => {{
    const col = el('div', 'bar-col');
    col.appendChild(el('div', 'bar-total', day.total ? fmtH(day.total) : '·'));
    const stack = el('div', 'bar-stack');
    stack.style.height = `${{Math.max(day.total/maxT*100, day.total?3:0)}}%`;
    allSubs.forEach(sub => {{
      const v = day.subjects[sub] || 0;
      if (!v) return;
      const seg = el('div', 'bar-seg');
      seg.style.height = `${{v/day.total*100}}%`;
      seg.style.background = colorFor(sub);
      seg.title = `${{sub}} ${{fmtH(v)}}`;
      stack.appendChild(seg);
    }});
    col.appendChild(stack);
    const tag = day.tags && day.tags.length ? ` <span class="bar-tag">${{day.tags.includes('受伤')?'🩹':(day.tags.includes('章节完结')?'✓':'')}}</span>` : '';
    col.appendChild(el('div', 'bar-date', mmdd(day.date) + tag));
    chart.appendChild(col);
  }});
  sl.appendChild(chart);

  const legend = el('div', 'legend');
  allSubs.forEach(sub => {{
    const i = el('div', 'item');
    i.innerHTML = `<span class="dot" style="background:${{colorFor(sub)}}"></span>${{sub}} · ${{fmtH(DATA.subject_totals[sub])}}`;
    legend.appendChild(i);
  }});
  sl.appendChild(legend);
  return sl;
}}

function progressSlide() {{
  const sl = el('section', 'slide');
  sl.appendChild(el('div', 'kicker', '各科进度'));
  sl.appendChild(el('h2', 'head', '科目投入与章节推进'));

  const subs = Object.keys(DATA.subject_totals).sort((a,b)=>DATA.subject_totals[b]-DATA.subject_totals[a]);
  const maxT = Math.max(...subs.map(s=>DATA.subject_totals[s]), 1);
  const prog = el('div', 'prog');
  subs.forEach(sub => {{
    const t = DATA.subject_totals[sub];
    const lc = DATA.latest_chapter[sub];
    const row = el('div', 'prow');
    const badge = lc && lc.status ? `<span class="badge ${{lc.status}}">${{lc.status}}</span>` : '';
    const chap = lc && lc.chapter ? `${{lc.chapter}} ${{badge}}` : '<span style="color:var(--muted)">—</span>';
    row.innerHTML = `
      <div class="name"><span class="dot" style="background:${{colorFor(sub)}}"></span>${{sub}}</div>
      <div>
        <div class="chap" style="margin-bottom:10px">${{chap}}</div>
        <div class="track"><div style="width:${{t/maxT*100}}%;background:${{colorFor(sub)}}"></div></div>
      </div>
      <div class="time">${{fmtH(t)}} · ${{DATA.subject_days[sub]}}天</div>`;
    prog.appendChild(row);
  }});
  sl.appendChild(prog);
  sl.appendChild(el('div', 'foot', '条形长度 = 累计学时占比'));
  return sl;
}}

function timelineSlide() {{
  const sl = el('section', 'slide');
  sl.appendChild(el('div', 'kicker', '复盘 · 杂谈'));
  sl.appendChild(el('h2', 'head', '关键节点与状态'));
  const tl = el('div', 'tl');
  // progress milestones + tagged days, merged & sorted
  const evs = [];
  DATA.progress_rows.filter(p=>p.status==='完结'||p.status==='起步').forEach(p=>{{
    evs.push({{date:p.date, body:`${{p.subject}} · ${{p.chapter}} <span class="badge ${{p.status}}">${{p.status}}</span>`}});
  }});
  DATA.timeline.forEach(t=>{{
    const chips = t.tags.map(x=>`<span class="chip">${{x}}</span>`).join('');
    if (t.tags.some(x=>x!=='章节完结')) evs.push({{date:t.date, body:`${{chips}}${{t.mood?' '+t.mood:''}}`}});
  }});
  evs.sort((a,b)=>a.date.localeCompare(b.date));
  evs.forEach(e=>{{
    const ev = el('div', 'ev');
    ev.innerHTML = `<div class="d">${{e.date}}</div><div class="body">${{e.body}}</div>`;
    tl.appendChild(ev);
  }});
  if (!evs.length) tl.appendChild(el('div', 'body', '暂无标记事件'));
  sl.appendChild(tl);
  sl.appendChild(el('div', 'foot', '事件来自日志 tags / 章节进度'));
  return sl;
}}

// ---- Assemble deck ----
const stage = document.getElementById('stage');
[coverSlide(), trendSlide(), progressSlide(), timelineSlide()].forEach(s => stage.appendChild(s));
const slides = Array.from(stage.children);
let idx = 0;
document.getElementById('tot').textContent = slides.length;

function fit() {{
  const s = Math.min(innerWidth/1920, innerHeight/1080);
  stage.style.transform = `translate(${{(innerWidth-1920*s)/2}}px,${{(innerHeight-1080*s)/2}}px) scale(${{s}})`;
}}
function show(i) {{
  idx = Math.max(0, Math.min(slides.length-1, i));
  slides.forEach((s,n)=>s.classList.toggle('active', n===idx));
  document.getElementById('cur').textContent = idx+1;
}}
addEventListener('resize', fit);
document.getElementById('prev').onclick = ()=>show(idx-1);
document.getElementById('next').onclick = ()=>show(idx+1);
addEventListener('keydown', e=>{{
  if (e.key==='ArrowRight'||e.key===' ') show(idx+1);
  else if (e.key==='ArrowLeft') show(idx-1);
  else if (e.key==='Home') show(0);
  else if (e.key==='End') show(slides.length-1);
}});
fit(); show(0);
</script>
</body>
</html>
"""


def main():
    if not LOGS_DIR.is_dir():
        print(f"No logs dir: {LOGS_DIR}", file=sys.stderr)
        sys.exit(1)
    logs = load_logs()
    if not logs:
        print("No logs with frontmatter found. Add frontmatter to daily logs first.", file=sys.stderr)
        sys.exit(1)
    data = aggregate(logs)
    OUT_PATH.write_text(build_html(data), encoding="utf-8")
    s = data["summary"]
    print(f"[OK] {OUT_PATH.relative_to(ROOT)}")
    print(f"     {s['log_count']} logs · {s['first_date']}~{s['last_date']} · "
          f"{s['total_minutes']/60:.1f}h total · avg {s['avg_minutes']}min/day")


if __name__ == "__main__":
    main()
