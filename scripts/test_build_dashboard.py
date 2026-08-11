import unittest

from scripts.build_dashboard import SUBJECT_COLORS, aggregate, build_html


class DashboardAggregationTests(unittest.TestCase):
    def test_base_renderer_is_self_contained(self):
        html = build_html({"daily": []})
        self.assertNotIn("https://", html)
        self.assertNotIn("fonts.googleapis.com", html)

    def test_null_minutes_are_unknown_not_zero(self):
        data = aggregate([
            {
                "date": "2026-06-01",
                "total_minutes": None,
                "mood": None,
                "subjects": [
                    {"name": "数学-线代", "time_min": None, "detail": "学了矩阵"},
                    {"name": "专业课-组成原理", "time_min": None, "detail": "看了解析"},
                ],
                "progress": [],
                "tags": [],
            },
            {
                "date": "2026-06-02",
                "total_minutes": 90,
                "subjects": [
                    {"name": "数学-线代", "time_min": 90, "detail": "继续推进"},
                ],
                "progress": [],
                "tags": [],
            },
        ])

        self.assertIsNone(data["daily"][0]["total"])
        self.assertEqual(data["summary"]["total_minutes"], 90)
        self.assertEqual(data["summary"]["studied_days"], 1)
        self.assertEqual(data["summary"]["avg_minutes"], 90)
        self.assertEqual(data["subject_totals"]["数学-线代"], 90)
        self.assertEqual(data["subject_days"]["数学-线代"], 1)
        self.assertNotIn("专业课-组成原理", data["subject_totals"])

    def test_subject_alerts_only_track_structured_ongoing_subjects(self):
        data = aggregate([
            {
                "date": "2026-06-01",
                "total_minutes": 120,
                "subjects": [{"name": "专业课-组成原理", "time_min": 120, "detail": "第三章"}],
                "progress": [
                    {"subject": "专业课-组成原理", "chapter": "第三章", "status": "进行中"}
                ],
                "tags": [],
            },
            {
                "date": "2026-06-08",
                "total_minutes": 120,
                "subjects": [{"name": "数学-高数", "time_min": 120, "detail": "660"}],
                "progress": [
                    {"subject": "数学-高数", "chapter": "强化第二章", "status": "进行中"}
                ],
                "tags": [],
            },
        ])

        self.assertEqual(data["recent"]["days"], 7)
        self.assertEqual(data["recent"]["total_minutes"], 120)
        self.assertEqual(data["recent"]["avg_minutes"], 120)
        alert_subjects = {a["subject"] for a in data["alerts"]}
        self.assertEqual(data["active_subjects"], ["专业课-组成原理", "数学-高数"])
        self.assertIn("专业课-组成原理", alert_subjects)
        self.assertNotIn("英语", alert_subjects)
        self.assertNotIn("政治", alert_subjects)
        self.assertNotIn("其他", alert_subjects)

    def test_timeline_events_are_merged_by_date(self):
        data = aggregate([
            {
                "date": "2026-06-11",
                "total_minutes": 120,
                "subjects": [{"name": "数学-线代", "time_min": 120, "detail": "第三章"}],
                "progress": [
                    {"subject": "数学-线代", "chapter": "第三章 向量组", "status": "起步"},
                    {"subject": "专业课-组成原理", "chapter": "第二章", "status": "完结"},
                ],
                "tags": ["受伤", "章节完结"],
                "mood": "受干扰",
            }
        ])

        self.assertEqual(len(data["timeline_events"]), 1)
        event = data["timeline_events"][0]
        self.assertEqual(event["date"], "2026-06-11")
        self.assertEqual(event["tags"], ["受伤", "章节完结"])
        self.assertEqual(len(event["milestones"]), 2)

    def test_dashboard_summary_groups_subjects_and_keeps_latest_details(self):
        data = aggregate([
            {
                "date": "2026-06-01",
                "total_minutes": 180,
                "subjects": [
                    {"name": "数学-高数", "time_min": 90, "detail": "660 题"},
                    {"name": "专业课-组成原理", "time_min": 90, "detail": "浮点数"},
                ],
                "progress": [],
                "tags": [],
            },
            {
                "date": "2026-06-02",
                "phase": "基础阶段（一轮）",
                "total_minutes": 120,
                "focus": "线代第二章 + 英语作文",
                "subjects": [
                    {"name": "数学-线代", "time_min": 70, "detail": "矩阵习题"},
                    {"name": "英语", "time_min": 50, "detail": "作文模板"},
                ],
                "review": {
                    "next_actions": ["补计组习题", "复盘线代错题"],
                },
                "progress": [],
                "tags": ["作文"],
            },
        ])

        self.assertEqual(data["summary"]["current_phase"], "基础阶段（一轮）")
        self.assertEqual(data["summary"]["latest_focus"], "线代第二章 + 英语作文")
        self.assertEqual(data["group_totals"]["数学"], 160)
        self.assertEqual(data["group_totals"]["专业课"], 90)
        self.assertEqual(data["group_totals"]["英语"], 50)
        self.assertEqual(data["subject_colors"], SUBJECT_COLORS)
        self.assertEqual(data["latest_log"]["next_actions"], ["补计组习题", "复盘线代错题"])
        self.assertEqual(data["latest_log"]["subjects"][0]["detail"], "矩阵习题")

    def test_home_status_uses_recent_main_lines_and_latest_next_nodes(self):
        data = aggregate([
            {
                "date": "2026-07-27",
                "phase": "强化阶段",
                "total_minutes": 240,
                "subjects": [
                    {"name": "数学-高数", "time_min": 150, "detail": "第一章"},
                    {"name": "专业课-组成原理", "time_min": 90, "detail": "5.3 节"},
                ],
                "progress": [],
                "tags": [],
            },
            {
                "date": "2026-07-28",
                "phase": "强化阶段",
                "total_minutes": 330,
                "subjects": [
                    {
                        "name": "数学-高数",
                        "time_min": 180,
                        "detail": "第一章收尾",
                        "next": "完成第一章严选题。",
                    },
                    {
                        "name": "专业课-组成原理",
                        "time_min": 120,
                        "detail": "5.4 节",
                        "next": "继续 5.4 节。",
                    },
                    {"name": "英语", "time_min": 30, "detail": "单词"},
                ],
                "review": {
                    "next_actions": ["完成高数第一章严选题。", "继续学习计组 5.4 节。"],
                },
                "progress": [],
                "tags": [],
            },
        ])

        self.assertEqual(data["home_status"]["phase"], "强化阶段进行中")
        self.assertEqual(data["home_status"]["main"], "高数强化 × 组成原理")
        self.assertEqual(
            data["home_status"]["next"],
            "完成高数第一章严选题 · 继续学习计组 5.4 节",
        )

    def test_home_status_falls_back_to_latest_ongoing_progress(self):
        data = aggregate([
            {
                "date": "2026-08-01",
                "phase": "强化阶段",
                "total_minutes": 404,
                "subjects": [
                    {"name": "数学-高数", "time_min": 297, "detail": "强化第二章"},
                    {"name": "专业课-组成原理", "time_min": 107, "detail": "5.6 节"},
                ],
                "progress": [
                    {"subject": "数学-高数", "chapter": "强化第二章", "status": "进行中"},
                    {"subject": "专业课-组成原理", "chapter": "5.6 节", "status": "进行中"},
                ],
                "review": {"next_actions": []},
                "tags": [],
            }
        ])

        self.assertEqual(
            data["home_status"]["next"],
            "高数：强化第二章 · 组成原理：5.6 节",
        )
        self.assertFalse(data["summary"]["exam_date_confirmed"])

    def test_home_status_excludes_completed_subjects_from_main_line(self):
        data = aggregate([
            {
                "date": "2026-08-09",
                "phase": "强化阶段",
                "total_minutes": 382,
                "subjects": [
                    {"name": "数学-高数", "time_min": 202, "detail": "强化学习"},
                    {"name": "专业课-组成原理", "time_min": 99, "detail": "基础阶段完结"},
                ],
                "progress": [
                    {"subject": "专业课-组成原理", "chapter": "基础阶段", "status": "完结"},
                    {"subject": "专业课-操作系统", "chapter": "起步", "status": "起步"},
                ],
                "tags": [],
            },
            {
                "date": "2026-08-10",
                "phase": "强化阶段",
                "total_minutes": 349,
                "subjects": [
                    {"name": "数学-高数", "time_min": 254, "detail": "第二章严选题"},
                    {"name": "专业课-操作系统", "time_min": 95, "detail": "1.2 节"},
                ],
                "progress": [
                    {"subject": "数学-高数", "chapter": "强化第二章严选题", "status": "进行中"},
                    {"subject": "专业课-操作系统", "chapter": "1.2 节", "status": "进行中"},
                ],
                "tags": [],
            },
        ])

        self.assertEqual(data["home_status"]["main"], "高数强化 × 操作系统")

    def test_home_status_falls_back_to_minutes_without_progress_rows(self):
        data = aggregate([
            {
                "date": "2026-08-10",
                "phase": "强化阶段",
                "total_minutes": 349,
                "subjects": [
                    {"name": "数学-高数", "time_min": 254, "detail": "第二章严选题"},
                    {"name": "专业课-组成原理", "time_min": 95, "detail": "复习"},
                ],
                "progress": [],
                "tags": [],
            }
        ])

        self.assertEqual(data["home_status"]["main"], "高数强化 × 组成原理")
if __name__ == "__main__":
    unittest.main()
