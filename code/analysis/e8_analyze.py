import csv, json, sys
import numpy as np
D = sys.argv[1]
TAU = 0.2617101
TAU2 = 0.55
pred = {r["pair_id"]: r for r in csv.DictReader(open(f"{D}/results/ariadne/E8/pred_absent_unfiltered_noexit.csv"))}
man = {r["pair_id"]: r for r in csv.DictReader(open(f"{D}/results/ariadne/E8/build_manifest.csv"))}
print("pred rows", len(pred), "manifest rows", len(man), "status", {r["status"] for r in pred.values()})
assert set(pred) == set(man)
ids = sorted(pred)
rows = []
for i in ids:
    p, m = pred[i], man[i]
    rows.append(dict(id=i, tile=m["tile"], layer=m["layer"], score=float(p["score"]),
                     found=int(p["found"]), ncc=float(m["plain_ncc_max"]), filt=int(m["ncc_filtered_out"])))
score = np.array([r["score"] for r in rows]); found = np.array([r["found"] for r in rows])
ncc = np.array([r["ncc"] for r in rows]); filt = np.array([r["filt"] for r in rows])
layer = np.array([r["layer"] for r in rows]); tile = np.array([r["tile"] for r in rows])
acc = score >= TAU; acc55 = score >= TAU2
print("accept@tau (score>=tau) overall", acc.sum(), acc.mean())
print("pipeline found col overall", found.sum(), found.mean())
print("accept@0.55 overall", acc55.sum(), acc55.mean())
print("ncc>=0.5 count", (ncc >= 0.5).sum(), "filt flag count", filt.sum(), "consistency ncc>=0.5 vs flag", ((ncc>=0.5)==(filt==1)).all())
for L in ["m1","m2"]:
    s = layer==L
    print(L, "n", s.sum(), "accept", acc[s].sum(), round(acc[s].mean(),4), "acc@0.55", acc55[s].sum(), "found", found[s].sum())
sub = ncc >= 0.5
print("filtered-out subset n", sub.sum(), "accept", acc[sub].sum(), round(acc[sub].mean(),4) if sub.sum() else None)
print("rest n", (~sub).sum(), "accept", acc[~sub].sum(), round(acc[~sub].mean(),4) if (~sub).sum() else None)
print("filtered-out acc@0.55", acc55[sub].sum(), "rest acc@0.55", acc55[~sub].sum())
# tile-cluster bootstrap
tiles = sorted(set(tile)); idx_by = {t: np.where(tile==t)[0] for t in tiles}
def boot(mask_vals, layer_mask=None, B=2000):
    rng = np.random.default_rng(20261010)
    out = []
    T = len(tiles)
    for _ in range(B):
        pick = rng.integers(0, T, T)
        idx = np.concatenate([idx_by[tiles[k]] for k in pick])
        v = mask_vals[idx]
        if layer_mask is not None:
            v = v[layer_mask[idx]]
        out.append(v.mean() if len(v) else np.nan)
    return np.nanpercentile(out, [2.5, 97.5])
print("n tiles", len(tiles), "per tile pairs", set(len(v) for v in idx_by.values()))
print("CI overall tau", boot(acc.astype(float)))
print("CI m1", boot(acc.astype(float), layer=="m1"))
print("CI m2", boot(acc.astype(float), layer=="m2"))
print("CI overall 0.55", boot(acc55.astype(float)))
print("found==(score>=0.55) all:", bool(((score>=TAU2)==(found==1)).all()))
print("found==(score>=tau) all:", bool(((score>=TAU)==(found==1)).all()))
json.dump(dict(n=len(rows), tau=TAU, accept_tau=int(acc.sum()), rate_tau=float(acc.mean()),
  ci_overall=list(map(float,boot(acc.astype(float)))), ci_m1=list(map(float,boot(acc.astype(float), layer=="m1" if False else (layer=="m1")))), ci_m2=list(map(float,boot(acc.astype(float), layer=="m2" if False else (layer=="m2")))), ncc_ge_05=int(sub.sum()),
  rows=rows), open("e8_summary.json","w"))
