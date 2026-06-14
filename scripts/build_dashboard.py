#!/usr/bin/env python3
"""Build a self-contained HTML study dashboard from daily-log frontmatter.

Scans StudyProgress/DailyLogs/**/*.md, reads the YAML frontmatter block at the
top of each log, aggregates the structured data, and renders it into a single
zero-dependency HTML file (StudyProgress/dashboard.html) with all data, CSS and
JS inlined. Double-click the HTML to open it in any browser — no server needed.

The visual layout is a responsive single-page dashboard optimized for daily
review: open it directly in a browser, no local server required.

Usage:
    python scripts/build_dashboard.py
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "StudyProgress" / "DailyLogs"
OUT_PATH = ROOT / "StudyProgress" / "dashboard.html"

# Subject -> display group / color. Keeps the dashboard palette stable across
# trend bars, legends, totals and progress lanes.
SUBJECT_COLORS = {
    "数学-高数": "#c77966",
    "数学-线代": "#d7a05f",
    "数学-概率": "#b7a66b",
    "专业课-数据结构": "#76a08f",
    "专业课-组成原理": "#9f8665",
    "专业课-操作系统": "#8f93b8",
    "专业课-计算机网络": "#79a8b3",
    "英语": "#d98872",
    "政治": "#b7849f",
}
DEFAULT_COLOR = "#868e96"
DEFERRED_SUBJECTS = {"政治"}
WATCH_SUBJECTS = {"英语"}
GROUP_ORDER = ["数学", "专业课", "英语", "政治", "其他"]
GROUP_COLORS = {
    "数学": "#c88454",
    "专业课": "#9a8f5f",
    "英语": "#d77855",
    "政治": "#b77b8f",
    "其他": "#6B7280",
}

# 初试首日（思想政治理论），用于封面倒计时。11408 初试固定在 12 月，2026 年为 12/20-21。
EXAM_DATE = date(2026, 12, 20)
# 趋势屏只展示最近 N 天，避免长期记录后柱子被压成细线。
TREND_WINDOW_DAYS = 21


def as_minutes(value) -> int | None:
    """Return an integer minute value when explicitly provided."""
    if isinstance(value, (int, float)):
        return int(value)
    return None


def subject_group(subject: str) -> str:
    """Map detailed subject names into dashboard-level lanes."""
    if subject.startswith("数学-"):
        return "数学"
    if subject.startswith("专业课-"):
        return "专业课"
    if subject in {"英语", "政治"}:
        return subject
    return "其他"


def clean_list(value) -> list[str]:
    """Return a list of non-empty strings from optional markdown metadata."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def latest_nonempty(logs: list[dict], key: str) -> str:
    """Return the newest non-empty metadata value for a given key."""
    for log in reversed(logs):
        value = log.get(key)
        if value:
            return str(value)
    return "未说明"


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
    group_totals: dict[str, int] = {}
    group_days: dict[str, set[str]] = {}
    progress_rows: list[dict] = []
    timeline: list[dict] = []
    total_minutes = 0
    studied_days = 0
    latest_log: dict | None = None

    for log in logs:
        d = str(log.get("date"))
        subjects = log.get("subjects") or []
        per_subject = {}
        subject_details = []
        day_minutes = 0
        has_known_subject_time = False
        for s in subjects:
            if not isinstance(s, dict):
                continue
            name = s.get("name") or "未分类"
            t = as_minutes(s.get("time_min"))
            detail = str(s.get("detail") or "").strip()
            subject_details.append({
                "name": name,
                "group": subject_group(name),
                "time_min": t,
                "detail": detail,
                "result": str(s.get("result") or "").strip(),
                "next": str(s.get("next") or "").strip(),
            })
            if t is None:
                continue
            has_known_subject_time = True
            per_subject[name] = per_subject.get(name, 0) + t
            subject_totals[name] = subject_totals.get(name, 0) + t
            group = subject_group(name)
            group_totals[group] = group_totals.get(group, 0) + t
            group_days.setdefault(group, set()).add(d)
            if t > 0:
                subject_days[name] = subject_days.get(name, 0) + 1
            day_minutes += t

        # Prefer explicit total_minutes; fall back to sum of subjects.
        tm = as_minutes(log.get("total_minutes"))
        if tm is None and has_known_subject_time:
            tm = day_minutes
        if tm is not None:
            total_minutes += tm
        if tm is not None and tm > 0:
            studied_days += 1

        daily.append({
            "date": d,
            "total": tm,
            "subjects": per_subject,
            "subject_details": subject_details,
            "phase": log.get("phase") or "",
            "focus": log.get("focus") or "",
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

        review = log.get("review") if isinstance(log.get("review"), dict) else {}
        focus = str(log.get("focus") or "").strip()
        if not focus:
            focus = " + ".join(
                detail["detail"] or detail["name"] for detail in subject_details[:3]
            )
        latest_log = {
            "date": d,
            "phase": str(log.get("phase") or "").strip(),
            "focus": focus,
            "mood": str(log.get("mood") or "").strip(),
            "tags": log.get("tags") or [],
            "subjects": subject_details,
            "next_actions": clean_list(review.get("next_actions") or log.get("next_actions")),
            "issues": clean_list(review.get("issues") or review.get("blockers") or log.get("issues")),
        }

    # Latest chapter per subject (most recent progress row wins).
    latest_chapter: dict[str, dict] = {}
    for row in progress_rows:
        latest_chapter[row["subject"]] = row

    # Completed-chapter count per subject (status == 完结). De-dupe by chapter
    # name so re-logging the same chapter as 完结 doesn't double count.
    chapters_done: dict[str, set] = {}
    for row in progress_rows:
        if row.get("status") == "完结" and row.get("chapter"):
            chapters_done.setdefault(row["subject"], set()).add(row["chapter"])
    subject_chapters_done = {s: len(c) for s, c in chapters_done.items()}

    recent = recent_summary(daily, window_days=7)
    timeline_events = build_timeline_events(progress_rows, timeline)

    today = date.today()
    days_to_exam = (EXAM_DATE - today).days

    return {
        "generated": today.isoformat(),
        "daily": daily,
        "subject_totals": subject_totals,
        "subject_days": subject_days,
        "subject_colors": SUBJECT_COLORS,
        "group_totals": {group: group_totals.get(group, 0) for group in GROUP_ORDER},
        "group_days": {group: len(group_days.get(group, set())) for group in GROUP_ORDER},
        "group_colors": GROUP_COLORS,
        "subject_chapters_done": subject_chapters_done,
        "progress_rows": progress_rows,
        "latest_chapter": latest_chapter,
        "latest_log": latest_log or {},
        "timeline": timeline,
        "timeline_events": timeline_events,
        "recent": recent,
        "alerts": subject_alerts(daily, subject_totals, recent),
        "summary": {
            "total_minutes": total_minutes,
            "studied_days": studied_days,
            "log_count": len(logs),
            "first_date": daily[0]["date"] if daily else None,
            "last_date": daily[-1]["date"] if daily else None,
            "avg_minutes": round(total_minutes / studied_days) if studied_days else 0,
            "current_phase": latest_nonempty(logs, "phase"),
            "latest_focus": (latest_log or {}).get("focus") or "未说明",
            "exam_date": EXAM_DATE.isoformat(),
            "days_to_exam": days_to_exam,
        },
    }


def recent_summary(daily: list[dict], window_days: int = 7) -> dict:
    """Summarize the last calendar window ending at the latest logged date."""
    if not daily:
        return {
            "days": window_days,
            "start_date": None,
            "end_date": None,
            "total_minutes": 0,
            "studied_days": 0,
            "avg_minutes": 0,
            "subject_totals": {},
            "top_day": None,
        }

    end = date.fromisoformat(daily[-1]["date"])
    start = end - timedelta(days=window_days - 1)
    recent_days = [d for d in daily if start <= date.fromisoformat(d["date"]) <= end]
    known_totals = [d["total"] for d in recent_days if d["total"] is not None]
    total = sum(known_totals)
    studied = sum(1 for t in known_totals if t > 0)
    subject_totals: dict[str, int] = {}
    for day in recent_days:
        for subject, minutes in day["subjects"].items():
            subject_totals[subject] = subject_totals.get(subject, 0) + minutes

    top_day = None
    known_days = [d for d in recent_days if d["total"] is not None]
    if known_days:
        best = max(known_days, key=lambda d: d["total"])
        top_day = {"date": best["date"], "total": best["total"]}

    return {
        "days": window_days,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "total_minutes": total,
        "studied_days": studied,
        "avg_minutes": round(total / studied) if studied else 0,
        "subject_totals": subject_totals,
        "top_day": top_day,
    }


def subject_alerts(daily: list[dict], subject_totals: dict[str, int], recent: dict) -> list[dict]:
    """Return lightweight balance reminders for subjects that are active now."""
    active_subjects = (set(subject_totals) | WATCH_SUBJECTS) - DEFERRED_SUBJECTS
    recent_subjects = {
        subject for subject, minutes in recent.get("subject_totals", {}).items() if minutes > 0
    }
    alerts = []
    for subject in sorted(active_subjects):
        if subject in recent_subjects:
            continue
        last_seen = None
        for day in reversed(daily):
            if day["subjects"].get(subject, 0) > 0:
                last_seen = day["date"]
                break
        alerts.append({
            "subject": subject,
            "message": f"近 {recent['days']} 天未记录",
            "last_seen": last_seen,
        })
    return alerts


def build_timeline_events(progress_rows: list[dict], timeline: list[dict]) -> list[dict]:
    """Merge chapter milestones and tags by date for a denser timeline slide."""
    by_date: dict[str, dict] = {}

    def event_for(day: str) -> dict:
        return by_date.setdefault(day, {
            "date": day,
            "milestones": [],
            "tags": [],
            "mood": "",
        })

    for row in progress_rows:
        if row.get("status") not in {"完结", "起步"}:
            continue
        event_for(row["date"])["milestones"].append({
            "subject": row.get("subject", ""),
            "chapter": row.get("chapter", ""),
            "status": row.get("status", ""),
        })

    for row in timeline:
        ev = event_for(row["date"])
        for tag in row.get("tags", []):
            if tag not in ev["tags"]:
                ev["tags"].append(tag)
        if row.get("mood"):
            ev["mood"] = row["mood"]

    return [by_date[d] for d in sorted(by_date)]


def build_html(data: dict) -> str:
    """Render the aggregated dashboard data into one self-contained HTML file."""
    payload = json.dumps(data, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__DASHBOARD_DATA__", payload)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>11408 学习看板</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Hanken+Grotesk:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --paper: #f0ebde;
  --paper-deep: #e4dcc9;
  --ink: #111111;
  --ink-soft: #3f3f3f;
  --ink-faint: rgba(17, 17, 17, .16);
  --grid: rgba(17, 17, 17, .08);
  --text: #111111;
  --muted: #5c6477;
  --rule: rgba(17, 17, 17, .38);
  --warm: #d77855;
  --teal: #9a8f5f;
  --violet: #b77b8f;
  --font-display: "Newsreader", "Noto Serif SC", Georgia, serif;
  --font-body: "Hanken Grotesk", "Noto Serif SC", "Microsoft YaHei", sans-serif;
  --font-mono: "DM Mono", ui-monospace, monospace;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--text);
  font-family: var(--font-body);
  background:
    linear-gradient(to right, var(--grid) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid) 1px, transparent 1px),
    var(--paper);
  background-size: 34px 34px;
}
button, input { font: inherit; }

