#!/usr/bin/env python3
"""Build summary/runs.csv (one row per game) and summary/results.json (aggregate numbers) for one
evaluation, from its summary/runs.jsonl, replays/ and meta.json. Standard library only.

    python3 tools/build_summary.py evaluations/v130051
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = json.loads((ROOT / "data/vocab.json").read_text(encoding="utf-8"))
ENC = {v["key"].split(".", 1)[1]: v["name"] for v in VOCAB if v["key"].startswith("ENCOUNTER.")}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def ending(r: dict) -> str:
    """Where the run stopped; same buckets as the project's evaluation report."""
    if r["win"]:
        return "victory"
    if r["stuck"]:
        return "stalled"
    cs = r.get("combats") or []
    last = cs[-1] if cs and cs[-1]["floor"] == r["floor"] else None
    act = last["act"] if last else int(r["act"])
    if act >= 2:
        return "died_act3_boss" if last and last["room"] == "Boss" else "died_act3_other"
    return f"died_act{act + 1}"


def last_offcombat(path: Path) -> dict:
    """The last out-of-combat decision of a replay (its deck, relics)."""
    best = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            st = json.loads(line)
            if not st["g"][8] and "deck" in st:
                best = st
    return best


def main(ev: Path) -> None:
    meta = json.loads((ev / "meta.json").read_text(encoding="utf-8"))
    routine = set((ev / "routine_eval_seeds.txt").read_text(encoding="utf-8").split())
    runs = [json.loads(l) for l in (ev / "summary/runs.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = []
    for r in runs:
        rp = ev / "replays" / f"{r['seed']}.jsonl.gz"
        with gzip.open(rp, "rt", encoding="utf-8") as f:
            head = json.loads(f.readline())
        last = last_offcombat(rp)
        cs = r["combats"]
        boss = [c for c in cs if c["room"] == "Boss"]
        a1 = next((c for c in boss if c["act"] == 0), None)
        a2 = next((c for c in boss if c["act"] == 1), None)
        a3 = [c for c in boss if c["act"] == 2]
        hp = lambda c: f"{c['hp']}/{c['max_hp']}" if c else ""
        enc = lambda c: ENC.get(c["encounter"], c["encounter"]) if c else ""
        e = ending(r)
        rows.append({
            "seed": r["seed"], "result": "win" if r["win"] else "loss", "ending": e,
            "act": r["act"] + 1, "floor": r["floor"], "decisions": head["steps"], "routine_eval_seed": "yes" if r["seed"] in routine else "no",
            "combats": len(cs), "elites": sum(c["room"] == "Elite" for c in cs),
            "act1_boss": enc(a1), "act1_boss_hp_in": hp(a1),
            "act2_boss": enc(a2), "act2_boss_hp_in": hp(a2),
            "act3_boss1": enc(a3[0] if a3 else None), "act3_boss1_hp_in": hp(a3[0] if a3 else None),
            "act3_boss2": enc(a3[1] if len(a3) > 1 else None), "act3_boss2_hp_in": hp(a3[1] if len(a3) > 1 else None),
            "lost_to": "" if r["win"] else enc(cs[-1]) if cs and cs[-1]["floor"] == r["floor"] else "",
            "final_deck_size": len(last.get("deck", [])), "final_relics": len(last.get("rel", [])),
            "transcript": f"{ev.relative_to(ROOT).as_posix()}/transcripts/{r['seed']}.txt",
        })
    with open(ev / "summary/runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    n, k = len(runs), sum(r["win"] for r in runs)
    lo, hi = wilson(k, n)
    reach = lambda pred: sum(1 for r in runs if pred(r))
    a3b1 = reach(lambda r: any(c["act"] == 2 and c["room"] == "Boss" for c in r["combats"]))
    a3b2 = reach(lambda r: sum(c["act"] == 2 and c["room"] == "Boss" for c in r["combats"]) >= 2)
    ends = {}
    for row in rows:
        ends[row["ending"]] = ends.get(row["ending"], 0) + 1
    part = lambda inside: [r for r in runs if (r["seed"] in routine) == inside]
    split = {}
    for name, rs in (("routine_eval_seeds", part(True)), ("other_seeds", part(False))):
        w = sum(r["win"] for r in rs)
        a, b = wilson(w, len(rs))
        split[name] = {"games": len(rs), "wins": w, "win_rate": round(w / len(rs), 4), "win_rate_95ci_wilson": [round(a, 4), round(b, 4)]}
    res = {
        "model_version": meta["model_version"], "character": meta["character"], "ascension": meta["ascension"],
        "seeds": meta["seeds"], "games": n,
        "wins": k, "win_rate": k / n, "win_rate_95ci_wilson": [round(lo, 4), round(hi, 4)],
        "by_seed_group": split,
        "floor_mean": round(sum(r["floor"] for r in runs) / n, 2),
        "reached_act2": reach(lambda r: r["act"] >= 1) / n, "reached_act3": reach(lambda r: r["act"] >= 2) / n,
        "reached_act3_boss1": a3b1 / n, "beat_act3_boss1_given_reached": a3b2 / a3b1,
        "win_given_reached_act3_boss2": k / a3b2,
        "endings": ends,
    }
    (ev / "summary/results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 tools/build_summary.py evaluations/<id>")
    main(Path(sys.argv[1]).resolve())
