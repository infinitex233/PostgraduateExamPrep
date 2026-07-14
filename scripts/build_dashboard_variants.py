#!/usr/bin/env python3
"""Build the Capsule-styled dashboard.

This script generates the sole dashboard artifact:

- StudyProgress/dashboard.html
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import build_dashboard

OUT_DIR = ROOT / "StudyProgress"
PROGRESS_INDEX = ROOT / "StudyProgress" / "ProgressIndex.md"
MONTHLY_LOG_DIR = ROOT / "StudyProgress" / "DailyLogs" / "Monthly"
DASHBOARD_OUT = "dashboard.html"
STALE_DASHBOARD_FILES = [
    "dashboard_signal.html",
    "dashboard_capsule.html",
    "dashboard_capsule_dashboard.html",
    "DashboardTemplatePreviews.html",
    "dashboard_vellum.html",
]
CAPSULE_SUBJECT_COLORS = {
    "数学-高数": "#E85D4E",
    "数学-线代": "#C4D94E",
    "数学-概率": "#C5B5E0",
    "专业课-数据结构": "#8BB4F7",
    "专业课-组成原理": "#A06CE8",
    "专业课-操作系统": "#F2D160",
    "专业课-计算机网络": "#F5B895",
    "英语": "#A8E6CF",
    "政治": "#C5B5E0",
}
CAPSULE_DEFAULT_COLOR = "#FFFFFF"
SUBJECT_DISPLAY_NAMES = {
    "数学-概率": "数学-概统",
}


def display_subject(subject: str) -> str:
    return SUBJECT_DISPLAY_NAMES.get(subject, subject)


def canonical_subject(subject: str) -> str:
    return "数学-概率" if subject == "数学-概统" else subject


def fmt_minutes(minutes: int | float | None) -> str:
    if minutes is None:
        return "未说明"
    minutes = int(minutes)
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}h{m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def parse_duration(text: str) -> int:
    """Parse duration strings like 107h21min, 35min, or 4h."""
    total = 0
    h = re.search(r"(\d+)h", text)
    m = re.search(r"(\d+)m(?:in)?", text)
    if h:
        total += int(h.group(1)) * 60
    if m:
        total += int(m.group(1))
    return total


def parse_named_durations(text: str, pattern: str) -> list[dict]:
    """Parse semicolon-separated named duration summaries from ProgressIndex."""
    match = re.search(pattern, text)
    if not match:
        return []
    items = []
    for chunk in re.split(r"[；;]", match.group(1)):
        chunk = chunk.strip()
        item = re.match(r"(.+?)\s+(\d+h(?:\d+min)?|\d+min)", chunk)
        if not item:
            continue
        items.append({
            "name": canonical_subject(item.group(1).strip()),
            "minutes": parse_duration(item.group(2)),
        })
    return items


def parse_monthly_subjects(month: str) -> list[dict]:
    """Read concrete subject totals from a monthly summary note."""
    path = MONTHLY_LOG_DIR / f"{month}.md"
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    in_subjects = False
    subjects = []
    for line in text.splitlines():
        if line.startswith("## 分科记录"):
            in_subjects = True
            continue
        if in_subjects and line.startswith("## "):
            break
        if not in_subjects or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"科目", "---"} or set(cells[0]) == {"-"}:
            continue
        name = "其它" if cells[0] == "其他" else cells[0]
        subjects.append({"name": name, "minutes": parse_duration(cells[1])})
    return subjects


def parse_progress_index() -> dict:
    """Read imported-month totals from ProgressIndex.md."""
    if not PROGRESS_INDEX.exists():
        return {
            "months": [],
            "all_total": None,
            "exam_total": None,
            "other_total": None,
            "exam_subjects": [],
            "other_subjects": [],
        }

    text = PROGRESS_INDEX.read_text(encoding="utf-8")
    months = []
    in_months = False
    for line in text.splitlines():
        if line.startswith("## 月度概览"):
            in_months = True
            continue
        if in_months and line.startswith("## "):
            break
        if not in_months or not line.startswith("| 2026-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        months.append({
            "month": cells[0],
            "days": int(cells[1]),
            "total_minutes": parse_duration(cells[2]),
            "exam_minutes": parse_duration(cells[3]),
            "other_minutes": parse_duration(cells[4]),
            "subjects": parse_monthly_subjects(cells[0]),
        })

    obs = re.search(r"补录期总完成时长：([^，]+)，其中考研相关 ([^，]+)，课内/其他 ([^。]+)", text)
    exam_subjects = parse_named_durations(text, r"考研科目投入：([^。]+)")
    other_subjects = parse_named_durations(text, r"课内作业/期末复习及其他累计 [^：]+：([^。]+)")
    return {
        "months": months,
        "all_total": parse_duration(obs.group(1)) if obs else None,
        "exam_total": parse_duration(obs.group(2)) if obs else None,
        "other_total": parse_duration(obs.group(3)) if obs else None,
        "exam_subjects": exam_subjects,
        "other_subjects": other_subjects,
    }


def enriched_data() -> dict:
    data = build_dashboard.aggregate(build_dashboard.load_logs())
    archive = parse_progress_index()
    daily = data.get("daily") or []
    for month in archive.get("months", []):
        if month.get("subjects"):
            continue
        subject_totals: dict[str, int] = {}
        for day in daily:
            if not str(day.get("date", "")).startswith(month["month"]):
                continue
            for name, minutes in (day.get("subjects") or {}).items():
                display_name = "其它" if name == "其他" else name
                subject_totals[display_name] = subject_totals.get(display_name, 0) + int(minutes or 0)
        month["subjects"] = [
            {"name": name, "minutes": minutes}
            for name, minutes in sorted(subject_totals.items(), key=lambda item: item[1], reverse=True)
            if minutes
        ]
    data["archive"] = archive
    if archive["all_total"] is not None:
        data["summary"]["archive_total_minutes"] = archive["all_total"]
        data["summary"]["archive_exam_minutes"] = archive["exam_total"]
        data["summary"]["archive_other_minutes"] = archive["other_total"]
    else:
        data["summary"]["archive_total_minutes"] = data["summary"]["total_minutes"]
        data["summary"]["archive_exam_minutes"] = None
        data["summary"]["archive_other_minutes"] = None
    return data


def last_n_daily(data: dict, count: int = 14) -> list[dict]:
    return (data.get("daily") or [])[-count:]


def top_subjects(data: dict, count: int = 8) -> list[tuple[str, int]]:
    totals = data.get("subject_totals") or {}
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)[:count]


def html_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def pct(value: int | float, maximum: int | float) -> float:
    if maximum <= 0:
        return 0
    return max(0, min(100, value / maximum * 100))


def esc(value: object) -> str:
    return (
        str(value if value is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def split_exam_subjects(data: dict) -> tuple[int, int]:
    archive = data.get("archive") or {}
    exam = archive.get("exam_total")
    other = archive.get("other_total")
    if exam is None or other is None:
        return 0, 0
    return int(exam), int(other)


def capsule_color(subject: str) -> str:
    return CAPSULE_SUBJECT_COLORS.get(subject, CAPSULE_DEFAULT_COLOR)


def render_signal(data: dict) -> str:
    s = data["summary"]
    months = data["archive"]["months"]
    recent = last_n_daily(data)
    subjects = top_subjects(data)
    latest = data.get("latest_log") or {}
    exam_minutes, other_minutes = split_exam_subjects(data)
    recent_summary = data.get("recent") or {}

    max_month = max((m["total_minutes"] for m in months), default=1)
    max_day = max((d["total"] or 0 for d in recent), default=1)
    max_subject = max((m for _, m in subjects), default=1)

    trend_bars = "\n".join(
        f'<div class="trend-bar"><span>{fmt_minutes(day["total"])}</span>'
        f'<i style="height:{pct(day["total"] or 0, max_day):.1f}%"></i>'
        f'<em>{esc(day["date"][5:])}</em></div>'
        for day in recent
    )
    month_cards = "\n".join(
        f'<div class="month-card"><div><b>{esc(m["month"])}</b><span>{m["days"]} 天</span></div>'
        f'<strong>{fmt_minutes(m["total_minutes"])}</strong>'
        f'<div class="track"><i style="width:{pct(m["total_minutes"], max_month):.1f}%"></i></div>'
        f'<p>考研 {fmt_minutes(m["exam_minutes"])} · 课内/其他 {fmt_minutes(m["other_minutes"])}</p></div>'
        for m in months
    )
    subject_rows = "\n".join(
        f'<div class="subject-row"><b>{esc(name)}</b><div class="track">'
        f'<i style="width:{pct(minutes, max_subject):.1f}%"></i></div>'
        f'<span>{fmt_minutes(minutes)}</span></div>'
        for name, minutes in subjects
    )
    latest_subjects = "\n".join(
        f'<li><b>{esc(item["name"])}</b><span>{esc(item.get("detail") or item.get("result") or "未说明")}</span>'
        f'<em>{fmt_minutes(item.get("time_min"))}</em></li>'
        for item in (latest.get("subjects") or [])[:6]
    )
    actions = (latest.get("next_actions") or [])[:5]
    if not actions:
        actions = ["继续记录每日主线、分科用时和需要收尾的问题。"]
    action_items = "\n".join(f"<li>{esc(item)}</li>" for item in actions)
    issues = "\n".join(f"<li>{esc(item)}</li>" for item in (latest.get("issues") or [])[:4])

    progress_rows = []
    for name, minutes in subjects:
        latest_chapter = (data.get("latest_chapter") or {}).get(name) or {}
        done = (data.get("subject_chapters_done") or {}).get(name, 0)
        chapter = latest_chapter.get("chapter") or "尚未记录章节进度"
        status = latest_chapter.get("status") or ""
        progress_rows.append(
            f'<div class="progress-row"><b>{esc(name)}</b><span>{esc(chapter)}'
            f'{" · " + esc(status) if status else ""}</span><em>{done} 章完结 · {fmt_minutes(minutes)}</em></div>'
        )
    progress_html = "\n".join(progress_rows)

    log_rows = "\n".join(
        f'<div class="log-row"><b>{esc(day["date"])}</b><span>{esc(day.get("focus") or day.get("mood") or "未说明")}</span>'
        f'<em>{fmt_minutes(day.get("total"))}</em></div>'
        for day in reversed((data.get("daily") or [])[-4:])
    )
    timeline = "\n".join(
        f'<div class="node"><b>{esc(event["date"])}</b><span>{esc("；".join([m.get("chapter", "") for m in event.get("milestones", [])] + event.get("tags", [])) or event.get("mood") or "记录节点")}</span></div>'
        for event in reversed((data.get("timeline_events") or [])[-7:])
    )
    alert_items = "\n".join(
        f'<li><b>{esc(item["subject"])}</b><span>{esc(item["message"])}'
        f'{(" · 上次 " + esc(item["last_seen"])) if item.get("last_seen") else ""}</span></li>'
        for item in (data.get("alerts") or [])[:5]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="screen-orientation" content="landscape">
<title>11408 Signal Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap" rel="stylesheet">
<style>
:root {{
  --stage-bg:#111827; --navy:#1C2644; --navy-2:#15213C; --cream:#F0ECE3;
  --ink:#1A2030; --warm:#E2DCD0; --muted:#8A96A8; --soft:#B8C0CE;
  --gold:#C8A870; --amber:#D8B66F; --green:#8FAE9B; --red:#C98279;
  --border:#2E3D5C; --border-light:#CAC4B4;
  --serif:"Source Serif 4","Noto Sans SC",Georgia,serif;
  --sans:"DM Sans","Noto Sans SC",sans-serif;
  --mono:"IBM Plex Mono","Noto Sans SC",monospace;
}}
* {{ box-sizing:border-box; }}
html,body {{ width:100%; height:100%; margin:0; overflow:hidden; background:var(--stage-bg); }}
.deck-viewport {{ position:fixed; inset:0; overflow:hidden; background:var(--stage-bg); }}
.deck-stage {{ position:absolute; left:0; top:0; width: 1920px; height: 1080px; overflow:hidden; transform-origin:0 0; background:var(--navy); }}
.slide {{ position:absolute; inset:0; width: 1920px; height: 1080px; overflow:hidden; display:block; visibility:hidden; opacity:0; pointer-events:none; color:var(--warm); font-family:var(--sans); padding:68px 84px; background:
  linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
  linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px),
  var(--navy); background-size:80px 80px; }}
.slide.active,.slide.visible {{ visibility:visible; opacity:1; pointer-events:auto; z-index:1; }}
.slide.paper {{ color:var(--ink); background:var(--cream); }}
.chrome {{ display:flex; justify-content:space-between; align-items:center; padding-bottom:18px; border-bottom:1px solid var(--border); font-family:var(--mono); color:var(--muted); font-size:15px; letter-spacing:.12em; }}
.paper .chrome {{ border-bottom-color:var(--border-light); color:#5A6270; }}
.kicker {{ font-family:var(--mono); color:var(--gold); font-size:15px; letter-spacing:.14em; margin-bottom:18px; text-transform:uppercase; }}
h1,h2,h3 {{ margin:0; font-family:var(--serif); font-weight:600; letter-spacing:0; }}
h1 {{ font-size:118px; line-height:.94; }}
h2 {{ font-size:68px; line-height:1.02; }}
h3 {{ font-size:34px; line-height:1.18; }}
em,.gold {{ color:var(--gold); font-style:italic; }}
.lead {{ font-size:24px; line-height:1.65; color:var(--muted); margin:22px 0 0; }}
.paper .lead {{ color:#5A6270; }}
.cover-grid {{ display:grid; grid-template-columns:.86fr 1.14fr; gap:56px; padding-top:54px; }}
.cover-left {{ display:grid; align-content:start; gap:28px; }}
.brief-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.brief {{ border-top:1px solid var(--border); padding-top:16px; min-height:100px; }}
.brief b,.stat b,.big-number {{ display:block; font-family:var(--serif); color:var(--gold); font-size:48px; line-height:1; font-weight:600; }}
.brief span,.mono,.stat span {{ font-family:var(--mono); font-size:13px; color:var(--muted); letter-spacing:.06em; }}
.paper-card {{ background:var(--cream); color:var(--ink); padding:34px; min-height:744px; display:grid; grid-template-rows:auto 1fr auto; box-shadow:0 22px 60px rgba(0,0,0,.18); }}
.stat-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; }}
.stat {{ border-top:1px solid var(--border-light); padding-top:18px; }}
.stat b {{ font-size:50px; }}
.trend {{ height:330px; display:grid; grid-template-columns:repeat(14,1fr); gap:10px; align-items:end; margin-top:34px; }}
.trend-bar {{ display:grid; grid-template-rows:26px 1fr 24px; gap:7px; height:100%; text-align:center; font-family:var(--mono); font-size:12px; color:#6B7280; }}
.trend-bar i {{ align-self:end; display:block; min-height:6px; background:var(--gold); }}
.paper-card .trend-bar i {{ background:var(--navy); }}
.trend-bar em {{ color:#6B7280; font-style:normal; }}
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:42px; padding-top:44px; }}
.panel {{ border-top:1px solid var(--border); padding-top:22px; }}
.paper .panel {{ border-top-color:var(--border-light); }}
.month-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
.month-card {{ border:1px solid rgba(200,168,112,.38); padding:20px; min-height:154px; background:rgba(255,255,255,.025); }}
.month-card div:first-child {{ display:flex; justify-content:space-between; align-items:baseline; color:var(--muted); font-family:var(--mono); font-size:13px; }}
.month-card strong {{ display:block; margin:14px 0; font-family:var(--serif); font-size:42px; color:var(--gold); }}
.month-card p {{ margin:12px 0 0; color:var(--muted); font-size:17px; }}
.track {{ height:10px; background:rgba(255,255,255,.09); overflow:hidden; }}
.paper .track {{ background:rgba(28,38,68,.13); }}
.track i {{ display:block; height:100%; background:var(--gold); }}
.subject-row {{ display:grid; grid-template-columns:190px 1fr 110px; gap:16px; align-items:center; min-height:42px; font-size:17px; }}
.subject-row b {{ color:var(--warm); }}
.paper .subject-row b {{ color:var(--ink); }}
.subject-row span {{ font-family:var(--mono); color:var(--muted); font-size:13px; }}
.radar {{ display:grid; grid-template-columns:1.08fr .92fr; gap:36px; }}
.dial {{ position:relative; height:520px; border:1px solid var(--border-light); background:
  radial-gradient(circle at 50% 50%, rgba(28,38,68,.06) 0 16%, transparent 17%),
  linear-gradient(rgba(28,38,68,.08) 1px, transparent 1px),
  linear-gradient(90deg, rgba(28,38,68,.08) 1px, transparent 1px); background-size:100% 100%, 52px 52px, 52px 52px; }}
.dial .ring {{ position:absolute; border:1px solid rgba(28,38,68,.18); border-radius:50%; left:50%; top:50%; transform:translate(-50%,-50%); }}
.ring.r1 {{ width:160px; height:160px; }} .ring.r2 {{ width:300px; height:300px; }} .ring.r3 {{ width:440px; height:440px; }}
.dial-point {{ position:absolute; width:18px; height:18px; border-radius:50%; background:var(--gold); transform:translate(-50%,-50%); box-shadow:0 0 0 8px rgba(200,168,112,.18); }}
.dial-label {{ position:absolute; transform:translate(-50%,-50%); font-family:var(--mono); color:#5A6270; font-size:13px; white-space:nowrap; }}
.latest-list,.task-list,.alert-list {{ margin:24px 0 0; padding:0; list-style:none; display:grid; gap:14px; }}
.latest-list li {{ display:grid; grid-template-columns:150px 1fr 92px; gap:18px; padding-top:14px; border-top:1px solid var(--border); }}
.paper .latest-list li {{ border-top-color:var(--border-light); }}
.latest-list b,.task-list b,.alert-list b {{ color:var(--gold); font-family:var(--mono); font-size:13px; }}
.latest-list span {{ color:var(--muted); line-height:1.5; font-size:19px; }}
.latest-list em {{ color:var(--warm); font-style:normal; font-family:var(--mono); font-size:13px; }}
.paper .latest-list em {{ color:var(--ink); }}
.task-list li,.alert-list li {{ padding:14px 0 0; border-top:1px solid var(--border); color:var(--muted); line-height:1.5; font-size:21px; }}
.progress-row,.log-row,.node {{ display:grid; grid-template-columns:190px 1fr 160px; gap:20px; align-items:start; padding:15px 0; border-top:1px solid var(--border); }}
.node {{ grid-template-columns:150px 1fr; }}
.progress-row b,.log-row b,.node b {{ color:var(--gold); font-family:var(--mono); font-size:13px; }}
.progress-row span,.log-row span,.node span {{ color:var(--muted); line-height:1.5; font-size:19px; }}
.progress-row em,.log-row em {{ color:var(--warm); font-style:normal; font-family:var(--mono); font-size:13px; }}
.rotate-hint {{ position:fixed; inset:0; display:none; align-items:center; justify-content:center; z-index:3000; background:#111827; color:#E2DCD0; font:18px var(--sans); text-align:center; padding:30px; }}
@media (orientation: portrait) and (max-width:900px) {{ .rotate-hint {{ display:flex; }} }}
.deck-controls {{ position:fixed; left:50%; bottom:16px; transform:translateX(-50%); z-index:1000; }}
.deck-controls button {{ border:1px solid rgba(200,168,112,.55); background:rgba(28,38,68,.86); color:var(--gold); width:44px; height:34px; margin:0 4px; font-family:var(--mono); }}
.counter {{ color:var(--gold); font-family:var(--mono); margin:0 12px; }}
@media print {{ html,body{{width:1920px;height:auto;overflow:visible;background:#fff}} .deck-viewport{{position:static;overflow:visible;background:#fff}} .deck-stage{{position:static;width:auto;height:auto;transform:none!important;background:none}} .slide{{position:relative;display:block!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;width:1920px;height:1080px;break-after:page;page-break-after:always}} .slide:last-child{{break-after:auto;page-break-after:auto}} .deck-controls{{display:none!important}} }}
@media (prefers-reduced-motion:reduce) {{ *,*::before,*::after{{animation-duration:.01ms!important;transition-duration:.2s!important}} }}
</style>
</head>
<body data-dashboard-variant="signal">
<div class="rotate-hint">请将手机转为横屏查看。<br>这版看板为宽屏复盘布局。</div>
<div class="deck-viewport"><main class="deck-stage" id="deckStage">
<section class="slide active visible">
  <div class="chrome"><span>11408 COMMAND ROOM</span><span>{esc(s["first_date"])} / {esc(s["last_date"])}</span></div>
  <div class="cover-grid">
    <div class="cover-left">
      <div><div class="kicker">FOUNDATION PHASE</div><h1>Study <em>Signal</em><br>Dashboard</h1><p class="lead">把每日记录压成几组能行动的信号：总量、最近强度、科目重心、推进节点和下一步。</p></div>
      <div class="brief-grid">
        <div class="brief"><b>{fmt_minutes(exam_minutes)}</b><span>考研相关投入</span></div>
        <div class="brief"><b>{fmt_minutes(other_minutes)}</b><span>课内/其他投入</span></div>
        <div class="brief"><b>{fmt_minutes(recent_summary.get("total_minutes", 0))}</b><span>近 7 天投入</span></div>
        <div class="brief"><b>{fmt_minutes(recent_summary.get("avg_minutes", 0))}</b><span>近 7 天日均</span></div>
      </div>
    </div>
    <div class="paper-card">
      <div class="stat-grid">
        <div class="stat"><b>{fmt_minutes(s["archive_total_minutes"])}</b><span>累计完成</span></div>
        <div class="stat"><b>89</b><span>有效记录日</span></div>
        <div class="stat"><b>{fmt_minutes(s["total_minutes"])}</b><span>六月日志</span></div>
        <div class="stat"><b>{s["days_to_exam"]}</b><span>距初试天数</span></div>
      </div>
      <div class="trend">{trend_bars}</div>
      <div class="mono">最近记录：{esc(latest.get("date", "未说明"))} · {esc(latest.get("focus", "未说明"))}</div>
    </div>
  </div>
</section>
<section class="slide">
  <div class="chrome"><span>LOAD MAP</span><span>02 / 05</span></div>
  <div class="split">
    <div><div class="kicker">MONTHLY ROUTE</div><h2>月度负荷<br><em>看整体路线</em></h2><p class="lead">左侧是从 3 月以来的完整补录口径，右侧保留近 14 条记录的实际波动，用于判断最近是否在稳态推进。</p><div class="month-grid">{month_cards}</div></div>
    <div class="panel"><h3>近 14 条记录</h3><div class="trend" style="height:520px;margin-top:28px">{trend_bars}</div></div>
  </div>
</section>
<section class="slide paper">
  <div class="chrome"><span>SUBJECT RADAR</span><span>03 / 05</span></div>
  <div class="radar" style="padding-top:42px">
    <div><div class="kicker">科目雷达</div><h2>主线投入<br><em>不只看总时长</em></h2><p class="lead">条形保留原看板的分科统计，雷达区把主要科目放到同一张“作战桌”上，便于看重心是否过度集中。</p><div class="panel" style="margin-top:28px">{subject_rows}</div></div>
    <div class="dial">
      <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
      {radar_points(subjects, max_subject)}
    </div>
  </div>
</section>
<section class="slide">
  <div class="chrome"><span>LATEST ACTIONS</span><span>04 / 05</span></div>
  <div class="split">
    <div><div class="kicker">{esc(latest.get("date", "LATEST"))}</div><h2>最近一次记录<br><em>{esc(latest.get("mood") or "状态未说明")}</em></h2><p class="lead">{esc(latest.get("focus") or "暂无最新主线")}</p><ul class="latest-list">{latest_subjects}</ul></div>
    <div><div class="kicker">下一步</div><h3>可执行清单</h3><ul class="task-list">{action_items}</ul><div class="kicker" style="margin-top:34px">提醒</div><ul class="alert-list">{issues or alert_items or "<li>暂无需要额外提醒的科目。</li>"}</ul></div>
  </div>
</section>
<section class="slide">
  <div class="chrome"><span>ROUTE LOG</span><span>05 / 05</span></div>
  <div class="split">
    <div><div class="kicker">当前推进</div><h2>章节与科目<br><em>落到路线节点</em></h2><div class="panel" style="margin-top:26px">{progress_html}</div></div>
    <div><div class="kicker">路线节点</div><h3>最近记录与节点</h3><div style="margin-top:22px">{timeline}</div><div class="kicker" style="margin-top:32px">RECENT LOGS</div>{log_rows}</div>
  </div>
</section>
</main></div>
<div class="deck-controls"><button id="prev">‹</button><span class="counter" id="counter">1 / 5</span><button id="next">›</button></div>
<script type="application/json" id="dashboard-data">{html_json(data)}</script>
<script>{controller_js()}</script>
</body>
</html>"""