.shell {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1.5px solid var(--ink);
  background: rgba(240, 235, 222, .92);
  backdrop-filter: blur(10px);
}
.topbar .shell {
  min-height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.brand {
  display: flex;
  align-items: baseline;
  gap: 12px;
  color: var(--ink);
}
.brand strong {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 600;
}
.brand span, .navmeta {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: .04em;
  color: var(--ink-soft);
}
.navmeta { text-align: right; line-height: 1.4; }

.hero {
  display: grid;
  grid-template-columns: minmax(0, .82fr) minmax(380px, 1.18fr);
  gap: 22px;
  align-items: stretch;
  padding: 32px 0 22px;
}
.hero-copy {
  border-top: 1.5px solid var(--ink);
  border-bottom: 1.5px solid var(--ink);
  padding: 26px 0 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.eyebrow {
  font-family: var(--font-mono);
  color: var(--ink);
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: 18px;
}
h1 {
  margin: 0;
  max-width: 620px;
  color: var(--ink);
  font-family: var(--font-display);
  font-size: clamp(42px, 5.6vw, 74px);
  font-weight: 400;
  line-height: .98;
  letter-spacing: 0;
}
.lead {
  max-width: 620px;
  margin: 18px 0 0;
  color: var(--muted);
  font-size: 18px;
  line-height: 1.65;
}
.hero-side {
  display: grid;
  gap: 16px;
}
.countdown {
  border: 1.5px solid var(--ink);
  padding: 20px 26px;
  background: rgba(240, 235, 222, .72);
}
.countdown .smallcap {
  display: block;
  margin-bottom: 14px;
}
.countdown .days {
  color: var(--ink);
  font-family: var(--font-display);
  font-size: clamp(64px, 9vw, 112px);
  line-height: 1;
}
.countdown .label {
  margin-top: 12px;
  color: var(--muted);
  font-size: 16px;
}
.latest {
  border: 1.5px solid var(--ink);
  padding: 22px 26px;
  background: var(--paper);
}
.latest h2, .panel h2 {
  margin: 0;
  color: var(--ink);
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 400;
  line-height: 1;
}
.latest-title {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
  border-bottom: 1px solid var(--ink-faint);
  padding-bottom: 16px;
  margin-bottom: 18px;
}
.date-pill {
  font-family: var(--font-mono);
  color: var(--ink);
  font-size: 12px;
  white-space: nowrap;
}
.focus {
  margin: 0 0 18px;
  font-size: 18px;
  line-height: 1.5;
}
.latest-list, .action-list, .log-list, .timeline, .progress-list {
  display: grid;
  gap: 12px;
}
.latest-item, .action, .log-row, .timeline-row, .progress-row {
  border-top: 1px solid var(--ink-faint);
  padding-top: 12px;
}
.latest-item {
  display: grid;
  grid-template-columns: 120px 1fr auto;
  gap: 12px;
  align-items: baseline;
}
.subject-name, .minutes, .tag, .smallcap {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: .04em;
}
.subject-name { color: var(--ink); }
.minutes { color: var(--muted); }
.latest-item .subject-name, .status, .date-pill { color: var(--warm); }
.detail { line-height: 1.55; }

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin: 0 0 22px;
}
.metric {
  border: 1.5px solid var(--ink);
  background: rgba(240, 235, 222, .78);
  padding: 22px;
  min-height: 132px;
}
.metric .value {
  color: var(--ink);
  font-family: var(--font-display);
  font-size: 52px;
  line-height: .95;
}
.metric .label {
  margin-top: 12px;
  color: var(--muted);
  font-size: 14px;
}
.grid {
  display: grid;
  grid-template-columns: minmax(0, 1.32fr) minmax(330px, .68fr);
  gap: 18px;
  padding-bottom: 58px;
}
.panel {
  border: 1.5px solid var(--ink);
  background: rgba(240, 235, 222, .86);
  padding: 26px;
  min-width: 0;
}
.panel.wide { grid-column: 1 / -1; }
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 20px;
  border-bottom: 1.5px solid var(--ink);
  padding-bottom: 14px;
  margin-bottom: 20px;
}
.panel-note {
  color: var(--muted);
  font-size: 13px;
  text-align: right;
}

