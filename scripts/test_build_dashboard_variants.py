import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import build_dashboard_variants as variants


class DashboardVariantTests(unittest.TestCase):
    def test_all_renderers_are_self_contained(self):
        data = variants.enriched_data()
        for html in (
            variants.render_signal(data),
            variants.render_capsule(data),
            variants.render_capsule_dashboard(data),
        ):
            self.assertNotIn("https://", html)
            self.assertNotIn("fonts.googleapis.com", html)

    def test_probability_subject_uses_display_name_without_changing_data_key(self):
        self.assertEqual(variants.display_subject("数学-概率"), "数学-概统")
        self.assertEqual(variants.display_subject("数学-线代"), "数学-线代")
        self.assertEqual(variants.canonical_subject("数学-概统"), "数学-概率")
        self.assertEqual(
            len(set(variants.CAPSULE_SUBJECT_COLORS.values())),
            len(variants.CAPSULE_SUBJECT_COLORS),
        )

    def test_monthly_summaries_use_dedicated_directory(self):
        self.assertEqual(
            variants.MONTHLY_SUMMARY_DIR,
            variants.ROOT / "StudyProgress" / "Summaries" / "Monthly",
        )
        subjects = variants.parse_monthly_subjects("2026-03")
        self.assertIn("数学-高数", [item["name"] for item in subjects])
        self.assertIn("其它", [item["name"] for item in subjects])
        self.assertTrue(all(item["minutes"] > 0 for item in subjects))
        # 月度小结的分科之和必须等于月度概览声明的总时长。
        declared = {
            month["month"]: month["total_minutes"]
            for month in variants.parse_progress_index()["months"]
        }
        for month, total in declared.items():
            monthly = variants.parse_monthly_subjects(month)
            if not monthly:
                continue
            self.assertEqual(
                sum(item["minutes"] for item in monthly), total, month
            )

    def test_month_bar_segments_store_minutes_instead_of_linear_widths(self):
        month = {
            "total_minutes": 100,
            "subjects": [
                {"name": "数学-高数", "minutes": 60},
                {"name": "英语", "minutes": 30},
            ],
        }
        html = variants.month_bar_segments(month)

        self.assertEqual(
            [item["name"] for item in variants.month_subject_items(month)],
            ["数学-高数", "英语", "未细分"],
        )
        self.assertIn('data-minutes="60" style="background:#E85D4E"', html)
        self.assertIn('data-minutes="30" style="background:#A8E6CF"', html)
        self.assertIn('title="未细分 10m" data-minutes="10"', html)
        self.assertLess(html.index("数学-高数"), html.index("英语"))
        self.assertLess(html.index("英语"), html.index("未细分"))
        self.assertIn(f"background:{variants.CAPSULE_OTHER_COLOR}", html)
        self.assertNotIn("width:", html)
        self.assertEqual(variants.month_bar_segments({"total_minutes": 0}), "")

    def test_variant_renderer_outputs_single_capsule_dashboard(self):
        data = variants.enriched_data()
        summary = data["summary"]
        archive = data["archive"]
        months = archive["months"]
        latest_date = summary["last_date"]
        latest_short_date = latest_date[5:]
        archive_days = sum(month["days"] for month in months)
        exam_subjects = {
            item["name"]: item["minutes"] for item in archive["exam_subjects"]
        }

        with TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            paths = variants.build_variants(out_dir=out_dir)

            self.assertEqual({path.name for path in paths}, {"dashboard.html"})
            self.assertFalse((out_dir / "dashboard_signal.html").exists())
            self.assertFalse((out_dir / "dashboard_capsule.html").exists())
            self.assertFalse((out_dir / "dashboard_capsule_dashboard.html").exists())
            self.assertFalse((out_dir / "DashboardTemplatePreviews.html").exists())
            self.assertFalse((out_dir / "dashboard_vellum.html").exists())

            capsule_dashboard = (out_dir / "dashboard.html").read_text(encoding="utf-8")
            self.assertIn("width: 1920px;", capsule_dashboard)
            self.assertIn("height: 1080px;", capsule_dashboard)
            self.assertIn("mobile-panel", capsule_dashboard)
            self.assertIn('class="mobile-nav"', capsule_dashboard)
            for section_id in [
                "mobile-overview",
                "mobile-monthly",
                "mobile-subjects",
                "mobile-progress",
                "mobile-logs",
            ]:
                self.assertIn(f'id="{section_id}"', capsule_dashboard)
            self.assertEqual(
                capsule_dashboard.count('class="mobile-recent-row"'),
                min(14, len(data["daily"])),
            )
            self.assertIn("mobile-month-grid", capsule_dashboard)
            self.assertIn("mobile-archive", capsule_dashboard)
            self.assertIn("mobile-nodes", capsule_dashboard)
            self.assertIn(".rotate-hint { display:block; }", capsule_dashboard)
            self.assertIn("class=\"slide active visible\"", capsule_dashboard)
            self.assertIn("data-dashboard-variant=\"capsule-dashboard\"", capsule_dashboard)
            self.assertIn("#E85D4E", capsule_dashboard)
            self.assertIn("#C4D94E", capsule_dashboard)
            self.assertIn("#C5B5E0", capsule_dashboard)
            self.assertIn("#8BB4F7", capsule_dashboard)
            self.assertIn("#A06CE8", capsule_dashboard)
            self.assertIn("#F2D160", capsule_dashboard)
            self.assertIn("#F5B895", capsule_dashboard)
            self.assertIn("#A8E6CF", capsule_dashboard)
            self.assertIn("#D98CB3", capsule_dashboard)
            self.assertGreaterEqual(capsule_dashboard.count("class=\"slide"), 5)
            self.assertIn(f'{months[0]["month"]} 至 {months[-1]["month"]}', capsule_dashboard)
            self.assertIn(
                variants.fmt_minutes(summary["archive_total_minutes"]), capsule_dashboard
            )
            home_status = data["home_status"]
            self.assertIn(
                f'<p class="status-phase">{home_status["phase"]}。</p>',
                capsule_dashboard,
            )
            self.assertIn(f'<p><b>主线：</b>{home_status["main"]}</p>', capsule_dashboard)
            self.assertIn(
                f'<p><b>下一节点：</b>{home_status["next"]}</p>',
                capsule_dashboard,
            )
            self.assertNotIn("最近主线：", capsule_dashboard)
            # 首页「最近一天」面板必须带上最新日志日期与主线，防止后续改动遮蔽 latest_log。
            latest_log = data["latest_log"]
            self.assertIn(f'<h2 style="margin-top:18px">{latest_log["date"]}</h2>', capsule_dashboard)
            self.assertIn(f'<p class="lead">{latest_log["focus"]}</p>', capsule_dashboard)
            self.assertNotIn("暂无记录", capsule_dashboard)
            self.assertIn(f"{archive_days}天", capsule_dashboard)
            self.assertIn("计划初试倒计时", capsule_dashboard)
            self.assertIn(f'{summary["days_to_exam"]}天', capsule_dashboard)
            self.assertNotIn(f"{archive_days} 天", capsule_dashboard)
            self.assertNotIn(f'{summary["days_to_exam"]} 天', capsule_dashboard)
            self.assertIn("grid-template-columns:repeat(5,1fr)", capsule_dashboard)
            self.assertIn('--display:"Anthropic Serif Display",Georgia', capsule_dashboard)
            self.assertIn('--body:system-ui,"Microsoft YaHei"', capsule_dashboard)
            self.assertIn('--ui:system-ui,"Microsoft YaHei"', capsule_dashboard)
            self.assertNotIn("data:font/woff2;base64,", capsule_dashboard)
            self.assertIn("font-variant-numeric:lining-nums proportional-nums", capsule_dashboard)
            self.assertIn('font-feature-settings:"lnum" 1,"pnum" 1', capsule_dashboard)
            self.assertIn("font-synthesis:none", capsule_dashboard)
            self.assertNotIn("Source Serif 4 Dashboard", capsule_dashboard)
            self.assertNotIn("tabular-nums", capsule_dashboard)
            self.assertNotIn('font-family:var(--metric)', capsule_dashboard)
            self.assertIn(".subject-pill > span,.latest-pill > em", capsule_dashboard)
            for label in ["累计", "日均", "有效天数", "初试倒计时", "近7日投入"]:
                self.assertIn(f"<span>{label}</span><b", capsule_dashboard)
            self.assertNotIn("初始倒计时", capsule_dashboard)
            self.assertIn("font-size:15px; color:rgba(26,26,26,.62)", capsule_dashboard)
            self.assertIn("font-size:14px; line-height:1.35", capsule_dashboard)
            self.assertIn(".metric-pill b { display:block; order:2;", capsule_dashboard)
            self.assertIn(".metric-pill > span { order:1;", capsule_dashboard)
            self.assertIn("月度概览", capsule_dashboard)
            # 月份卡片随日志增长，逐个断言而不是写死具体月份。
            for month in months:
                self.assertIn(month["month"], capsule_dashboard)
            self.assertEqual(capsule_dashboard.count('class="month-pill"'), len(months) * 2)
            for month in months:
                complete_summary = " · ".join(
                    f'{variants.display_subject(item["name"])} '
                    f'{variants.fmt_minutes(item["minutes"])}'
                    for item in variants.month_subject_items(month)
                )
                self.assertIn(f"<p>{complete_summary}</p>", capsule_dashboard)
            self.assertNotIn("考研 102h2m", capsule_dashboard)
            self.assertNotIn("考研 71h26m", capsule_dashboard)
            for name in ("数学-高数", "数学-概率"):
                self.assertIn(
                    f'{variants.display_subject(name)} · '
                    f'{variants.fmt_minutes(exam_subjects[name])}',
                    capsule_dashboard,
                )
            # 近 14 条趋势柱必须为每天每个有投入的科目渲染带时长的 title。
            for day in data["daily"][-14:]:
                for subject, minutes in (day.get("subjects") or {}).items():
                    if minutes:
                        self.assertIn(
                            f'title="{variants.display_subject(subject)} '
                            f'{variants.fmt_minutes(minutes)}"',
                            capsule_dashboard,
                        )
            self.assertIn('"数学-概率": "#C5B5E0"', capsule_dashboard)
            self.assertIn('"政治": "#D98CB3"', capsule_dashboard)
            self.assertIn("archive-subject-grid { display:grid; grid-template-columns:1fr", capsule_dashboard)
            self.assertIn("grid-template-columns:210px minmax(300px,1fr) 120px", capsule_dashboard)
            self.assertIn(".archive-subject-grid .capsule-track { height:28px; }", capsule_dashboard)
            self.assertNotIn("class=\"subject-pill other-row\"", capsule_dashboard)
            self.assertNotIn("aria-label=\"PRCV-Final · 25h41m\"", capsule_dashboard)
            self.assertNotIn("补录", capsule_dashboard)
            for label in [
                "最近一天",
                "近 14 条记录",
                "科目投入",
                "下一步",
                "当前推进",
                "最近记录",
                "节点",
            ]:
                self.assertIn(label, capsule_dashboard)
            self.assertIn("柱高为总时长，色块为当日科目", capsule_dashboard)
            self.assertIn('class="stack-track area-stack vertical"', capsule_dashboard)
            self.assertIn('class="capsule-fill area-stack horizontal"', capsule_dashboard)
            self.assertIn("function roundedRectAreaAt", capsule_dashboard)
            self.assertIn("function positionForArea", capsule_dashboard)
            self.assertIn("function lengthForRoundedRectArea", capsule_dashboard)
            self.assertNotIn(".stack-track i:first-child", capsule_dashboard)
            self.assertNotIn(".month-pill .capsule-track i:last-child", capsule_dashboard)
            self.assertIn("按基础 / 强化阶段分列", capsule_dashboard)
            self.assertIn("SUBJECT_COLORS", capsule_dashboard)
            self.assertNotIn("#6F90C9", capsule_dashboard)
            self.assertIn(
                ".tag { display:inline-flex; align-items:center; justify-content:center; "
                "padding:12px 28px; background:var(--yellow); color:var(--ink);",
                capsule_dashboard,
            )
            self.assertIn(
                ".tag.sky,.tag.lime,.tag.peach,.tag.violet,.tag.lavender,.tag.yellow { color:var(--ink); }",
                capsule_dashboard,
            )
            expected_label_swaps = [
                '<div class="tag sky">档案月度口径</div><h2 style="margin-top:20px">月度概览</h2>',
                '<div class="tag peach">来自最新日志</div><h2 style="margin-top:20px">下一步</h2>',
                '<div class="tag lavender">按基础 / 强化阶段分列</div><h2 style="margin-top:20px">当前推进</h2>',
                '<div class="tag yellow">保留原始节奏</div><h2 style="margin-top:20px">最近记录</h2>',
                '<div class="tag violet">章节状态与标签</div><h2 style="margin-top:20px">节点</h2>',
            ]
            for snippet in expected_label_swaps:
                self.assertIn(snippet, capsule_dashboard)

            # 当前推进：基础/强化阶段徽章分列，含档案期完结科目（数据结构），去掉课内/其他。
            done_stage = next(
                item
                for item in data["subject_stages"]
                if item["subject"] == "专业课-数据结构" and item["status"] == "完结"
            )
            self.assertIn(
                f'<b>专业课-数据结构</b><div class="phase-chips">'
                f'<span class="phase-chip done"><em>{variants.esc(done_stage["phase"])}</em>'
                f'<i>已完结</i></span>',
                capsule_dashboard,
            )
            self.assertIn(
                '<span class="phase-chip doing"><em>强化阶段</em>',
                capsule_dashboard,
            )
            # 进行中科目必须回显 latest_chapter 的当前章节，而不是历史章节。
            # 注意：不要求一定存在进行中章节（全部完结是合法状态）。
            ongoing_chapters = [
                row
                for row in (data.get("latest_chapter") or {}).values()
                if variants.progress_status_class(row.get("status")) == "doing"
                and row.get("chapter")
            ]
            for row in ongoing_chapters:
                self.assertIn(
                    f'<i>{variants.esc(row["chapter"] + " " + row["status"])}</i>',
                    capsule_dashboard,
                )
                self.assertNotIn(
                    f'<span class="phase-chip doing"><em>{variants.esc(row["chapter"])}</em>',
                    capsule_dashboard,
                )
            self.assertIn("phase-chip done", capsule_dashboard)
            self.assertNotIn("0 章完结", capsule_dashboard)
            self.assertNotIn("条形长度为累计投入占比", capsule_dashboard)
            self.assertNotIn("<b>其他</b>", capsule_dashboard)
            # 科目投入列表按累计时长渲染；零投入科目走“未开始”分支。
            for name in variants.SUBJECT_ORDER:
                label = variants.display_subject(name)
                minutes = exam_subjects.get(name, 0)
                if minutes:
                    self.assertIn(f"{label} · {variants.fmt_minutes(minutes)}", capsule_dashboard)
                else:
                    self.assertIn(f"{label} · 0m", capsule_dashboard)
            if any(not exam_subjects.get(name) for name in variants.SUBJECT_ORDER):
                self.assertIn("未开始 · 0h", capsule_dashboard)
            else:
                self.assertNotIn("未开始 · 0h", capsule_dashboard)
            archive_range = f'{months[0]["month"]} 至 {months[-1]["month"]}'
            self.assertIn(f"档案累计 · {archive_range}", capsule_dashboard)
            self.assertIn(f"近 7 日投入 · 截至 {latest_short_date}", capsule_dashboard)
            self.assertIn(f"数据截至 {latest_date}", capsule_dashboard)
            self.assertIn('aria-label="上一页"', capsule_dashboard)
            self.assertIn('aria-live="polite"', capsule_dashboard)
            self.assertIn("pointerdown", capsule_dashboard)
            self.assertNotIn("touchstart", capsule_dashboard)
            self.assertNotIn("https://", capsule_dashboard)

            recent_totals = dict(variants.subject_totals_for_days(data["daily"][-14:]))
            for name, minutes in recent_totals.items():
                self.assertIn(
                    f'{variants.display_subject(name)} · {variants.fmt_minutes(minutes)}',
                    capsule_dashboard,
                )
            # 图例只反映近 14 天窗口，近 14 天没有投入的科目不得出现在图例中
            # （历史上曾误用档案累计值填充图例）。
            for name in variants.SUBJECT_ORDER:
                if name in recent_totals:
                    continue
                self.assertNotIn(
                    f'class="legend-pill" style="--fill:{variants.capsule_color(name)}">'
                    f'{variants.display_subject(name)} · ',
                    capsule_dashboard,
                )
            self.assertNotIn(
                f'class="legend-pill" style="--fill:{variants.CAPSULE_OTHER_COLOR}">其它 · ',
                capsule_dashboard,
            )

    def test_subject_stages_parsed_from_progress_index(self):
        stages = variants.enriched_data()["subject_stages"]
        self.assertIn(
            {"subject": "专业课-数据结构", "phase": "基础阶段", "status": "完结"}, stages
        )
        # 档案用「数学-概统」写表，解析后统一为 canonical 键「数学-概率」。
        self.assertIn({"subject": "数学-概率", "phase": "基础阶段", "status": "完结"}, stages)
        self.assertIn(
            {"subject": "专业课-组成原理", "phase": "基础阶段", "status": "完结"},
            stages,
        )
        self.assertIn(
            {"subject": "专业课-操作系统", "phase": "基础阶段", "status": "完结"}, stages
        )
        self.assertIn(
            {"subject": "专业课-计算机网络", "phase": "基础阶段", "status": "进行中"},
            stages,
        )

    def test_progress_index_accepts_future_year_months(self):
        with TemporaryDirectory() as tmp:
            index = Path(tmp) / "ProgressIndex.md"
            index.write_text(
                "## 月度概览\n\n"
                "| 月份 | 有记录天数 | 总完成时长 | 考研相关 | 课内/其他 |\n"
                "|---|---:|---:|---:|---:|\n"
                "| 2027-01 | 2 | 10h | 10h | 0min |\n",
                encoding="utf-8",
            )
            with patch.object(variants, "PROGRESS_INDEX", index):
                self.assertEqual(variants.parse_progress_index()["months"][0]["month"], "2027-01")

    def test_enriched_data_aggregates_all_months_including_operating_systems(self):
        """档案聚合必须自洽；累计值随日志增长，因此校验关系而不是具体数字。"""
        data = variants.enriched_data()
        archive = data["archive"]
        months = archive["months"]
        exam_subjects = {item["name"]: item["minutes"] for item in archive["exam_subjects"]}

        # 每个月：分科之和等于月总时长，两栏相加也等于月总时长。
        for month in months:
            self.assertEqual(
                sum(item["minutes"] for item in month["subjects"]),
                month["total_minutes"],
                month["month"],
            )
            self.assertEqual(
                month["exam_minutes"] + month["other_minutes"],
                month["total_minutes"],
                month["month"],
            )

        # 档案累计由月度概览聚合而来，且考研与课内两栏覆盖全部时长。
        self.assertEqual(archive["all_total"], sum(m["total_minutes"] for m in months))
        exam_total_from_months = sum(
            item["minutes"]
            for month in months
            for item in month["subjects"]
            if variants.canonical_subject(item["name"]) in variants.SUBJECT_ORDER
        )
        other_total_from_months = sum(
            item["minutes"]
            for month in months
            for item in month["subjects"]
            if variants.canonical_subject(item["name"]) not in variants.SUBJECT_ORDER
        )
        self.assertEqual(archive["exam_total"], exam_total_from_months)
        self.assertEqual(archive["other_total"], other_total_from_months)
        self.assertEqual(archive["exam_total"] + archive["other_total"], archive["all_total"])

        # 科目投入列表按规范科目顺序给出所有已投入科目。
        self.assertEqual(
            [item["name"] for item in archive["exam_subjects"]],
            [name for name in variants.SUBJECT_ORDER if exam_subjects.get(name)],
        )
        self.assertTrue(archive["exam_subjects"])

        # 每个考研科目的累计必须等于各月分科之和；操作系统曾因漏聚合而不显示。
        for name in variants.SUBJECT_ORDER:
            expected = sum(
                item["minutes"]
                for month in months
                for item in month["subjects"]
                if variants.canonical_subject(item["name"]) == name
            )
            self.assertEqual(exam_subjects.get(name, 0), expected, name)
        self.assertGreater(exam_subjects.get("专业课-操作系统", 0), 0)

        # summary 的三项档案累计必须与 archive 保持一致。
        self.assertEqual(data["summary"]["archive_total_minutes"], archive["all_total"])
        self.assertEqual(data["summary"]["archive_exam_minutes"], archive["exam_total"])
        self.assertEqual(data["summary"]["archive_other_minutes"], archive["other_total"])

    def test_progress_index_months_reconcile_with_daily_logs(self):
        """月度概览必须与逐日日志一致，避免每次记录后手工同步漏改。"""
        from scripts import build_dashboard as base

        index = variants.parse_progress_index()
        by_month: dict[str, dict] = {}
        for log in base.load_logs():
            month = str(log.get("date") or "")[:7]
            if not month:
                continue
            subjects = log.get("subjects") or []
            values = [int(subject.get("time_min") or 0) for subject in subjects]
            declared = log.get("total_minutes")
            if declared is None and not any(values):
                continue
            bucket = by_month.setdefault(
                month, {"days": 0, "total": 0, "exam": 0, "other": 0}
            )
            bucket["days"] += 1
            bucket["total"] += int(declared) if declared is not None else sum(values)
            for subject, value in zip(subjects, values):
                key = variants.canonical_subject(subject.get("name", ""))
                bucket["exam" if key in variants.SUBJECT_ORDER else "other"] += value

        for month in index["months"]:
            bucket = by_month.get(month["month"])
            if bucket is None:
                continue  # 3-5 月只做月度补录，没有逐日日志
            self.assertEqual(bucket["days"], month["days"], month["month"])
            self.assertEqual(bucket["total"], month["total_minutes"], month["month"])
            self.assertEqual(bucket["exam"], month["exam_minutes"], month["month"])
            self.assertEqual(bucket["other"], month["other_minutes"], month["month"])

        # 反向：有逐日日志的月份必须在月度概览中出现，防止漏登一个月。
        declared_months = {month["month"] for month in index["months"]}
        self.assertFalse(set(by_month) - declared_months)

    def test_daily_log_totals_match_their_subjects(self):
        """每天的 total_minutes 必须等于各科之和；未知的结构化值写 null。"""
        from scripts import build_dashboard as base

        for log in base.load_logs():
            subjects = log.get("subjects") or []
            subtotal = sum(int(subject.get("time_min") or 0) for subject in subjects)
            declared = log.get("total_minutes")
            if declared is None:
                continue
            self.assertEqual(int(declared), subtotal, log.get("date"))
            # 带科目前缀的条目必须是规范考研科目，防止 frontmatter 写入
            # “数学-概统”“操作系统”这类非规范键而被看板静默丢掉。
            for subject in subjects:
                log_date = log.get("date")
                name = str(subject.get("name") or "").strip()
                self.assertTrue(name, log_date)
                if name.startswith(("数学-", "专业课-")):
                    self.assertIn(name, variants.SUBJECT_ORDER, log_date)


if __name__ == "__main__":
    unittest.main()
