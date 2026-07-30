import unittest

from scripts.build_dashboard import SUBJECT_COLORS, aggregate


class DashboardAggregationTests(unittest.TestCase):
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

    def test_recent_window_and_subject_alerts_ignore_deferred_politics(self):
        data = aggregate([
            {
                "date": "2026-06-01",
                "total_minutes": 60,
                "subjects": [{"name": "英语", "time_min": 60, "detail": "单词"}],
                "progress": [],
                "tags": [],
            },
            {
                "date": "2026-06-08",
                "total_minutes": 120,
                "subjects": [{"name": "数学-高数", "time_min": 120, "detail": "660"}],
                "progress": [],
                "tags": [],
            },
        ])

        self.assertEqual(data["recent"]["days"], 7)
        self.assertEqual(data["recent"]["total_minutes"], 120)
        self.assertEqual(data["recent"]["avg_minutes"], 120)
        alert_subjects = {a["subject"] for a in data["alerts"]}
        self.assertIn("英语", alert_subjects)
        self.assertNotIn("政治", alert_subjects)

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


if __name__ == "__main__":
    unittest.main()