.trend {
  height: 320px;
  display: grid;
  grid-template-columns: repeat(var(--bar-count), minmax(34px, 1fr));
  gap: 10px;
  align-items: end;
}
.bar-col {
  min-width: 0;
  display: grid;
  grid-template-rows: auto minmax(40px, 1fr) auto;
  gap: 8px;
  height: 100%;
}
.bar-value {
  color: var(--muted);
  font-family: var(--font-mono);
  font-size: 11px;
  text-align: center;
}
.bar {
  align-self: end;
  min-height: 3px;
  border: 1px solid var(--ink);
  display: flex;
  flex-direction: column-reverse;
  background: rgba(17, 17, 17, .06);
}
.segment { width: 100%; }
.bar-date {
  color: var(--muted);
  font-family: var(--font-mono);
  font-size: 11px;
  text-align: center;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 18px;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 13px;
}
.swatch { width: 12px; height: 12px; border: 1px solid var(--text); }

.group-bars { display: grid; gap: 16px; }
.group-row {
  display: grid;
  grid-template-columns: 76px 1fr 86px;
  gap: 12px;
  align-items: center;
}
.lane {
  height: 18px;
  border: 1px solid var(--ink);
  background: rgba(17, 17, 17, .05);
}
.lane-fill { height: 100%; }

