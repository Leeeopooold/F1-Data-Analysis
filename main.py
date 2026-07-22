"""F1 遥测对比命令行入口。"""

from __future__ import annotations

import argparse
from pathlib import Path

from f1_analysis import (
    DEFAULT_COLORS,
    build_summary_table,
    get_fastest_laps,
    load_session,
    plot_telemetry,
    plot_track_speed_delta,
    save_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="比较 F1 单圈遥测数据，并导出量化摘要与赛道地图。"
    )
    parser.add_argument("--year", type=int, default=2024, help="赛季年份（默认：2024）")
    parser.add_argument("--event", default="Bahrain", help="分站名称或轮次（默认：Bahrain）")
    parser.add_argument("--session", default="Q", help="比赛阶段，如 Q、R、FP1（默认：Q）")
    parser.add_argument(
        "--drivers", nargs="+", default=["VER", "LEC"], help="车手缩写，至少两位（默认：VER LEC）"
    )
    parser.add_argument(
        "--xlim", nargs=2, type=float, metavar=("START", "END"), help="遥测图的赛道距离范围（米）"
    )
    parser.add_argument("--cache-dir", type=Path, default=Path("f1_cache"), help="FastF1 缓存目录")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="报告输出目录")
    parser.add_argument("--show", action="store_true", help="生成文件后同时显示图表窗口")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if len(args.drivers) < 2:
        raise SystemExit("--drivers 至少需要提供两位车手，例如：--drivers VER LEC")

    print(f"加载 {args.year} {args.event} {args.session} 数据…")
    session = load_session(args.year, args.event, args.session, args.cache_dir)
    laps = get_fastest_laps(session, args.drivers)
    summary = build_summary_table(laps)

    # 使用赛事和车手组合命名产物，便于在同一个输出目录中保留多次分析结果。
    args.output_dir.mkdir(parents=True, exist_ok=True)
    name = f"{args.year}_{str(args.event).replace(' ', '_')}_{args.session}_{'_vs_'.join(args.drivers)}"
    summary_path = args.output_dir / f"{name}_summary.csv"
    telemetry_path = args.output_dir / f"{name}_telemetry.png"
    track_map_path = args.output_dir / f"{name}_track_speed_delta.png"

    # 先保存可复用的数值结果，再输出面向人工复盘的图表。
    save_summary(summary, summary_path)
    plot_telemetry(laps, telemetry_path, DEFAULT_COLORS, xlim=args.xlim, show=args.show)
    plot_track_speed_delta(laps[args.drivers[0]], laps[args.drivers[1]], track_map_path, show=args.show)

    print("\n最快圈量化摘要：")
    print(summary.to_string(index=False))
    print(f"\n已导出：\n- {summary_path}\n- {telemetry_path}\n- {track_map_path}")


if __name__ == "__main__":
    main()
