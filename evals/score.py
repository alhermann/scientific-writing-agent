"""Score a judged matching file against the ground truth.

Usage:
    python3 evals/score.py evals/results/<run>/matches_<cond>.json

Matching file format (produced by the judge step, human-verified):
{
  "condition": "A",
  "model": "...",
  "total_findings": 31,            # all findings the system reported
  "valid_extra_findings": 2,       # valid findings that add no new GT id:
                                   # genuine non-planted issues AND duplicate
                                   # reports of an already-matched flaw
  "matched": ["GT-01", "GT-05"],   # planted flaws the system found
  "localization_correct": ["GT-01"]  # subset of matched with correct location
}

Stdlib only.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

WEIGHTS = {"critical": 4, "major": 2, "minor": 1}


def score(matches_path: str | Path) -> dict:
    matches_path = Path(matches_path)
    m = json.loads(matches_path.read_text(encoding="utf-8"))
    gt_path = Path(__file__).parent / "data" / "ground_truth.json"
    gt = {f["id"]: f for f in json.loads(gt_path.read_text(encoding="utf-8"))["flaws"]}

    matched = set(m["matched"])
    unknown = matched - set(gt)
    if unknown:
        raise ValueError(f"matched ids not in ground truth: {unknown}")

    n_gt = len(gt)
    recall = len(matched) / n_gt

    # weighted recall
    w_total = sum(WEIGHTS[f["severity"]] for f in gt.values())
    w_hit = sum(WEIGHTS[gt[i]["severity"]] for i in matched)
    w_recall = w_hit / w_total

    # breakdowns
    def breakdown(keyfn) -> dict:
        out: dict = {}
        groups = defaultdict(list)
        for fid, f in gt.items():
            groups[keyfn(f)].append(fid)
        for g, fids in sorted(groups.items()):
            hit = len([i for i in fids if i in matched])
            out[g] = {"hit": hit, "of": len(fids),
                      "recall": round(hit / len(fids), 3)}
        return out

    total_findings = m.get("total_findings", 0)
    valid = len(matched) + m.get("valid_extra_findings", 0)
    precision = (valid / total_findings) if total_findings else None

    f1w = None
    if precision is not None and (w_recall + precision) > 0:
        f1w = 2 * w_recall * precision / (w_recall + precision)

    loc = m.get("localization_correct")
    localization = (len(loc) / len(matched)) if (loc and matched) else None

    return {
        "condition": m.get("condition"),
        "model": m.get("model"),
        "recall": round(recall, 3),
        "weighted_recall": round(w_recall, 3),
        "precision": round(precision, 3) if precision is not None else None,
        "weighted_f1": round(f1w, 3) if f1w is not None else None,
        "localization_accuracy": round(localization, 3) if localization is not None else None,
        "matched": f"{len(matched)}/{n_gt}",
        "by_severity": breakdown(lambda f: f["severity"]),
        "by_check": breakdown(lambda f: f["check"]),
        "by_category": breakdown(lambda f: f["rule_id"].split("-")[0]),
        "missed": sorted(set(gt) - matched),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    print(json.dumps(score(sys.argv[1]), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