.progress-row {
  display: grid;
  grid-template-columns: 190px 1fr 112px;
  gap: 16px;
  align-items: start;
}
.progress-row strong {
  color: var(--ink);
  font-weight: 700;
}
.chapter {
  color: var(--text);
  line-height: 1.5;
}
.status {
  display: inline-block;
  margin-left: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.log-row {
  display: grid;
  grid-template-columns: 96px 1fr 88px;
  gap: 14px;
  align-items: start;
}
.log-main {
  line-height: 1.55;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.tag {
  border: 1px solid var(--ink-faint);
  color: var(--ink);
  padding: 3px 7px;
}
.timeline-row {
  display: grid;
  grid-template-columns: 104px 1fr;
  gap: 14px;
  line-height: 1.55;
}
.action {
  line-height: 1.55;
}
.muted { color: var(--muted); }
.empty { color: var(--muted); line-height: 1.6; }

@media (max-width: 900px) {
  .shell { width: min(100% - 28px, 680px); }
  .topbar .shell { align-items: flex-start; flex-direction: column; padding: 14px 0; }
  .navmeta { text-align: left; }
  .hero, .grid { grid-template-columns: 1fr; }
  .hero { min-height: 0; padding-top: 34px; }
  .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .trend { overflow-x: auto; grid-auto-flow: column; grid-auto-columns: minmax(42px, 1fr); grid-template-columns: none; padding-bottom: 6px; }
  .progress-row, .log-row, .latest-item, .timeline-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
@media (max-width: 560px) {
  .metrics { grid-template-columns: 1fr; }
  .panel, .latest, .countdown, .metric { padding: 18px; }
  .panel-head { align-items: start; flex-direction: column; }
  .panel-note { text-align: left; }
  h1 { font-size: 52px; }
}
</style>
</head>
<body>
<header class="topbar">
  <div class="shell">
    <div class="brand"><strong>11408 学习看板</strong><span>Postgraduate Exam Prep</span></div>
    <div class="navmeta" id="navmeta"></div>
  </div>
</header>

<main class="shell">
  <section class="hero">
    <div class="hero-copy">
      <div class="eyebrow">Daily Progress Archive</div>
      <h1>Study Progress</h1>
      <p class="lead" id="lead"></p>
    </div>
    <aside class="hero-side">
      <div class="countdown">
        <div class="smallcap">Exam Countdown</div>
        <div class="days" id="daysToExam"></div>
        <div class="label" id="examLabel"></div>
      </div>
      <div class="latest">
        <div class="latest-title">
          <h2>最近一天</h2>
          <div class="date-pill" id="latestDate"></div>
        </div>
        <p class="focus" id="latestFocus"></p>
        <div class="latest-list" id="latestSubjects"></div>
      </div>
    </aside>
  </section>

  <section class="metrics" id="metrics"></section>

  <section class="grid">
    <section class="panel wide">
      <div class="panel-head">
        <h2>近 14 条记录</h2>
        <div class="panel-note">柱高为总时长，色块为科目构成</div>
      </div>
      <div class="trend" id="trend"></div>
      <div class="legend" id="legend"></div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>科目投入</h2>
        <div class="panel-note">按具体科目合并</div>
      </div>
      <div class="group-bars" id="groupBars"></div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>下一步</h2>
        <div class="panel-note">来自最新日志</div>
      </div>
      <div class="action-list" id="actions"></div>
    </section>

    <section class="panel wide">
      <div class="panel-head">
        <h2>当前推进</h2>
        <div class="panel-note">条形长度为累计投入占比</div>
      </div>
      <div class="progress-list" id="progressList"></div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>最近记录</h2>
        <div class="panel-note">保留原始节奏</div>
      </div>
      <div class="log-list" id="logList"></div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>节点</h2>
        <div class="panel-note">章节状态与标签</div>
      </div>
      <div class="timeline" id="timeline"></div>
    </section>
  </section>
</main>

<script id="dashboard-data" type="application/json">__DASHBOARD_DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById("dashboard-data").textContent);
const SUBJECT_COLORS = DATA.subject_colors || {};
const $ = id => document.getElementById(id);
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[c]));
const mmdd = value => value ? value.slice(5) : "";
function fmtMinutes(value) {
  if (value == null) return "未说明";
  const h = Math.floor(value / 60);
  const m = value % 60;
  if (h && m) return `${h}h${m}m`;
  if (h) return `${h}h`;
  return `${m}m`;
}
function colorForSubject(subject) {
  return SUBJECT_COLORS[subject] || "#6B7280";
}

