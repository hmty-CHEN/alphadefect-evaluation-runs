#!/usr/bin/env python3
"""Build evaluations/index.csv (one row per evaluation) from every evaluations/*/summary/results.json
and print the same table as Markdown. Standard library only.

    python3 tools/build_index.py
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["evaluation", "model_version", "character", "ascension", "game_version", "seeds", "games", "wins", "win_rate",
          "win_rate_ci_low", "win_rate_ci_high", "floor_mean"]
ORDER = ["Defect", "Regent", "Silent", "Fool"]      # characters in the order they were added


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def main() -> None:
    rows = []
    def key(p: Path):
        r = json.loads(p.read_text(encoding="utf-8"))
        c = r["character"]
        return (ORDER.index(c) if c in ORDER else len(ORDER), c, r["model_version"])

    for res in sorted((ROOT / "evaluations").glob("*/summary/results.json"), key=key):
        r = json.loads(res.read_text(encoding="utf-8"))
        meta = json.loads((res.parents[1] / "meta.json").read_text(encoding="utf-8"))
        lo, hi = wilson(r["wins"], r["games"])
        rows.append({
            "evaluation": res.parents[1].name, "model_version": r["model_version"], "character": r["character"],
            "ascension": r["ascension"], "game_version": meta.get("game_version", ""), "seeds": r["seeds"], "games": r["games"], "wins": r["wins"],
            "win_rate": round(r["win_rate"], 4), "win_rate_ci_low": round(lo, 4), "win_rate_ci_high": round(hi, 4), "floor_mean": r["floor_mean"],
        })
    with open(ROOT / "evaluations/index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("| Evaluation | Character | Games | Wins | Win rate (95% CI) | Mean floor |\n|---|---|---|---|---|---|")
    for r in rows:
        lo, hi = wilson(r["wins"], r["games"])
        print(f"| [{r['evaluation']}](evaluations/{r['evaluation']}) | {r['character']} | {r['games']:,} | {r['wins']:,} "
              f"| {r['win_rate']:.1%} ({lo:.1%}–{hi:.1%}) | {r['floor_mean']} |")


if __name__ == "__main__":
    main()
