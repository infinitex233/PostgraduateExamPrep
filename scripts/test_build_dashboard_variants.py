import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import build_dashboard_variants as variants


class DashboardVariantTests(unittest.TestCase):
    def test_probability_subject_uses_display_name_without_changing_data_key(self):
        self.assertEqual(variants.display_subject("数学-概率"), "数学-概统")
        self.assertEqual(variants.display_subject("数学-线代"), "数学-线代")
        self.assertEqual(variants.canonical_subject("数学-概统"), "数学-概率")

    def test_monthly_summaries_use_dedicated_directory(self):
        self.assertEqual(
            variants.MONTHLY_SUMMARY_DIR,
            variants.ROOT / "StudyProgress" / "Summaries" / "Monthly",
        )
        self.assertIn(
            {"name": "数学-高数", "minutes": 3608},
            variants.parse_monthly_subjects("2026-03"),
        )

    def test_variant_renderer_outputs_single_capsule_dashboard(self):
        data = variants.enriched_data()
        summary = data["summary"]
        archive = data["archive"]
        months = archive["months"]
        archive_days = sum(month["days"] for month in months)
        exam_subjects = {
            item["name"]: item["minutes"] for item in archive["exam_subjects"]
        }
        latest_probability_day = next(
            day for day in reversed(data["daily"]) if "数学-概率" in day["subjects"]
        )

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
            self.assertIn("横屏", capsule_dashboard)
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
            self.assertIn(f"{archive_days}天", capsule_dashboard)
            self.assertIn("距初试首日", capsule_dashboard)
            self.assertIn(f'{summary["days_to_exam"]}天', capsule_dashboard)
            self.assertNotIn(f"{archive_days} 天", capsule_dashboard)
            self.assertNotIn(f'{summary["days_to_exam"]} 天', capsule_dashboard)
            self.assertIn("grid-template-columns:repeat(5,1fr)", capsule_dashboard)
            self.assertIn("月度概览", capsule_dashboard)
            self.assertIn("2026-03", capsule_dashboard)
            self.assertIn("2026-06", capsule_dashboard)
            self.assertIn("数学-高数 60h8m", capsule_dashboard)
            self.assertIn("专业课-数据结构 29h16m", capsule_dashboard)
            self.assertIn("其它 5h19m", capsule_dashboard)
            self.assertIn("专业课-组成原理 24h16m", capsule_dashboard)
            self.assertIn("其它 55h54m", capsule_dashboard)
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
            self.assertIn(
                'title="数学-概统 '
                f'{variants.fmt_minutes(latest_probability_day["subjects"]["数学-概率"])}"',
                capsule_dashboard,
            )
            self.assertIn('"数学-概率": "#C5B5E0"', capsule_dashboard)
            self.assertIn("archive-subject-grid { display:grid; grid-template-columns:1fr", capsule_dashboard)
            self.assertIn("grid-template-columns:220px minmax(360px,1fr) 110px", capsule_dashboard)
            self.assertIn(".archive-subject-grid .capsule-track { height:42px; }", capsule_dashboard)
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
            self.assertIn("柱高为总时长，色块为科目构成", capsule_dashboard)
            self.assertIn("条形长度为累计投入占比", capsule_dashboard)
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
                '<div class="tag sky">整体节奏</div><h2 style="margin-top:20px">月度概览</h2>',
                '<div class="tag lime">柱高为总时长，色块为科目构成</div><h2 style="margin-top:20px">近 14 条记录</h2>',
                '<div class="tag lime">按学习记录累计</div><h2 style="margin-top:20px">科目投入</h2>',
                '<div class="tag peach">来自最新日志</div><h2 style="margin-top:20px">下一步</h2>',
                '<div class="tag lavender">条形长度为累计投入占比</div><h2 style="margin-top:20px">当前推进</h2>',
                '<div class="tag yellow">保留原始节奏</div><h2 style="margin-top:20px">最近记录</h2>',
                '<div class="tag violet">章节状态与标签</div><h2 style="margin-top:20px">节点</h2>',
            ]
            for snippet in expected_label_swaps:
                self.assertIn(snippet, capsule_dashboard)


if __name__ == "__main__":
    unittest.main()