function renderHero() {
  const s = DATA.summary;
  $("navmeta").innerHTML = `${esc(s.first_date || "")} 至 ${esc(s.last_date || "")}<br>生成于 ${esc(DATA.generated)}`;
  $("lead").textContent = `${s.current_phase || "未说明"}。最近主线：${s.latest_focus || "未说明"}。`;
  const days = s.days_to_exam;
  $("daysToExam").textContent = days > 0 ? days : (days === 0 ? "Today" : "Done");
  $("examLabel").textContent = `${s.exam_date} 初试首日`;
  const latest = DATA.latest_log || {};
  $("latestDate").textContent = latest.date || "暂无";
  $("latestFocus").textContent = latest.focus || "暂无最新记录";
  const subjects = (latest.subjects || []).filter(item => item.detail || item.time_min != null);
  $("latestSubjects").innerHTML = subjects.length ? subjects.map(item => `
    <div class="latest-item">
      <div class="subject-name">${esc(item.name)}</div>
      <div class="detail">${esc(item.detail || "未说明")}</div>
      <div class="minutes">${fmtMinutes(item.time_min)}</div>
    </div>`).join("") : `<div class="empty">暂无可展示的分科记录。</div>`;
}

function renderMetrics() {
  const s = DATA.summary;
  const recent = DATA.recent || {};
  const metrics = [
    [`${(s.total_minutes / 60).toFixed(1)}h`, "累计学习时长"],
    [fmtMinutes(s.avg_minutes), "学习日日均"],
    [`${s.studied_days} 天`, "有效学习日"],
    [fmtMinutes(recent.total_minutes || 0), "近 7 天投入"]
  ];
  $("metrics").innerHTML = metrics.map(([value, label]) => `
    <div class="metric"><div class="value">${esc(value)}</div><div class="label">${esc(label)}</div></div>
  `).join("");
}