def render_capsule_dashboard(data: dict) -> str:
    """Render a Capsule-styled landscape deck with original dashboard sections."""
    s = data["summary"]
    recent = last_n_daily(data)
    subjects = top_subjects(data, count=9)
    latest = data.get("latest_log") or {}
    recent_summary = data.get("recent") or {}
    archive = data.get("archive") or {}
    months = archive.get("months") or []
    archive_total = s.get("archive_total_minutes") or s["total_minutes"]
    archive_exam = s.get("archive_exam_minutes")
    archive_other = s.get("archive_other_minutes")
    archive_days = sum(m.get("days", 0) for m in months) or s["studied_days"]
    archive_avg = round(archive_total / archive_days) if archive_days else s["avg_minutes"]
    archive_range = (
        f'{months[0]["month"]} 至 {months[-1]["month"]}'
        if months else f'{s["first_date"]} 至 {s["last_date"]}'
    )
    archive_lead_parts = [f"累计 {fmt_minutes(archive_total)}"]
    if archive_exam is not None:
        archive_lead_parts.append(f"考研相关 {fmt_minutes(archive_exam)}")
    if archive_other is not None:
        archive_lead_parts.append(f"课内/其他 {fmt_minutes(archive_other)}")
    archive_lead = "，其中".join([archive_lead_parts[0], "，".join(archive_lead_parts[1:])]) if len(archive_lead_parts) > 1 else archive_lead_parts[0]
    archive_exam_subjects = archive.get("exam_subjects") or [
        {"name": name, "minutes": minutes}
        for name, minutes in subjects
        if name != "其他"
    ]
    capsule_data = dict(data)
    capsule_data["subject_colors"] = CAPSULE_SUBJECT_COLORS

    max_day = max((d["total"] or 0 for d in recent), default=1)
    max_subject = max((m for _, m in subjects), default=1)
    max_month = max((m.get("total_minutes", 0) for m in months), default=1)
    max_exam_subject = max((item.get("minutes", 0) for item in archive_exam_subjects), default=1)
    color_vars = {
        "#E85D4E": "coral",
        "#C4D94E": "lime",
        "#C5B5E0": "lavender",
        "#8BB4F7": "sky",
        "#A06CE8": "violet",
        "#F2D160": "yellow",
        "#F5B895": "peach",
        "#A8E6CF": "mint",
        "#FFFFFF": "white",
    }

    metrics = [
        ("累计学习时长", fmt_minutes(archive_total), "coral"),
        ("学习日日均", fmt_minutes(archive_avg), "lime"),
        ("有效学习日", f"{archive_days}天", "sky"),
        ("距初试首日", f'{s.get("days_to_exam", 0)}天', "peach"),
        ("近 7 天投入", fmt_minutes(recent_summary.get("total_minutes", 0)), "violet"),
    ]
    metric_html = "\n".join(
        f'<div class="metric-pill"><b class="{color}">{esc(value)}</b><span>{esc(label)}</span></div>'
        for label, value, color in metrics
    )

    latest_subjects = "\n".join(
        f'<div class="latest-pill" style="--fill:{capsule_color(item["name"])}">'
        f'<b>{esc(display_subject(item["name"]))}</b><span>{esc(item.get("detail") or item.get("result") or "未说明")}</span>'
        f'<em>{fmt_minutes(item.get("time_min"))}</em></div>'
        for item in (latest.get("subjects") or [])[:7]
    )
    if not latest_subjects:
        latest_subjects = '<div class="empty-pill">暂无可展示的分科记录。</div>'

    trend_bars = []
    for day in recent:
        height = 12 if day.get("total") is None else max(4, pct(day.get("total") or 0, max_day))
        segments = []
        for subject, minutes in (day.get("subjects") or {}).items():
            seg_height = (minutes / day["total"] * 100) if day.get("total") else 0
            segments.append(
                f'<i title="{esc(display_subject(subject))} {fmt_minutes(minutes)}" '
                f'style="height:{seg_height:.1f}%;background:{capsule_color(subject)}"></i>'
            )
        trend_bars.append(
            f'<div class="stack-col"><span>{fmt_minutes(day.get("total"))}</span>'
            f'<div class="stack-track" style="height:{height:.1f}%">{"".join(segments)}</div>'
            f'<em>{esc(day["date"][5:])}</em></div>'
    )
    trend_html = "\n".join(trend_bars) or '<div class="empty-pill">暂无近 14 条记录。</div>'

    def month_subject_summary(month: dict) -> str:
        subjects = month.get("subjects") or []
        if not subjects:
            subjects = [
                {"name": "考研相关", "minutes": month.get("exam_minutes")},
                {"name": "其它", "minutes": month.get("other_minutes")},
            ]
        return " · ".join(
            f'{esc(display_subject(item["name"]))} {fmt_minutes(item.get("minutes"))}'
            for item in subjects[:5]
            if item.get("minutes")
        )

    month_cards = "\n".join(
        f'<div class="month-pill"><div><b>{esc(m["month"])}</b><span>{m["days"]} 天</span></div>'
        f'<strong>{fmt_minutes(m["total_minutes"])}</strong>'
        f'<div class="capsule-track"><i style="width:{pct(m["total_minutes"], max_month):.1f}%"></i></div>'
        f'<p>{month_subject_summary(m)}</p></div>'
        for m in months
    ) or '<div class="empty-pill">暂无月度概览。</div>'

    legend_html = "\n".join(
        f'<span class="legend-pill" style="--fill:{capsule_color(name)}">{esc(display_subject(name))} · {fmt_minutes(minutes)}</span>'
        for name, minutes in subjects
    )

    subject_rows = "\n".join(
        f'<div class="subject-pill" style="--fill:{capsule_color(name)}"><b>{esc(display_subject(name))}</b>'
        f'<div class="capsule-track"><i style="width:{pct(minutes, max_subject):.1f}%"></i></div>'
        f'<span>{fmt_minutes(minutes)}</span></div>'
        for name, minutes in subjects
    ) or '<div class="empty-pill">暂无可统计时长。</div>'

    archive_exam_rows = "\n".join(
        f'<div class="subject-pill" aria-label="{esc(display_subject(item["name"]))} · {fmt_minutes(item["minutes"])}" '
        f'style="--fill:{capsule_color(item["name"])}"><b>{esc(display_subject(item["name"]))}</b>'
        f'<div class="capsule-track"><i style="width:{pct(item["minutes"], max_exam_subject):.1f}%"></i></div>'
        f'<span>{fmt_minutes(item["minutes"])}</span></div>'
        for item in archive_exam_subjects
    ) or '<div class="empty-pill">暂无考研科目累计。</div>'

    actions = list((latest.get("next_actions") or [])[:5])
    if not actions:
        actions = ["继续记录明日学习主线、各科用时和需要补的尾巴。"]
    action_items = "\n".join(f'<div class="action-pill">{esc(item)}</div>' for item in actions)
    issue_items = "\n".join(
        f'<div class="action-pill muted">问题：{esc(item)}</div>'
        for item in (latest.get("issues") or [])[:3]
    )
    if not issue_items:
        issue_items = "\n".join(
            f'<div class="action-pill muted">{esc(display_subject(item["subject"]))}：{esc(item["message"])}'
            f'{(" · 上次 " + esc(item["last_seen"])) if item.get("last_seen") else ""}</div>'
            for item in (data.get("alerts") or [])[:3]
        )

    progress_rows = []
    for name, minutes in subjects:
        latest_chapter = (data.get("latest_chapter") or {}).get(name) or {}
        done = (data.get("subject_chapters_done") or {}).get(name, 0)
        chapter = latest_chapter.get("chapter") or "尚未记录章节进度"
        status = latest_chapter.get("status") or ""
        progress_rows.append(
            f'<div class="progress-pill" style="--fill:{capsule_color(name)}"><b>{esc(display_subject(name))}</b>'
            f'<span>{esc(chapter)}{(" · " + esc(status)) if status else ""}</span>'
            f'<em>{done} 章完结 · {fmt_minutes(minutes)}</em>'
            f'<div class="mini-track"><i style="width:{pct(minutes, max_subject):.1f}%"></i></div></div>'
        )
    progress_html = "\n".join(progress_rows) or '<div class="empty-pill">暂无章节进度。</div>'

    log_rows = "\n".join(
        f'<div class="log-pill"><b>{esc(day["date"])}</b>'
        f'<span>{esc(day.get("focus") or day.get("mood") or "未说明")}</span>'
        f'<em>{fmt_minutes(day.get("total"))}</em></div>'
        for day in reversed((data.get("daily") or [])[-6:])
    ) or '<div class="empty-pill">暂无日志。</div>'

    timeline = "\n".join(
        f'<div class="node-pill"><b>{esc(event["date"])}</b>'
        f'<span>{esc("；".join([m.get("chapter", "") for m in event.get("milestones", [])] + event.get("tags", [])) or event.get("mood") or "记录节点")}</span></div>'
        for event in reversed((data.get("timeline_events") or [])[-7:])
    ) or '<div class="empty-pill">暂无节点事件。</div>'

    subject_color_json = json.dumps(CAPSULE_SUBJECT_COLORS, ensure_ascii=False)
    color_swatches = "\n".join(
        f'<span style="--fill:{color}">{esc(display_subject(name))}</span>'
        for name, color in CAPSULE_SUBJECT_COLORS.items()
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="screen-orientation" content="landscape">
<title>11408 Capsule Dashboard Horizontal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&family=ZCOOL+XiaoWei&display=swap" rel="stylesheet">
<style>
@font-face {{
  font-family:"Anthropic Serif";
  src:url("https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6997199fab1923a705f0042d_AnthropicSerif-Roman-Web.woff2") format("woff2");
  font-weight:300 800;
  font-style:normal;
  font-display:swap;
}}
@font-face {{
  font-family:"Anthropic Serif";
  src:url("https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/699719a0cb5e870a441e0b92_AnthropicSerif-Italic-Web.woff2") format("woff2");
  font-weight:300 800;
  font-style:italic;
  font-display:swap;
}}
:root {{
  --cream:#F5F5F0; --ink:#1A1A1A; --outline:#1E1E1E; --white:#FFFFFF;
  --coral:#E85D4E; --lime:#C4D94E; --lavender:#C5B5E0; --sky:#8BB4F7;
  --violet:#A06CE8; --yellow:#F2D160; --peach:#F5B895; --mint:#A8E6CF;
  --shadow:rgba(26,26,26,.08); --display:"Anthropic Serif","ZCOOL XiaoWei",Georgia,serif;
  --body:"Space Grotesk","ZCOOL XiaoWei",sans-serif;
}}
* {{ box-sizing:border-box; }}
html,body {{ width:100%; height:100%; margin:0; overflow:hidden; background:#ecece5; }}
.deck-viewport {{ position:fixed; inset:0; overflow:hidden; background:#ecece5; }}
.deck-stage {{ position:absolute; left:0; top:0; width: 1920px; height: 1080px; overflow:hidden; transform-origin:0 0; background:var(--cream); }}
.slide {{ position:absolute; inset:0; width: 1920px; height: 1080px; overflow:hidden; display:block; visibility:hidden; opacity:0; pointer-events:none; padding:58px 78px 70px; color:var(--ink); font-family:var(--body); background:
  radial-gradient(ellipse at 10% 12%, rgba(232,93,78,.12), transparent 34%),
  radial-gradient(ellipse at 88% 18%, rgba(139,180,247,.13), transparent 34%),
  radial-gradient(ellipse at 76% 96%, rgba(196,217,78,.12), transparent 36%),
  var(--cream); }}
.slide.active,.slide.visible {{ visibility:visible; opacity:1; pointer-events:auto; z-index:1; }}
.grain {{ position:fixed; inset:0; pointer-events:none; opacity:.04; mix-blend-mode:multiply; z-index:3000; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='.6'/%3E%3C/svg%3E"); }}
.chrome {{ display:flex; justify-content:space-between; align-items:center; height:42px; font-size:16px; letter-spacing:.08em; color:rgba(26,26,26,.62); }}
.tag,.mini-tag,.pill-card,.metric-pill,.latest-pill,.subject-pill,.action-pill,.progress-pill,.log-pill,.node-pill,.legend-pill,.month-pill,.empty-pill,.deck-controls button,.counter {{ border:2px solid var(--outline); box-shadow:4px 4px 0 var(--shadow); }}
.tag,.mini-tag,.legend-pill,.empty-pill,.deck-controls button,.counter {{ border-radius:9999px; }}
.tag {{ display:inline-flex; align-items:center; justify-content:center; padding:12px 28px; background:var(--yellow); color:var(--ink); font-weight:800; letter-spacing:.08em; font-size:14px; }}
.mini-tag {{ display:inline-flex; padding:8px 18px; background:var(--lavender); font-size:12px; font-weight:800; color:rgba(26,26,26,.72); }}
.pill-card {{ background:var(--white); border-radius:32px; padding:26px; box-shadow:8px 8px 0 var(--shadow); }}
h1,h2,h3 {{ margin:0; font-family:var(--display); font-weight:800; letter-spacing:0; color:var(--ink); }}
h1 {{ font-size:94px; line-height:.94; }}
h2 {{ font-size:58px; line-height:.98; }}
h3 {{ font-size:38px; line-height:1; }}
.lead {{ margin:18px 0 0; font-size:22px; line-height:1.58; color:rgba(26,26,26,.66); }}
.home-grid {{ display:grid; grid-template-columns:1.18fr .82fr; gap:38px; padding-top:36px; }}
.metric-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:16px; margin-top:28px; }}
.metric-pill {{ background:var(--white); border-radius:32px; padding:24px 22px; min-height:150px; }}
.metric-pill b {{ display:block; font-family:var(--display); font-size:44px; line-height:1; margin-bottom:18px; white-space:nowrap; }}
.metric-pill span,.latest-pill em,.subject-pill span,.progress-pill em,.log-pill em {{ color:rgba(26,26,26,.62); font-weight:800; }}
.coral {{ color:var(--coral); }} .lime {{ color:var(--lime); }} .sky {{ color:var(--sky); }} .peach {{ color:var(--peach); }} .violet {{ color:var(--violet); }}
.tag.sky,.tag.lime,.tag.peach,.tag.violet,.tag.lavender,.tag.yellow {{ color:var(--ink); }}
.latest-panel {{ display:grid; grid-template-rows:auto auto 1fr; min-height:520px; align-self:start; }}
.latest-list {{ display:grid; gap:14px; margin-top:22px; align-content:start; }}
.latest-pill {{ display:grid; grid-template-columns:160px 1fr 94px; gap:14px; align-items:center; background:var(--white); border-radius:9999px; padding:14px 20px; }}
.legend-pill::before {{ content:""; width:18px; height:18px; border:2px solid var(--outline); border-radius:50%; background:var(--fill); }}
.latest-pill b {{ display:flex; align-items:center; gap:10px; }}
.latest-pill b::before {{ content:""; width:16px; height:16px; border:2px solid var(--outline); border-radius:50%; background:var(--fill); flex:0 0 auto; }}
.stack-layout {{ display:grid; grid-template-rows:auto 1fr auto; gap:22px; padding-top:28px; }}
.trend-grid {{ height:610px; display:grid; grid-template-columns:repeat(14,1fr); gap:13px; align-items:end; }}
.stack-col {{ height:100%; display:grid; grid-template-rows:32px 1fr 28px; gap:10px; text-align:center; font-size:13px; color:rgba(26,26,26,.62); }}
.stack-track {{ align-self:end; min-height:10px; display:flex; flex-direction:column-reverse; overflow:hidden; background:var(--white); border:2px solid var(--outline); border-radius:9999px; box-shadow:4px 4px 0 var(--shadow); }}
.stack-track i {{ display:block; width:100%; border-top:2px solid rgba(30,30,30,.86); }}
.legend-row {{ display:flex; flex-wrap:wrap; gap:10px; }}
.legend-pill {{ display:inline-flex; align-items:center; gap:8px; background:var(--white); padding:8px 14px; font-size:13px; font-weight:800; }}
.overview-grid {{ display:grid; grid-template-columns:.82fr 1.18fr; gap:34px; padding-top:30px; }}
.overview-grid h2 {{ font-size:50px; }}
.overview-grid .trend-grid {{ height:545px; gap:10px; }}
.overview-grid .legend-row {{ margin-top:4px; }}
.month-grid {{ display:grid; gap:16px; margin-top:22px; }}
.month-pill {{ background:var(--white); border-radius:30px; padding:20px 22px; }}
.month-pill div:first-child {{ display:flex; justify-content:space-between; align-items:center; font-weight:800; color:rgba(26,26,26,.64); }}
.month-pill strong {{ display:block; font-family:var(--display); font-size:38px; line-height:1; margin:13px 0 12px; color:var(--coral); }}
.month-pill p {{ margin:12px 0 0; color:rgba(26,26,26,.62); font-size:14px; font-weight:800; }}
.two-col {{ display:grid; grid-template-columns:.94fr 1.06fr; gap:38px; padding-top:34px; }}
.archive-subject-grid {{ display:grid; grid-template-columns:1fr; gap:20px; margin-top:22px; }}
.archive-subject-grid .subject-list {{ margin-top:0; gap:18px; }}
.archive-subject-grid .subject-pill {{ grid-template-columns:220px minmax(360px,1fr) 110px; padding:20px 24px; }}
.archive-subject-grid .capsule-track {{ height:42px; }}
.subject-list,.action-list,.progress-list,.log-list,.node-list {{ display:grid; gap:13px; margin-top:22px; }}
.subject-pill {{ display:grid; grid-template-columns:190px 1fr 100px; gap:16px; align-items:center; background:var(--white); border-radius:9999px; padding:13px 18px; }}
.capsule-track,.mini-track {{ height:30px; border:2px solid var(--outline); border-radius:9999px; background:var(--cream); overflow:hidden; }}
.capsule-track i,.mini-track i {{ display:block; height:100%; background:var(--fill); border-right:2px solid var(--outline); border-radius:9999px; }}
.action-pill,.log-pill,.node-pill,.progress-pill {{ background:var(--white); border-radius:9999px; padding:15px 22px; }}
.action-pill {{ font-size:21px; line-height:1.38; }}
.muted {{ color:rgba(26,26,26,.62); }}
.progress-pill {{ display:grid; grid-template-columns:180px 1fr 150px; gap:16px; align-items:center; }}
.progress-pill .mini-track {{ grid-column:2 / 4; height:16px; }}
.log-pill {{ display:grid; grid-template-columns:132px 1fr 90px; gap:16px; align-items:center; }}
.node-pill {{ display:grid; grid-template-columns:132px 1fr; gap:16px; align-items:center; }}
.swatches {{ display:flex; flex-wrap:wrap; gap:9px; margin-top:20px; }}
.swatches span {{ display:inline-flex; border:2px solid var(--outline); border-radius:9999px; background:var(--fill); padding:6px 12px; font-size:12px; font-weight:800; }}
.float {{ position:absolute; border:2px solid var(--outline); border-radius:9999px; padding:8px 20px; font-size:12px; font-weight:800; letter-spacing:.08em; }}
.f1 {{ left:86px; top:126px; transform:rotate(-12deg); background:var(--coral); }} .f2 {{ right:132px; top:126px; transform:rotate(10deg); background:var(--lavender); }}
.f3 {{ left:102px; bottom:112px; transform:rotate(8deg); background:var(--mint); }} .f4 {{ right:122px; bottom:118px; transform:rotate(-9deg); background:var(--lime); }}
.empty-pill {{ display:inline-flex; align-items:center; background:var(--white); padding:18px 24px; color:rgba(26,26,26,.62); }}
.rotate-hint {{ position:fixed; inset:0; display:none; align-items:center; justify-content:center; z-index:4000; background:var(--cream); color:var(--ink); font:18px var(--body); text-align:center; padding:30px; }}
@media (orientation:portrait) and (max-width:900px) {{ .rotate-hint {{ display:flex; }} }}
.deck-controls {{ position:fixed; left:50%; bottom:16px; transform:translateX(-50%); z-index:3500; }}
.deck-controls button {{ width:48px; height:34px; background:var(--white); margin:0 5px; font-family:var(--body); font-weight:800; }}
.counter {{ display:inline-flex; align-items:center; height:34px; padding:0 16px; background:var(--yellow); font-family:var(--body); font-weight:800; }}
@media print {{ html,body{{width:1920px;height:auto;overflow:visible;background:#fff}} .deck-viewport{{position:static;overflow:visible;background:#fff}} .deck-stage{{position:static;width:auto;height:auto;transform:none!important;background:none}} .slide{{position:relative;display:block!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;width:1920px;height:1080px;break-after:page;page-break-after:always}} .deck-controls,.rotate-hint{{display:none!important}} }}
@media (prefers-reduced-motion:reduce) {{ *,*::before,*::after{{animation-duration:.01ms!important;transition-duration:.2s!important}} }}
</style>
</head>
<body data-dashboard-variant="capsule-dashboard">
<div class="rotate-hint">请将手机转为横屏查看。<br>这版 Capsule 看板按 16:9 横屏舞台设计。</div>
<div class="deck-viewport"><main class="deck-stage" id="deckStage">
<section class="slide active visible">
  <span class="float f1">FOCUS</span><span class="float f2">RECORD</span><span class="float f3">NEXT</span><span class="float f4">NODE</span>
  <div class="chrome"><span>11408 CAPSULE DASHBOARD</span><span>{esc(archive_range)}</span></div>
  <div class="home-grid">
    <div><div class="tag">Daily Progress</div><h1 style="margin-top:28px">Study<br>Progress</h1><p class="lead">{esc(s.get("current_phase") or "未说明")}。{esc(archive_lead)}。最近主线：{esc(s.get("latest_focus") or "未说明")}。</p><div class="metric-grid">{metric_html}</div><div class="swatches">{color_swatches}</div></div>
    <div class="pill-card latest-panel"><div><div class="mini-tag">最近一天</div><h2 style="margin-top:18px">{esc(latest.get("date") or "暂无记录")}</h2></div><p class="lead">{esc(latest.get("focus") or "暂无最新记录")}</p><div class="latest-list">{latest_subjects}</div></div>
  </div>
</section>
<section class="slide">
  <div class="chrome"><span>MONTHLY AND RECENT TREND</span><span>02 / 05</span></div>
  <div class="overview-grid">
    <div><div class="tag sky">整体节奏</div><h2 style="margin-top:20px">月度概览</h2><div class="month-grid">{month_cards}</div></div>
    <div><div class="tag lime">柱高为总时长，色块为科目构成</div><h2 style="margin-top:20px">近 14 条记录</h2><div class="trend-grid">{trend_html}</div><div class="legend-row">{legend_html}</div></div>
  </div>
</section>
<section class="slide">
  <div class="chrome"><span>SUBJECTS AND ACTIONS</span><span>03 / 05</span></div>
  <div class="two-col">
    <div><div class="tag lime">按学习记录累计</div><h2 style="margin-top:20px">科目投入</h2><div class="archive-subject-grid"><div class="subject-list">{archive_exam_rows}</div></div></div>
    <div><div class="tag peach">来自最新日志</div><h2 style="margin-top:20px">下一步</h2><div class="action-list">{action_items}{issue_items}</div></div>
  </div>
</section>
<section class="slide">
  <div class="chrome"><span>CURRENT PROGRESS</span><span>04 / 05</span></div>
  <div style="padding-top:34px"><div class="tag lavender">条形长度为累计投入占比</div><h2 style="margin-top:20px">当前推进</h2><div class="progress-list">{progress_html}</div></div>
</section>
<section class="slide">
  <div class="chrome"><span>ROUTE LOG</span><span>05 / 05</span></div>
  <div class="two-col">
    <div><div class="tag yellow">保留原始节奏</div><h2 style="margin-top:20px">最近记录</h2><div class="log-list">{log_rows}</div></div>
    <div><div class="tag violet">章节状态与标签</div><h2 style="margin-top:20px">节点</h2><div class="node-list">{timeline}</div></div>
  </div>
</section>
</main></div>
<div class="grain"></div>
<div class="deck-controls"><button id="prev">‹</button><span class="counter" id="counter">1 / 5</span><button id="next">›</button></div>
<script type="application/json" id="dashboard-data">{html_json(capsule_data)}</script>
<script>const SUBJECT_COLORS = {subject_color_json}; const CAPSULE_COLOR_NAMES = {json.dumps(color_vars, ensure_ascii=False)};</script>
<script>{controller_js()}</script>
</body>
</html>"""


def render_capsule(data: dict) -> str:
    s = data["summary"]
    months = data["archive"]["months"]
    recent = last_n_daily(data)
    subjects = top_subjects(data)
    latest = data.get("latest_log") or {}
    exam_minutes, other_minutes = split_exam_subjects(data)
    recent_summary = data.get("recent") or {}

    max_month = max((m["total_minutes"] for m in months), default=1)
    max_day = max((d["total"] or 0 for d in recent), default=1)
    max_subject = max((m for _, m in subjects), default=1)
    accents = ["coral", "lime", "sky", "violet", "yellow", "lavender", "peach", "mint"]

    stat_cards = "\n".join([
        capsule_stat("累计完成", fmt_minutes(s["archive_total_minutes"]), "coral"),
        capsule_stat("考研相关", fmt_minutes(exam_minutes), "lime"),
        capsule_stat("课内/其他", fmt_minutes(other_minutes), "sky"),
        capsule_stat("距初试", f'{s["days_to_exam"]} 天', "violet"),
    ])
    month_cards = "\n".join(
        f'<div class="pill-card month-card"><div class="card-top"><b>{esc(m["month"])}</b><span>{m["days"]} 天</span></div>'
        f'<strong>{fmt_minutes(m["total_minutes"])}</strong><div class="capsule-track">'
        f'<i class="{accents[idx % len(accents)]}" style="width:{pct(m["total_minutes"], max_month):.1f}%"></i></div>'
        f'<p>考研 {fmt_minutes(m["exam_minutes"])} · 课内/其他 {fmt_minutes(m["other_minutes"])}</p></div>'
        for idx, m in enumerate(months)
    )
    trend_bars = "\n".join(
        f'<div class="capsule-bar"><span>{esc(day["date"][5:])}</span>'
        f'<div class="vertical-track"><i class="{accents[idx % len(accents)]}" style="height:{pct(day["total"] or 0, max_day):.1f}%"></i></div>'
        f'<b>{fmt_minutes(day["total"])}</b></div>'
        for idx, day in enumerate(recent)
    )
    subject_rows = "\n".join(
        f'<div class="subject-pill"><b>{esc(name)}</b><div class="capsule-track">'
        f'<i class="{accents[idx % len(accents)]}" style="width:{pct(minutes, max_subject):.1f}%"></i></div>'
        f'<span>{fmt_minutes(minutes)}</span></div>'
        for idx, (name, minutes) in enumerate(subjects)
    )
    orbit = capsule_orbit(subjects, max_subject)
    latest_subjects = "\n".join(
        f'<li><b>{esc(item["name"])}</b><span>{esc(item.get("detail") or item.get("result") or "未说明")}</span>'
        f'<em>{fmt_minutes(item.get("time_min"))}</em></li>'
        for item in (latest.get("subjects") or [])[:5]
    )
    actions = (latest.get("next_actions") or [])[:4] or ["继续记录每日主线、分科用时和需要收尾的问题。"]
    action_items = "\n".join(f"<li>{esc(item)}</li>" for item in actions)
    alerts = "\n".join(
        f'<li><b>{esc(item["subject"])}</b><span>{esc(item["message"])}'
        f'{(" · 上次 " + esc(item["last_seen"])) if item.get("last_seen") else ""}</span></li>'
        for item in (data.get("alerts") or [])[:4]
    )
    progress_rows = []
    for idx, (name, minutes) in enumerate(subjects):
        latest_chapter = (data.get("latest_chapter") or {}).get(name) or {}
        done = (data.get("subject_chapters_done") or {}).get(name, 0)
        chapter = latest_chapter.get("chapter") or "尚未记录章节进度"
        status = latest_chapter.get("status") or ""
        progress_rows.append(
            f'<div class="route-pill {accents[idx % len(accents)]}"><b>{esc(name)}</b>'
            f'<span>{esc(chapter)}{" · " + esc(status) if status else ""}</span>'
            f'<em>{done} 章完结 · {fmt_minutes(minutes)}</em></div>'
        )
    progress_html = "\n".join(progress_rows)
    timeline = "\n".join(
        f'<div class="node-pill"><b>{esc(event["date"])}</b><span>{esc("；".join([m.get("chapter", "") for m in event.get("milestones", [])] + event.get("tags", [])) or event.get("mood") or "记录节点")}</span></div>'
        for event in reversed((data.get("timeline_events") or [])[-6:])
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="screen-orientation" content="landscape">
<title>11408 Capsule Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&family=Space+Grotesk:wght@300..700&family=ZCOOL+XiaoWei&display=swap" rel="stylesheet">
<style>
:root {{
  --cream:#F5F5F0; --ink:#1A1A1A; --outline:#1E1E1E; --white:#FFFFFF;
  --coral:#E85D4E; --lime:#C4D94E; --lavender:#C5B5E0; --sky:#8BB4F7;
  --violet:#A06CE8; --yellow:#F2D160; --peach:#F5B895; --mint:#A8E6CF;
  --shadow:rgba(26,26,26,.08); --display:"Bodoni Moda","ZCOOL XiaoWei",serif;
  --body:"Space Grotesk","ZCOOL XiaoWei",sans-serif;
}}
* {{ box-sizing:border-box; }}
html,body {{ width:100%; height:100%; margin:0; overflow:hidden; background:#ecece5; }}
.deck-viewport {{ position:fixed; inset:0; overflow:hidden; background:#ecece5; }}
.deck-stage {{ position:absolute; left:0; top:0; width: 1920px; height: 1080px; overflow:hidden; transform-origin:0 0; background:var(--cream); }}
.slide {{ position:absolute; inset:0; width: 1920px; height: 1080px; overflow:hidden; display:block; visibility:hidden; opacity:0; pointer-events:none; padding:72px 104px; color:var(--ink); font-family:var(--body); background:
  radial-gradient(ellipse at 8% 10%, rgba(232,93,78,.13), transparent 34%),
  radial-gradient(ellipse at 90% 18%, rgba(139,180,247,.14), transparent 34%),
  radial-gradient(ellipse at 70% 92%, rgba(196,217,78,.12), transparent 36%),
  var(--cream); }}
.slide.active,.slide.visible {{ visibility:visible; opacity:1; pointer-events:auto; z-index:1; }}
.grain {{ position:fixed; inset:0; pointer-events:none; opacity:.04; mix-blend-mode:multiply; z-index:3000; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='.6'/%3E%3C/svg%3E"); }}
.chrome {{ display:flex; justify-content:space-between; align-items:center; font-size:16px; letter-spacing:.08em; color:rgba(26,26,26,.62); }}
.headline {{ font-family:var(--display); font-size:106px; line-height:.92; font-weight:800; letter-spacing:0; margin:0; }}
.headline em {{ font-style:italic; }}
.section-title {{ font-family:var(--display); font-size:72px; line-height:.98; font-weight:800; letter-spacing:0; margin:0; }}
.lead {{ font-size:25px; line-height:1.65; color:rgba(26,26,26,.66); margin:24px 0 0; max-width:780px; }}
.pill,.tag,.deck-controls button,.counter {{ border-radius:9999px; border:2px solid var(--outline); }}
.tag {{ display:inline-flex; align-items:center; justify-content:center; padding:12px 28px; background:var(--yellow); font-weight:700; letter-spacing:.08em; font-size:14px; box-shadow:4px 4px 0 var(--shadow); }}
.pill-card {{ background:var(--white); border:2px solid var(--outline); border-radius:32px; box-shadow:8px 8px 0 var(--shadow); padding:30px; }}
.cover {{ display:grid; grid-template-columns:.9fr 1.1fr; gap:62px; padding-top:60px; }}
.float {{ position:absolute; border-radius:9999px; border:2px solid var(--outline); padding:9px 22px; font-size:12px; font-weight:700; letter-spacing:.08em; }}
.f1 {{ left:122px; top:142px; transform:rotate(-13deg); background:var(--coral); }} .f2 {{ right:160px; top:134px; transform:rotate(12deg); background:var(--lavender); }}
.f3 {{ left:118px; bottom:160px; transform:rotate(9deg); background:var(--violet); }} .f4 {{ right:176px; bottom:162px; transform:rotate(-10deg); background:var(--lime); }}
.f5 {{ left:760px; top:154px; transform:rotate(4deg); background:var(--peach); }} .f6 {{ right:96px; top:498px; transform:rotate(17deg); background:var(--white); }}
.stat-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
.stat-pill {{ min-height:178px; border-radius:32px; }}
.stat-pill b {{ display:block; font-family:var(--display); font-size:58px; line-height:1; margin-bottom:14px; }}
.stat-pill span,.mini {{ font-size:14px; letter-spacing:.08em; color:rgba(26,26,26,.62); font-weight:700; }}
.accent-line {{ width:70px; height:6px; border-radius:9999px; margin-top:20px; background:var(--coral); }}
.coral {{ background:var(--coral); }} .lime {{ background:var(--lime); }} .sky {{ background:var(--sky); }} .violet {{ background:var(--violet); }} .yellow {{ background:var(--yellow); }} .lavender {{ background:var(--lavender); }} .peach {{ background:var(--peach); }} .mint {{ background:var(--mint); }}
.split {{ display:grid; grid-template-columns:.92fr 1.08fr; gap:52px; padding-top:46px; }}
.month-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; margin-top:30px; }}
.card-top {{ display:flex; justify-content:space-between; align-items:center; font-weight:700; }}
.month-card strong {{ display:block; font-family:var(--display); font-size:52px; line-height:1; margin:18px 0; }}
.month-card p {{ margin:16px 0 0; color:rgba(26,26,26,.64); font-size:18px; }}
.capsule-track {{ height:36px; border:2px solid var(--outline); border-radius:9999px; background:var(--cream); overflow:hidden; }}
.capsule-track i {{ display:block; height:100%; border-radius:9999px; border-right:2px solid var(--outline); }}
.trend-grid {{ height:526px; display:grid; grid-template-columns:repeat(14,1fr); gap:14px; align-items:end; }}
.capsule-bar {{ display:grid; grid-template-rows:28px 1fr 28px; gap:10px; height:100%; text-align:center; font-size:13px; color:rgba(26,26,26,.62); }}
.vertical-track {{ height:100%; border:2px solid var(--outline); border-radius:9999px; background:var(--white); overflow:hidden; display:flex; align-items:flex-end; box-shadow:4px 4px 0 var(--shadow); }}
.vertical-track i {{ display:block; width:100%; border-radius:9999px 9999px 0 0; border-top:2px solid var(--outline); }}
.subject-wrap {{ display:grid; gap:17px; margin-top:30px; }}
.subject-pill {{ display:grid; grid-template-columns:210px 1fr 110px; gap:18px; align-items:center; border:2px solid var(--outline); border-radius:9999px; background:var(--white); padding:12px 18px; box-shadow:4px 4px 0 var(--shadow); }}
.subject-pill b,.route-pill b,.node-pill b,.latest-list b,.task-list b {{ font-weight:800; }}
.orbit {{ position:relative; height:570px; }}
.orbit-center {{ position:absolute; left:50%; top:50%; width:178px; height:178px; transform:translate(-50%,-50%); border-radius:50%; border:2px solid var(--outline); background:var(--lime); display:grid; place-items:center; font-family:var(--display); font-size:54px; font-weight:800; box-shadow:6px 6px 0 var(--shadow); }}
.orbit-pill {{ position:absolute; min-width:160px; border:2px solid var(--outline); border-radius:9999px; padding:16px 22px; box-shadow:6px 6px 0 var(--shadow); font-size:15px; }}
.latest-list,.task-list {{ margin:28px 0 0; padding:0; list-style:none; display:grid; gap:16px; }}
.latest-list li,.task-list li,.node-pill,.route-pill {{ border:2px solid var(--outline); border-radius:9999px; background:var(--white); box-shadow:4px 4px 0 var(--shadow); }}
.latest-list li {{ display:grid; grid-template-columns:142px 1fr 94px; gap:18px; align-items:center; padding:16px 22px; }}
.latest-list span,.task-list li span,.route-pill span,.node-pill span {{ color:rgba(26,26,26,.66); }}
.latest-list em,.route-pill em {{ font-style:normal; font-weight:800; }}
.task-list li {{ padding:18px 26px; font-size:22px; }}
.route-list,.node-list {{ display:grid; gap:16px; margin-top:28px; }}
.route-pill {{ display:grid; grid-template-columns:190px 1fr 150px; gap:18px; align-items:center; padding:16px 22px; }}
.node-pill {{ display:grid; grid-template-columns:148px 1fr; gap:18px; align-items:center; padding:16px 22px; }}
.rotate-hint {{ position:fixed; inset:0; display:none; align-items:center; justify-content:center; z-index:4000; background:var(--cream); color:var(--ink); font:18px var(--body); text-align:center; padding:30px; }}
@media (orientation:portrait) and (max-width:900px) {{ .rotate-hint {{ display:flex; }} }}
.deck-controls {{ position:fixed; left:50%; bottom:16px; transform:translateX(-50%); z-index:3500; }}
.deck-controls button {{ width:48px; height:34px; background:var(--white); margin:0 5px; font-family:var(--body); font-weight:800; }}
.counter {{ display:inline-flex; align-items:center; height:34px; padding:0 16px; background:var(--yellow); font-family:var(--body); font-weight:800; }}
@media print {{ html,body{{width:1920px;height:auto;overflow:visible;background:#fff}} .deck-viewport{{position:static;overflow:visible;background:#fff}} .deck-stage{{position:static;width:auto;height:auto;transform:none!important;background:none}} .slide{{position:relative;display:block!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;width:1920px;height:1080px;break-after:page;page-break-after:always}} .deck-controls,.rotate-hint{{display:none!important}} }}
@media (prefers-reduced-motion:reduce) {{ *,*::before,*::after{{animation-duration:.01ms!important;transition-duration:.2s!important}} }}
</style>
</head>
<body data-dashboard-variant="capsule">
<div class="rotate-hint">请将手机转为横屏查看。<br>Capsule 版为 16:9 宽屏胶囊看板。</div>
<div class="deck-viewport"><main class="deck-stage" id="deckStage">
<section class="slide active visible">
  {floating_pills()}
  <div class="chrome"><span>11408 STUDY CAPSULE</span><span>{esc(s["first_date"])} / {esc(s["last_date"])}</span></div>
  <div class="cover"><div><div class="tag">PROGRESS SIGNALS</div><h1 class="headline" style="margin-top:34px">Study<br><em>Capsule</em></h1><p class="lead">用更轻的胶囊系统看备考：总投入、近 7 天强度、月度负荷、科目重心和下一步都放进可扫读的模块。</p></div><div class="stat-grid">{stat_cards}</div></div>
</section>
<section class="slide">
  <div class="chrome"><span>LOAD MAP</span><span>02 / 05</span></div>
  <div class="split"><div><div class="tag lavender">MONTHLY ROUTE</div><h2 class="section-title" style="margin-top:28px">月度胶囊<br>看整体路线</h2><p class="lead">完整补录口径保留阶段节奏，近 14 条记录显示最近实际波动。</p><div class="month-grid">{month_cards}</div></div><div class="pill-card"><h3 class="section-title" style="font-size:46px">近 14 条记录</h3><div class="trend-grid" style="margin-top:34px">{trend_bars}</div></div></div>
</section>
<section class="slide">
  <div class="chrome"><span>SUBJECT CAPSULES</span><span>03 / 05</span></div>
  <div class="split"><div><div class="tag sky">SUBJECT LANES</div><h2 class="section-title" style="margin-top:28px">科目胶囊<br>看重心偏移</h2><p class="lead">条形胶囊保留分科统计，右侧轨道把主要科目的投入距离放到同一张图里。</p><div class="subject-wrap">{subject_rows}</div></div><div class="pill-card orbit"><div class="orbit-center">89</div>{orbit}</div></div>
</section>
<section class="slide">
  <div class="chrome"><span>NEXT ACTIONS</span><span>04 / 05</span></div>
  <div class="split"><div><div class="tag peach">{esc(latest.get("date", "LATEST"))}</div><h2 class="section-title" style="margin-top:28px">最近一次记录<br>{esc(latest.get("mood") or "状态未说明")}</h2><p class="lead">{esc(latest.get("focus") or "暂无最新主线")}</p><ul class="latest-list">{latest_subjects}</ul></div><div><div class="tag lime">NEXT</div><h3 class="section-title" style="font-size:48px;margin-top:28px">下一步</h3><ul class="task-list">{action_items}</ul><div class="tag coral" style="margin-top:36px">REMINDERS</div><ul class="task-list">{alerts or "<li>暂无需要额外提醒的科目。</li>"}</ul></div></div>
</section>
<section class="slide">
  <div class="chrome"><span>ROUTE LOG</span><span>05 / 05</span></div>
  <div class="split"><div><div class="tag yellow">CURRENT ROUTE</div><h2 class="section-title" style="margin-top:28px">章节与科目<br>落到路线节点</h2><div class="route-list">{progress_html}</div></div><div><div class="tag violet">TIMELINE</div><h3 class="section-title" style="font-size:48px;margin-top:28px">路线节点</h3><div class="node-list">{timeline}</div></div></div>
</section>
</main></div>
<div class="grain"></div>
<div class="deck-controls"><button id="prev">‹</button><span class="counter" id="counter">1 / 5</span><button id="next">›</button></div>
<script type="application/json" id="dashboard-data">{html_json(data)}</script>
<script>{controller_js()}</script>
</body>
</html>"""


def capsule_stat(label: str, value: str, color: str) -> str:
    return (
        f'<div class="pill-card stat-pill"><b>{esc(value)}</b><span>{esc(label)}</span>'
        f'<div class="accent-line {color}"></div></div>'
    )


def floating_pills() -> str:
    return (
        '<span class="float f1">FOCUS</span><span class="float f2">ROUTE</span>'
        '<span class="float f3">NEXT</span><span class="float f4">REVIEW</span>'
        '<span class="float f5">EXAM</span><span class="float f6">LOG</span>'
    )


def capsule_orbit(subjects: list[tuple[str, int]], maximum: int) -> str:
    if not subjects:
        return ""
    positions = [
        ("left:45px;top:58px;transform:rotate(-10deg)", "coral"),
        ("right:42px;top:72px;transform:rotate(12deg)", "sky"),
        ("right:78px;bottom:92px;transform:rotate(-8deg)", "violet"),
        ("left:64px;bottom:88px;transform:rotate(10deg)", "yellow"),
        ("left:252px;top:32px;transform:rotate(4deg)", "peach"),
        ("left:286px;bottom:34px;transform:rotate(-5deg)", "mint"),
    ]
    pills = []
    for idx, (name, minutes) in enumerate(subjects[:6]):
        style, color = positions[idx]
        pills.append(
            f'<div class="orbit-pill {color}" style="{style}"><b>{esc(name)}</b><br>{fmt_minutes(minutes)}</div>'
        )
    return "\n".join(pills)


def radar_points(subjects: list[tuple[str, int]], maximum: int) -> str:
    if not subjects:
        return ""
    points = []
    center_x, center_y = 50, 50
    for idx, (name, minutes) in enumerate(subjects[:8]):
        angle = -90 + idx * (360 / min(len(subjects), 8))
        radius = 13 + pct(minutes, maximum) * 0.32
        import math

        x = center_x + math.cos(math.radians(angle)) * radius
        y = center_y + math.sin(math.radians(angle)) * radius
        lx = center_x + math.cos(math.radians(angle)) * min(46, radius + 11)
        ly = center_y + math.sin(math.radians(angle)) * min(46, radius + 11)
        points.append(f'<div class="dial-point" style="left:{x:.1f}%;top:{y:.1f}%"></div>')
        points.append(
            f'<div class="dial-label" style="left:{lx:.1f}%;top:{ly:.1f}%">{esc(name)} · {fmt_minutes(minutes)}</div>'
        )
    return "\n".join(points)


def controller_js() -> str:
    return """
class Deck {
  constructor() {
    this.stage = document.getElementById('deckStage');
    this.slides = [...document.querySelectorAll('.slide')];
    this.counter = document.getElementById('counter');
    const requested = Number(new URLSearchParams(window.location.search).get('slide') || 0);
    this.index = Number.isFinite(requested) ? requested : 0;
    this.scale();
    this.bind();
    this.show(this.index);
  }
  scale() {
    const factor = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    const x = (window.innerWidth - 1920 * factor) / 2;
    const y = (window.innerHeight - 1080 * factor) / 2;
    this.stage.style.transform = `translate(${x}px, ${y}px) scale(${factor})`;
  }
  show(next) {
    this.index = Math.max(0, Math.min(next, this.slides.length - 1));
    this.slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === this.index);
      slide.classList.toggle('visible', i === this.index);
    });
    this.counter.textContent = `${this.index + 1} / ${this.slides.length}`;
  }
  bind() {
    window.addEventListener('resize', () => this.scale());
    document.getElementById('prev').addEventListener('click', () => this.show(this.index - 1));
    document.getElementById('next').addEventListener('click', () => this.show(this.index + 1));
    document.addEventListener('keydown', (e) => {
      if (['ArrowRight', ' ', 'PageDown'].includes(e.key)) this.show(this.index + 1);
      if (['ArrowLeft', 'PageUp'].includes(e.key)) this.show(this.index - 1);
    });
    let startX = null;
    document.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
    document.addEventListener('touchend', (e) => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 42) this.show(this.index + (dx < 0 ? 1 : -1));
      startX = null;
    }, { passive: true });
  }
}
new Deck();
"""


def build_variants(out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    data = enriched_data()
    outputs = [
        (out_dir / DASHBOARD_OUT, render_capsule_dashboard(data)),
    ]
    for path, html in outputs:
        path.write_text(html, encoding="utf-8")

    if out_dir == OUT_DIR:
        for filename in STALE_DASHBOARD_FILES:
            stale_path = out_dir / filename
            if stale_path.exists():
                stale_path.unlink()

    return [path for path, _ in outputs]


def main() -> int:
    paths = build_variants()
    for path in paths:
        print(f"[OK] {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
