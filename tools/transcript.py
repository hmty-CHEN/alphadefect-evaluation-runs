#!/usr/bin/env python3
"""Turn a raw replay (replays/RTxxxx.jsonl.gz) into a readable English transcript.

    python3 tools/transcript.py replays/RT0000.jsonl.gz            # print to stdout
    python3 tools/transcript.py replays/RT0000.jsonl.gz -o out.txt
    python3 tools/transcript.py --all replays transcripts          # regenerate every transcript

Standard library only. Names come from data/vocab.json (index = vocabulary ID used in the replays).
See docs/replay-format.md for the meaning of every field.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = json.loads((ROOT / "data/vocab.json").read_text(encoding="utf-8"))
ENC = {v["key"].split(".", 1)[1]: v["name"] for v in VOCAB if v["key"].startswith("ENCOUNTER.")}

DECISION = ["Stuck", "Combat", "Card select", "Card reward", "Pick a pack", "Rewards", "Event", "Rest site", "Shop", "Treasure",
            "Crystal Sphere", "Map", "Game over"]
ROOM = ["Unassigned", "Monster", "Elite", "Boss", "Treasure", "Shop", "Event", "Rest site", "Map"]
PURPOSE = ["transform", "exhaust", "remove", "enchant", "discard", "upgrade", "card-specific"]
INTENT_FLAGS = ["Attack", "Buff", "Debuff", "Defend", "Heal/Summon", "Stun/Sleep/Escape", "Other"]
SHOP_KIND = ["Card", "Relic", "Potion", "Removal"]
K_CREATURE, K_CARD, K_MAP, K_OPTION = 2, 4, 8, 9


def nm(i: int) -> str:
    return VOCAB[i]["name"] if 0 <= i < len(VOCAB) else f"#{i}"


def up(n: int) -> str:
    return "+" * n if n and n > 0 else ""


def obj_name(o, st) -> str:
    if not o:
        return ""
    k, i, z, ex = o
    if k == K_CARD:
        return nm(i) + up(ex)
    if k == K_CREATURE:
        if z == 1:
            return "self"
        same = sum(1 for e in st.get("en", []) if e["n"] == i)
        return nm(i) + (f" #{ex}" if same > 1 else "")
    if k == K_OPTION:
        v, aux = ex
        s = nm(aux) if i <= 1 and aux else nm(i)
        return f"{s} {v}" if s == "Gold" and v else s
    if k == K_MAP:
        return f"{nm(i)} (row {ex[0] + 1}, col {ex[1] + 1})"
    return nm(i)


def cand_text(c, st) -> str:
    k, A, B, key, f0, f1, f2 = c
    a, b = obj_name(A, st), obj_name(B, st)
    return {
        1: lambda: "End turn",
        2: lambda: f"Play {a}" + (f" -> {b}" if B else ""),
        3: lambda: f"Use potion {a}" + (f" -> {b}" if B else ""),
        4: lambda: f"Discard potion {a}",
        5: lambda: f"Select {a}",
        6: lambda: "Confirm selection",
        7: lambda: f"Take {a}",
        8: lambda: nm(key),
        9: lambda: f"Pick pack {f0 + 1}",
        10: lambda: f"Take reward: {a}",
        11: lambda: "Leave / skip",
        12: lambda: a + (f" ({b})" if B else ""),
        13: lambda: a,
        14: lambda: f"Buy {a}" + (f" ({f0} gold)" if f0 else ""),
        15: lambda: f"Go to {a}",
        16: lambda: f"Take relic {a}",
        17: lambda: "Skip relic",
        18: lambda: f"Crystal Sphere cell ({f0}, {f1}), {'big' if f2 else 'small'} tool",
    }.get(k, lambda: f"Action type {k}")()


def pct(p: float) -> str:
    return f"{p * 100:.1f}%" if p >= 0.001 else "<0.1%"


def cards(lst) -> str:
    """[[card, upgrades], ...] -> 'Strike x4, Zap+, ...' in first-seen order."""
    cnt = Counter((c[0], c[1]) for c in lst)
    return ", ".join(nm(i) + up(u) + (f" x{n}" if n > 1 else "") for (i, u), n in cnt.items()) or "(none)"


def intent(e) -> str:
    dmg, hits, flags = e["it"]
    parts = []
    for on, label in zip(flags, INTENT_FLAGS):
        if on:
            parts.append(f"Attack {dmg}" + (f"x{hits}" if hits > 1 else "") if label == "Attack" else label)
    move = next((m for m in e.get("mv", []) if m[1] == 0), None)
    s = " + ".join(parts) or "Unknown"
    return f"{nm(move[0])}: {s}" if move else s


def cost(h) -> str:
    """Hand entry [card, upgrades, cost, playable, damage, block] -> its cost as shown in game ('X', or '-' when unplayable)."""
    if h[2] >= 0:
        return str(h[2])
    return "X" if VOCAB[h[0]]["cost"] == -1 else "-"


def powers(p) -> str:
    return ", ".join(f"{nm(i)} {a}" if a else nm(i) for i, a in p)


def combat_state(st) -> list[str]:
    g, pl = st["g"], st.get("pl", {})
    out = [f"HP {pl.get('hp', g[2])}/{pl.get('m', g[3])}  Block {pl.get('b', 0)}  Energy {g[5]}/{g[6]}"
           + (f"  Orbs ({st.get('os', 0)} slots): " + (", ".join(f"{nm(o[0])}" for o in st.get("orb", [])) or "empty") if st.get("os") else "")
           + (f"  Powers: {powers(pl['p'])}" if pl.get("p") else "")]
    for e in st.get("en", []):
        if not e.get("al", 1):
            continue
        out.append(f"Enemy {nm(e['n'])}: HP {e['hp']}/{e['m']}" + (f"  Block {e['b']}" if e["b"] else "")
                   + f"  Intent {intent(e)}" + (f"  Powers: {powers(e['p'])}" if e.get("p") else ""))
    hand = ", ".join(nm(h[0]) + up(h[1]) + f" [{cost(h)}]" for h in st.get("hand", []))
    out.append(f"Hand: {hand or '(empty)'}  | Draw {st.get('draw', 0)}  Discard {len(st.get('disc', []))}  Exhaust {len(st.get('exh', []))}")
    if st.get("pot"):
        out.append("Potions: " + ", ".join(nm(p[0]) for p in st["pot"]))
    return out


def decision_line(n: int, st, indent: str) -> list[str]:
    c = st["c"]
    chosen = st["a"]
    probs = {i: p for i, p in st.get("pr", [])}
    p = probs.get(chosen)
    head = f"{indent}#{n:<4} {cand_text(c[chosen], st)}" if chosen < len(c) else f"{indent}#{n:<4} (action {chosen})"
    head += f"   [{pct(p) if p is not None else '<0.5%'}, {len(c)} option{'s' if len(c) != 1 else ''}]"
    lines = [head]
    # identical options (e.g. two copies of Defend in hand) are separate candidates; group them by their text
    mine = cand_text(c[chosen], st) if chosen < len(c) else None
    alts: dict[str, list[float]] = {}
    for i, q in st.get("pr", []):
        if i != chosen and i < len(c):
            alts.setdefault(cand_text(c[i], st), []).append(q)
    if alts and len(c) > 1:
        parts = []
        for t, qs in alts.items():
            s = f"{t} {pct(qs[0])}" + (f" x{len(qs)}" if len(qs) > 1 else "")
            parts.append(s + (" (identical option)" if t == mine else ""))
        lines.append(f"{indent}       also: " + "; ".join(parts))
    return lines


def transcript(path: Path) -> str:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        head = json.loads(f.readline())
        steps = [json.loads(s) for s in f if s.strip()]
    combats = {c["floor"]: c for c in head.get("combats", [])}
    res = "VICTORY" if head["win"] else "DEFEAT"
    out = [f"AlphaDefect v{head['version']} - seed {head['seed']} - Defect, Ascension 10",
           f"Result: {res} on floor {head['floor']} (Act {head['act'] + 1}), {len(steps)} decisions",
           "Each decision: #step  chosen action   [model probability of that action, number of legal options]",
           "               'also:' lists the other options the model gave >= 0.5% probability.", ""]
    floor = turn = None
    deck = relics = None
    last_out = None
    for n, st in enumerate(steps):
        g = st["g"]
        act, fl, in_combat = g[0], g[1], g[8]
        if fl != floor:
            floor, turn = fl, None
            room = ROOM[g[9]] if 0 <= g[9] < len(ROOM) else str(g[9])
            cb = combats.get(fl)
            title = f"{cb['room']}: {ENC.get(cb['encounter'], cb['encounter'])}" if cb else room
            out += ["", f"=== Act {act + 1} - Floor {fl} - {title} ===   HP {g[2]}/{g[3]}  Gold {g[4]}"]
        if not in_combat:
            if st.get("deck") is not None:
                d = Counter((c[0], c[1]) for c in st["deck"])
                if deck is None:
                    out.append(f"  Deck ({sum(d.values())}): {cards(st['deck'])}")
                elif d != deck:
                    add, rem = d - deck, deck - d
                    ch = [f"+{nm(i)}{up(u)}" + (f" x{k}" if k > 1 else "") for (i, u), k in add.items()]
                    ch += [f"-{nm(i)}{up(u)}" + (f" x{k}" if k > 1 else "") for (i, u), k in rem.items()]
                    out.append(f"  Deck change: {', '.join(ch)}  ({sum(d.values())} cards)")
                deck = d
            r = [x[0] for x in st.get("rel", [])]
            if relics is None:
                out.append(f"  Relics: {', '.join(nm(i) for i in r)}")
            else:
                new = [i for i in r if i not in relics]
                lost = [i for i in relics if i not in r]
                if new:
                    out.append(f"  Relic gained: {', '.join(nm(i) for i in new)}")
                if lost:
                    out.append(f"  Relic lost: {', '.join(nm(i) for i in lost)}")
            relics = r
            cx = st.get("cx") or []
            ench = [f"{nm(c[1])}{up(c[2])} <{nm(c[3])} {c[4]}>" for c in cx if c[0] == 7 and c[3]]
            if ench and ench != last_out:
                out.append(f"  Enchanted cards in deck: {', '.join(ench)}")
                last_out = ench
            if st["d"] == 8 and st.get("shop"):
                sh = st["shop"]
                items = [f"{SHOP_KIND[i[0]] if 0 <= i[0] < 4 else '?'} {nm(i[1]) if i[0] != 3 else ''}{up(i[5])} {i[2]}g"
                         + ("" if i[3] else " (sold)") for i in sh["it"]]
                out.append(f"  Shop shelf (gold {sh['g']}): " + "; ".join(x.replace("  ", " ") for x in items))
            if st["d"] == 2 and st.get("sel"):
                s = st["sel"]
                out.append(f"  Select cards - purpose: {PURPOSE[s[0]] if 0 <= s[0] < len(PURPOSE) else 'other'}"
                           + (f" (from {nm(s[4])})" if s[4] else "") + f", choose {s[1]}-{s[2]}, already chosen {s[3]}")
            label = DECISION[st["d"]] if 0 <= st["d"] < len(DECISION) else str(st["d"])
            for i, line in enumerate(decision_line(n, st, "  ")):
                out.append(line.replace(f"#{n:<4}", f"#{n:<4} [{label}]", 1) if i == 0 else line)
        else:
            if g[7] != turn:
                turn = g[7]
                out.append(f"  -- Turn {turn} --")
                out += ["     " + s for s in combat_state(st)]
            elif st["d"] == 2 and st.get("sel"):
                s = st["sel"]
                out.append(f"     Select cards - purpose: {PURPOSE[s[0]] if 0 <= s[0] < len(PURPOSE) else 'other'}"
                           + (f" (from {nm(s[4])})" if s[4] else "") + f", choose {s[1]}-{s[2]}")
            out += decision_line(n, st, "     ")
    last = steps[-1] if steps else None
    out += ["", f"=== End: {res} on floor {head['floor']} ==="]
    if deck is not None:
        out.append(f"Final deck ({sum(deck.values())}): " + ", ".join(nm(i) + up(u) + (f" x{k}" if k > 1 else "") for (i, u), k in deck.items()))
    if relics:
        out.append(f"Final relics ({len(relics)}): {', '.join(nm(i) for i in relics)}")
    if last and last.get("pot"):
        out.append(f"Potions held at the end: {', '.join(nm(p[0]) for p in last['pot'])}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--all", action="store_true", help="src and dst are directories")
    a = ap.parse_args()
    if a.all:
        dst = Path(a.dst or "transcripts"); dst.mkdir(parents=True, exist_ok=True)
        for p in sorted(Path(a.src).glob("*.jsonl.gz")):
            (dst / (p.name.removesuffix(".jsonl.gz") + ".txt")).write_text(transcript(p), encoding="utf-8")
    else:
        text = transcript(Path(a.src))
        if a.out:
            Path(a.out).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