function renderTrend() {
  const days = (DATA.daily || []).slice(-14);
  const maxTotal = Math.max(...days.map(day => day.total || 0), 1);
  $("trend").style.setProperty("--bar-count", days.length || 1);
  $("trend").innerHTML = days.map(day => {
    const height = day.total == null ? 12 : Math.max(4, (day.total / maxTotal) * 100);
    const entries = Object.entries(day.subjects || {});
    const segments = entries.length ? entries.map(([subject, minutes]) => `
      <div class="segment" title="${esc(subject)} ${fmtMinutes(minutes)}"
        style="height:${day.total ? (minutes / day.total) * 100 : 0}%;background:${colorForSubject(subject)}"></div>
    `).join("") : "";
    return `<div class="bar-col">
      <div class="bar-value">${fmtMinutes(day.total)}</div>
      <div class="bar" style="height:${height}%">${segments}</div>
      <div class="bar-date">${mmdd(day.date)}</div>
    </div>`;
  }).join("");

  const subjects = Object.keys(DATA.subject_totals || {}).sort((a, b) => DATA.subject_totals[b] - DATA.subject_totals[a]);
  $("legend").innerHTML = subjects.map(subject => `
    <span class="legend-item"><span class="swatch" style="background:${colorForSubject(subject)}"></span>${esc(subject)} · ${fmtMinutes(DATA.subject_totals[subject])}</span>
  `).join("");
}

