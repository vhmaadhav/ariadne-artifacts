"""Print selected metrics (value [lo, hi]) per method from an iris_report JSON."""
import json, sys
path = sys.argv[1]
keys = sys.argv[2].split(",") if len(sys.argv) > 2 else ["loc_only@5", "success@1", "success@3", "success@5", "gross_rate", "err_px_p50", "err_px_p90", "F1", "absent_accepted", "present_declined", "auroc_present", "correct_match_auc"]
j = json.load(open(path, encoding="utf-8"))
for name, m in j["methods"].items():
    def find(d, key):
        if isinstance(d, dict):
            if key in d and isinstance(d[key], dict) and "value" in d[key]:
                return d[key]
            for k, v in d.items():
                if k == "strata":
                    continue
                r = find(v, key)
                if r is not None:
                    return r
    row = []
    for k in keys:
        v = find(m, k)
        row.append(f"{k} {v['value']:.3f} [{v['lo']:.3f},{v['hi']:.3f}]" if v else f"{k} n/a")
    print(f"{name}: " + " | ".join(row))
