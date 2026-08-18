#!/usr/bin/env python3
"""Create a deterministic minimal Feishu Base provisioning plan from normalized OGSM JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


STATUS_OPTIONS = ["待更新", "未开始", "已启动", "进行中", "接近完成", "待验收", "受阻", "已完成"]


def field(name: str, kind: str, **kwargs):
    return {"name": name, "type": kind, **kwargs}


def build_plan(model: dict, base_name: str, table_name: str) -> dict:
    records = model.get("records", [])
    strategies = sorted({r.get("strategy", "").strip() for r in records if r.get("strategy", "").strip()})
    owner_queries = sorted({r.get("owner", "").strip() for r in records if r.get("owner", "").strip()})
    fields = [
        field("行动", "text", primary=True, description="一条记录对应一个可执行行动；作为主字段。"),
        field("源记录ID", "text", unique_key=True, description="稳定导入键；重复运行时用于更新而非重复创建。"),
        field("O｜目的", "text"), field("G｜目标", "text"),
        field("S｜策略", "select", multiple=False, options=strategies), field("M｜衡量", "text"),
        field("负责人", "user", multiple=False), field("协作人", "user", multiple=True),
        field("负责人原文（备查）", "text"), field("开始日期", "datetime"), field("截止日期", "datetime"),
        field("进度状态", "select", multiple=False, options=STATUS_OPTIONS),
        field("当前进度（自动）", "formula", expression='SWITCH([进度状态],"已启动",20,"进行中",50,"接近完成",80,"待验收",90,"已完成",100,"受阻",20,0)'),
        field("健康灯（自动）", "formula", expression='IFS([当前进度（自动）]=100,"🟢 绿灯",[进度状态]="受阻","🔴 红灯",NOT(ISBLANK([风险/卡点])),"🔴 红灯",AND(NOT(ISBLANK([截止日期])),[截止日期]<TODAY()),"🔴 红灯",AND(NOT(ISBLANK([截止日期])),DAYS([截止日期],TODAY())<=7,[当前进度（自动）]<80),"🟡 黄灯",DAYS(TODAY(),[最后修改时间])>7,"🟡 黄灯",TRUE(),"🟢 绿灯")'),
        field("风险/卡点", "text"), field("下一步动作", "text"), field("交付物/证据", "text"),
        field("升级提醒对象", "user", multiple=True), field("最后修改时间", "updated_at"),
        field("源文件", "text"), field("源工作表", "text"), field("源行号", "number"), field("导入指纹", "text"),
    ]

    planned_records = []
    fingerprint = model.get("source", {}).get("sha256", "")
    for row in records:
        planned_records.append({
            "源记录ID": row.get("source_record_id"), "行动": row.get("action"),
            "O｜目的": row.get("objective"), "G｜目标": row.get("goal"),
            "S｜策略": row.get("strategy"), "M｜衡量": row.get("measure"),
            "负责人原文（备查）": row.get("owner"), "开始日期": row.get("start_date") or None,
            "截止日期": row.get("due_date") or None, "进度状态": row.get("status") or "待更新",
            "风险/卡点": row.get("risk"), "下一步动作": row.get("next_action"),
            "交付物/证据": row.get("evidence"), "源文件": row.get("source_file"),
            "源工作表": row.get("source_sheet"), "源行号": row.get("source_row"), "导入指纹": fingerprint,
        })

    return {
        "plan_version": 1,
        "mode": "minimal-one-table",
        "base": {"name": base_name, "table_name": table_name},
        "confirmation_required": {
            "owner_identity": owner_queries,
            "review_issues": model.get("issues", []),
            "health_profile": "default-v1",
            "workflows_enabled": False,
        },
        "fields": fields,
        "record_upsert_key": "源记录ID",
        "records": planned_records,
        "views": [
            {"name": "00｜O-G-S-M行动总览", "type": "grid", "group_by": "S｜策略"},
            {"name": "01｜红灯事项", "type": "grid", "filter": [["健康灯（自动）", "==", "🔴 红灯"]]},
            {"name": "02｜风险关注", "type": "grid", "filter": [["风险/卡点", "isNotEmpty", None]]},
            {"name": "03｜待更新", "type": "grid", "filter": [["进度状态", "==", "待更新"]]},
            {"name": "04｜进度状态看板", "type": "kanban", "group_by": "进度状态"},
            {"name": "05｜策略进度看板", "type": "kanban", "group_by": "S｜策略"},
        ],
        "dashboard": [
            {"name": "总体平均进度", "type": "statistics", "measure": ["当前进度（自动）", "AVERAGE"]},
            {"name": "健康灯分布", "type": "pie", "group_by": "健康灯（自动）", "measure": ["行动", "COUNT"]},
            {"name": "各策略平均进度", "type": "bar", "group_by": "S｜策略", "measure": ["当前进度（自动）", "AVERAGE"]},
            {"name": "各负责人平均进度", "type": "bar", "group_by": "负责人", "measure": ["当前进度（自动）", "AVERAGE"]},
        ],
        "workflows": [
            {"name": "截止日期变更提醒", "enabled": False, "trigger": "截止日期被修改", "receiver": "负责人"},
            {"name": "红灯每日汇总", "enabled": False, "trigger": "每日定时", "receiver": "升级提醒对象", "deduplicate": True},
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("normalized", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-name", required=True)
    parser.add_argument("--table-name", default="OGSM行动")
    parser.add_argument("--allow-review", action="store_true", help="Build a plan despite review issues; does not authorize Base writes")
    args = parser.parse_args()
    model = json.loads(args.normalized.read_text(encoding="utf-8"))
    summary = model.get("summary", {})
    if summary.get("blocking_issue_count", 0):
        print("blocking precheck issues remain; no plan created", file=sys.stderr)
        return 2
    if summary.get("review_issue_count", 0) and not args.allow_review:
        print("review issues remain; obtain user confirmation or pass --allow-review to create a draft plan", file=sys.stderr)
        return 3
    plan = build_plan(model, args.base_name, args.table_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "records": len(plan["records"]), "output": str(args.output), "workflows_enabled": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