function renderGroups() {
  const totals = DATA.subject_totals || {};
  const subjects = Object.keys(totals).sort((a, b) => totals[b] - totals[a]);
  const max = Math.max(...subjects.map(subject => totals[subject] || 0), 1);
  $("groupBars").innerHTML = subjects
    .map(subject => `<div class="group-row">
      <strong>${esc(subject)}</strong>
      <div class="lane"><div class="lane-fill" style="width:${(totals[subject] / max) * 100}%;background:${colorForSubject(subject)}"></div></div>
      <div class="minutes">${fmtMinutes(totals[subject])}</div>
    </div>`).join("") || `<div class="empty">暂无可统计时长。</div>`;
}

function renderActions() {
  const latest = DATA.latest_log || {};
  const actions = latest.next_actions && latest.next_actions.length
    ? latest.next_actions
    : ["继续记录明日学习主线、各科用时和需要补的尾巴。"];
  const issues = latest.issues || [];
  $("actions").innerHTML = [
    ...actions.map(item => `<div class="action">${esc(item)}</div>`),
    ...issues.map(item => `<div class="action muted">问题：${esc(item)}</div>`)
  ].join("");
}

function renderProgress() {
  const subjects = Object.keys(DATA.subject_totals || {}).sort((a, b) => DATA.subject_totals[b] - DATA.subject_totals[a]);
  const max = Math.max(...subjects.map(subject => DATA.subject_totals[subject] || 0), 1);
  const rows = subjects.map(subject => {
    const latest = (DATA.latest_chapter || {})[subject];
    const done = (DATA.subject_chapters_done || {})[subject] || 0;
    const width = ((DATA.subject_totals[subject] || 0) / max) * 100;
    const chapter = latest ? `${latest.chapter}<span class="status">${latest.status || ""}</span>` : "尚未记录章节进度";
    return `<div class="progress-row">
      <strong>${esc(subject)}</strong>
      <div>
        <div class="chapter">${chapter}</div>
        <div class="lane" style="margin-top:10px"><div class="lane-fill" style="width:${width}%;background:${colorForSubject(subject)}"></div></div>
      </div>
      <div class="minutes">${done} 章完结<br>${fmtMinutes(DATA.subject_totals[subject])}</div>
    </div>`;
  });
  $("progressList").innerHTML = rows.join("") || `<div class="empty">暂无章节进度。</div>`;
}

function renderLogs() {
  const rows = (DATA.daily || []).slice(-6).reverse().map(day => {
    const details = (day.subject_details || [])
      .filter(item => item.detail || item.time_min != null)
      .slice(0, 3)
      .map(item => `${item.name}：${item.detail || fmtMinutes(item.time_min)}`)
      .join("；");
    const tags = (day.tags || []).map(tag => `<span class="tag">${esc(tag)}</span>`).join("");
    return `<div class="log-row">
      <div class="date-pill">${esc(day.date)}</div>
      <div class="log-main">${esc(day.focus || details || day.mood || "未说明")}${tags ? `<div class="tags">${tags}</div>` : ""}</div>
      <div class="minutes">${fmtMinutes(day.total)}</div>
    </div>`;
  });
  $("logList").innerHTML = rows.join("") || `<div class="empty">暂无日志。</div>`;
}

function renderTimeline() {
  const events = (DATA.timeline_events || []).slice(-7).reverse();
  $("timeline").innerHTML = events.map(event => {
    const milestones = (event.milestones || []).map(item => `${item.subject} · ${item.chapter} ${item.status || ""}`);
    const tags = (event.tags || []).map(tag => `#${tag}`);
    const body = [...milestones, ...tags, event.mood].filter(Boolean).join("；");
    return `<div class="timeline-row"><div class="date-pill">${esc(event.date)}</div><div>${esc(body)}</div></div>`;
  }).join("") || `<div class="empty">暂无节点事件。</div>`;
}

renderHero();
renderMetrics();
renderTrend();
renderGroups();
renderActions();
renderProgress();
renderLogs();
renderTimeline();
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


