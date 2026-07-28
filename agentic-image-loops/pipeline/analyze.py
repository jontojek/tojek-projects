#!/usr/bin/env python3
"""Print score table + plateau verdict for a run. Stdlib only.

  python analyze.py --run-dir ..\\01_hillclimb [--window 3] [--epsilon 2]
"""
import argparse
import json
import os


def read_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--window", type=int, default=3)
    ap.add_argument("--epsilon", type=float, default=2.0)
    args = ap.parse_args()

    run = {r["n"]: r for r in read_jsonl(os.path.join(args.run_dir, "logs", "run.jsonl"))}
    judge = {r["n"]: r for r in read_jsonl(os.path.join(args.run_dir, "logs", "judge.jsonl"))}

    ns = sorted(run)
    totals = []
    print(f"{'n':>3}  {'status':<6}  {'total':>5}  {'time':>6}  prompt")
    for n in ns:
        r, j = run[n], judge.get(n, {})
        tot = j.get("total")
        totals.append((n, tot))
        print(f"{n:>3}  {r['status']:<6}  {str(tot):>5}  {r.get('gen_time_s', ''):>6}  {r['prompt'][:70]}")

    scored = [(n, t) for n, t in totals if t is not None]
    if len(scored) >= args.window + 1:
        recent = [t for _, t in scored[-(args.window + 1):]]
        delta = max(recent) - min(recent)
        verdict = "PLATEAU — stop" if delta < args.epsilon else "still climbing"
        print(f"\nlast {args.window + 1} totals: {recent}  spread={delta}  -> {verdict}")
    else:
        print(f"\n{len(scored)} scored iterations; need {args.window + 1} for a plateau verdict.")


if __name__ == "__main__":
    main()
