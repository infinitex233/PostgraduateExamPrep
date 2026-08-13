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
        self.assertIn(
            {"name": "数学-高数", "minutes": 3608},
            variants.parse_monthly_subjects("2026-03"),
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
            self.assertIn("2026-03", capsule_dashboard)
            self.assertIn("2026-06", capsule_dashboard)
            self.assertIn("2026-07", capsule_dashboard)
            self.assertIn("2026-08", capsule_dashboard)
            self.assertEqual(capsule_dashboard.count('class="month-pill"'), len(months) * 2)
            self.assertIn("数学-高数 60h8m", capsule_dashboard)
            self.assertIn("专业课-数据结构 29h16m", capsule_dashboard)
            self.assertIn("专业课-组成原理 24h16m", capsule_dashboard)
            for month in months:
                complete_summary = " · ".join(
                    f'{variants.display_subject(item["name"])} '
                    f'{variants.fmt_minutes(item["minutes"])}'
                    for item in variants.month_subject_items(month)
                )
                self.assertIn(f"<p>{complete_summary}</p>", capsule_dashboard)
            self.assertNotIn("考研 102h2m", capsule_dashboard)
            self.assertNotIn("考研 71h26m", capsule_dashboard)
            self.assertIn(
                f'数学-高数 · {variants.fmt_minutes(exam_subjects["数学-高数"])}',
                capsule_dashboard,
            )
            self.assertIn(
                f'数学-概统 · {variants.fmt_minutes(exam_subjects["数学-概率"])}',
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
            self.assertIn(
                '<b>专业课-数据结构</b><div class="phase-chips">'
                '<span class="phase-chip done"><em>基础阶段</em><i>已完结</i></span>',
                capsule_dashboard,
            )
            self.assertIn(
                '<span class="phase-chip doing"><em>强化阶段</em><i>强化第三章 进行中</i></span>',
                capsule_dashboard,
            )
            self.assertIn("phase-chip done", capsule_dashboard)
            self.assertNotIn("0 章完结", capsule_dashboard)
            self.assertNotIn("条形长度为累计投入占比", capsule_dashboard)
            self.assertNotIn("<b>其他</b>", capsule_dashboard)
            self.assertIn("专业课-操作系统 · 0m", capsule_dashboard)
            self.assertIn("专业课-计算机网络 · 0m", capsule_dashboard)
            self.assertIn("政治 · 0m", capsule_dashboard)
            self.assertIn("未开始 · 0h", capsule_dashboard)
            self.assertIn("档案累计 · 2026-03 至 2026-08", capsule_dashboard)
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
            self.assertNotIn("数学-线代 · 62h19m", capsule_dashboard)
            self.assertNotIn("其它 · 55h54m", capsule_dashboard)

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
            {"subject": "专业课-操作系统", "phase": "基础阶段", "status": "进行中"},
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


if __name__ == "__main__":
    unittest.main()
