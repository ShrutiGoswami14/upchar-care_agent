"""Run the eval set against the agent. Usage (from project root): python -m evals.run_evals [--save-baseline]

Scores: tool selection, argument accuracy, task completion (reply text / database state), overall pass rate.
Compares against evals/baseline.json to flag regressions after you change a prompt, model or tool.
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Select the isolated evaluation database before importing db or agent.
os.environ["EVAL_MODE"] = "1"

import db
from agent import build_agent, run_agent

HERE = Path(__file__).parent


def check_case(case, reply, calls):
    called = [n for n, _ in calls]
    exp = set(case["expected_tools"])
    forbidden = set(case.get("must_not_call", []))
    if exp:
        tool_ok = exp.issubset(called) and not (forbidden & set(called))
    elif forbidden:
        tool_ok = not (forbidden & set(called))
    else:
        tool_ok = not called  # no tool should be used

    args_ok = True
    for tool, want in case.get("expected_args", {}).items():
        args_ok = args_ok and any(n == tool and all(str(a.get(k)) == str(v) for k, v in want.items()) for n, a in calls)

    complete = True
    if "contains" in case:
        complete = complete and any(s.lower() in reply.lower() for s in case["contains"])
    if "db_check" in case:
        conn = db.connect()
        got = conn.execute(case["db_check"]["sql"]).fetchone()[0]
        conn.close()
        complete = complete and got == case["db_check"]["expected"]
    return tool_ok, args_ok, complete


async def main():
    cases = json.loads((HERE / "eval_cases.json").read_text())
    agent = await build_agent()
    rows = []
    for case in cases:
        db.reset()
        start = time.time()
        try:
            reply, calls = await run_agent(agent, case["prompt"], thread_id=f"eval-{case['id']}")
            error = None
        except Exception as e:  # keep going so one failure doesn't stop the run
            reply, calls, error = "", [], str(e)
        tool_ok, args_ok, complete = check_case(case, reply, calls) if not error else (False, False, False)
        rows.append({"id": case["id"], "tool_ok": tool_ok, "args_ok": args_ok, "complete": complete,
                     "passed": tool_ok and args_ok and complete, "latency_s": round(time.time() - start, 2),
                     "tools": [n for n, _ in calls], "reply": reply[:200], "error": error})
        print(f"{'PASS' if rows[-1]['passed'] else 'FAIL'}  {case['id']:<22} tools={rows[-1]['tools']}", flush=True)
        await asyncio.sleep(float(os.getenv("EVAL_DELAY", "4")))  # avoid free-tier rate limits

    n = len(rows)
    summary = {
        "cases": n,
        "tool_selection_acc": round(sum(r["tool_ok"] for r in rows) / n, 3),
        "arg_acc": round(sum(r["args_ok"] for r in rows) / n, 3),
        "task_completion": round(sum(r["complete"] for r in rows) / n, 3),
        "pass_rate": round(sum(r["passed"] for r in rows) / n, 3),
        "avg_latency_s": round(sum(r["latency_s"] for r in rows) / n, 2),
    }
    print("\nSUMMARY", json.dumps(summary, indent=2), flush=True)

    (HERE / "latest.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))
    baseline_path = HERE / "baseline.json"
    if "--save-baseline" in sys.argv:
        baseline_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))
        print("Saved as baseline.", flush=True)
    elif baseline_path.exists():
        base = json.loads(baseline_path.read_text())
        base_pass = {r["id"]: r["passed"] for r in base["rows"]}
        regress = [r["id"] for r in rows if base_pass.get(r["id"]) and not r["passed"]]
        print("REGRESSIONS vs baseline:", regress or "none", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
