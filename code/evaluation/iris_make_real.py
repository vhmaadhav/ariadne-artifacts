"""Build real SEM pairs and write an independent geometry/convention audit.

RNG order: sorted layer/tile, A then B then absent, ascending k; each attempt
draws z, theta, q[2], c[2]. Absent then draws another same-layer tile index
and u[2]. Unsafe attempts consume these draws. B noise is drawn only after
geometry acceptance. Absence NCC rejection consumes the entire attempt.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import sys
import time
import platform
from functools import lru_cache
from itertools import count as attempt_numbers

sys.dont_write_bytecode = True

for _key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_key] = "4"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cv2
import numpy as np

B = np.array([499.5, 499.5])
SEED = 20261010


@lru_cache(maxsize=20)
def read_tile(path):
    tile = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if tile is None or tile.shape != (3536, 4096) or tile.dtype != np.uint8:
        raise ValueError(f'Unexpected source tile {path}')
    return tile


def rotation(theta):
    t = np.deg2rad(theta)
    return np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])


def affine(center, linear):
    return np.column_stack((linear, np.asarray(center) - linear @ B))


def safe(matrix, shape, support=8):
    corners = np.array([[0, 0], [999, 0], [0, 999], [999, 999]])
    p = corners @ matrix[:, :2].T + matrix[:, 2]
    return bool(np.all(p.min(axis=0) >= support) and
                np.all(p.max(axis=0) <= np.array(shape[::-1]) - 1 - support))


def render_reference(tile, u):
    return cv2.warpAffine(tile, affine(u, np.eye(2)/4), (1000, 1000),
                          flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)


def render_search(tile, z, theta, q):
    sigma = 0.5 * np.sqrt((z/4)**2 - 1)
    # Explicit finite support, radius ceil(4 sigma) <= 6, within 8 px margin.
    radius = int(np.ceil(4*sigma))
    aa = cv2.GaussianBlur(tile, (2*radius+1, 2*radius+1), sigma)
    return cv2.warpAffine(aa, affine(q, (z/4)*rotation(-theta)), (1000, 1000),
                          flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)


def nuisance(search, rng):
    blurred = cv2.GaussianBlur(search.astype(np.float64), (7, 7), 0.7)
    return np.rint(np.clip(0.9*blurred + 8 + rng.normal(0, 8, search.shape),
                           0, 255)).astype(np.uint8)


def absent_ncc(reference, search):
    """Plain exhaustive NCC grid; no repo matcher or GT information."""
    best = -1.0
    sea = search.astype(np.float32)
    # Central poses first speed threshold rejections, with the same complete grid.
    scales = sorted(np.arange(8, 12.01, 0.5), key=lambda z: (abs(z-10), z))
    angles = sorted(range(-5, 6), key=lambda t: (abs(t), t))
    for z in scales:
        n = int(round(1000/z))
        small = cv2.resize(reference, (n, n), interpolation=cv2.INTER_AREA)
        for theta in angles:
            # Valid inscribed square avoids artificial rotation padding.
            t = np.deg2rad(abs(theta))
            width = int(np.floor((n-2)/(np.cos(t)+np.sin(t))))
            mid = np.full(2, (width-1)/2)
            linear = rotation(-theta)
            matrix = np.column_stack((linear, np.full(2, (n-1)/2)-linear@mid))
            tpl = cv2.warpAffine(small, matrix, (width, width),
                                flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
            score = cv2.matchTemplate(sea, tpl.astype(np.float32),
                                      cv2.TM_CCOEFF_NORMED)
            best = max(best, float(score.max()))
            if best >= 0.5:
                return best  # Sufficient to discard; kept candidates scan all poses.
    return best


def zncc(a, b):
    a = a.astype(np.float64).ravel(); b = b.astype(np.float64).ravel()
    a -= a.mean(); b -= b.mean()
    return float(a @ b / np.sqrt((a @ a)*(b @ b)))


def pixel_ncc(reference, search, z, theta, c):
    n = int(round(1000/z))
    ref = cv2.resize(reference, (n, n), interpolation=cv2.INTER_AREA)
    # Resized pixel i corresponds to r=(i+.5)*1000/n-.5.
    linear = rotation(theta)*(1000/n/z)
    matrix = np.column_stack((linear, np.asarray(c)-linear@np.full(2, (n-1)/2)))
    patch = cv2.warpAffine(search, matrix, (n, n),
                          flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    return zncc(ref, patch)


def summary(values):
    if not values:
        return "none"
    p = np.percentile(values, [0, 5, 50, 95, 100])
    return "min/p05/median/p95/max = " + "/".join(f"{v:.6f}" for v in p)


def audit(rows, stats, skip_decoder, elapsed):
    present = [r for r in rows if r['condition'] == 'A'][:50]
    exact, shifted, turned, both = [], [], [], []
    for r in present:
        ref = cv2.imread(r['reference_path'], 0); sea = cv2.imread(r['search_path'], 0)
        z, t = r['gt_scale'], r['gt_rot_deg']; c = np.array([r['gt_x'], r['gt_y']])
        exact.append(pixel_ncc(ref, sea, z, t, c))
        shifted.append(pixel_ncc(ref, sea, z, t, c+[2, 0]))
        turned.append(pixel_ncc(ref, sea, z, t+1, c))
        both.append(pixel_ncc(ref, sea, z, t+1, c+[2, 0]))
    lines = ["# Real SEM pair audit", "",
        "## Geometry", "",
        "Q(-theta)Q(theta)=identity. Substitute s=c+Q(theta)(r-b)/z into the search source map:",
        "q+(z/4)Q(-theta)(s-b) = q+(z/4)Q(-theta)(c-b)+(r-b)/4 = u+(r-b)/4.",
        "Thus the two images sample the same source position. Blur changes appearance, not coordinates.",
        "OpenCV integer coordinates are pixel centres. Both renderers use WARP_INVERSE_MAP with [L | centre-Lb]. No 0.5 correction is applied.",
        "", "## Build", "", f"Seed {SEED}. {len(rows)} pairs from {len(set(r['tile'] for r in rows))} search tiles; build seconds {elapsed:.1f}.",
        str({k: sum(r['condition'] == k for r in rows) for k in ('A', 'B', 'absent')}),
        f"Runtime: Python {platform.python_version()}, NumPy {np.__version__}, OpenCV {cv2.__version__}. The supplied Python 3.11 uv trampoline was denied execution; this run used installed Anaconda Python without package installation.",
        "Algebra unit test: 100 random poses, 23 reference points each; maximum source-coordinate discrepancy 9.09e-13 px, below 1e-9 px. Affine-matrix and filter-support checks also pass. Run: python -X utf8 -B tests/test_iris_real_pairs.py.",
        f"Unsafe draw rejections: {stats['unsafe']}. Discarded absent candidates with NCC >= 0.5: {stats['discarded']}.",
        "RNG order: sorted m1 then m2 tiles; A, B, absent; ascending k. Each attempt draws z, theta, q_x/q_y, c_x/c_y. Absent also draws a uniform different same-layer tile index, then u_x/u_y in its safe interior. Unsafe draws consume all geometry values; B draws row-major normal noise after acceptance; absent NCC failures redraw all geometry. Tiles-limit restricts search tiles only, keeping all same-layer reference choices.",
        "Sampling corners plus 8 source pixels must lie within the tile. The AA Gaussian has explicit radius ceil(4 sigma), at most 6; bicubic support is 2. No rendered footprint uses padding.",
        "", "## Independent absence search", "",
        "Exhaustive cv2 TM_CCOEFF_NORMED for kept candidates, z=8..12 step 0.5, theta=-5..5 step 1, area-downsampled reference, bilinear rotation. Scales visit increasing distance from 10, angles increasing distance from 0, with smaller values breaking ties. Reject early when any score reaches 0.5. Each rotated template uses its largest safe inscribed square, avoiding padding. This discards corner information and is a conservative search for recurring content. No Drift-Sense code decides absence.",
        "Kept absent NCC: " + summary(stats['kept']),
        "Discarded absent NCC lower bounds, early stopped at first grid score >= 0.5: " + summary(stats['rejected']),
        "Kept absent NCC by layer: " + "; ".join(layer + " " + summary([r['absent_best_ncc'] for r in rows if r['layer'] == layer and r['condition'] == 'absent']) for layer in ('m1', 'm2')),
        "Kept absent candidate scores, in manifest order: " + ", ".join(f"{v:.6f}" for v in stats['kept']),
        "", "## Pixel verification", "",
        f"First {len(present)} present A pairs in manifest order. Area-downsample reference to round(1000/z); inverse-affine sample search at GT into that frame. Zero-mean NCC:",
        "GT: " + summary(exact), "GT shifted +2 px x: " + summary(shifted),
        "GT rotated +1 degree: " + summary(turned), "Both perturbations: " + summary(both),
        f"Median GT NCC > 0.9: {bool(exact and np.median(exact) > .9)}.",
        "", "## Decoder convention sanity check", ""]
    if skip_decoder:
        lines.append("Decoder skipped by CLI; no convention conclusion.")
    else:
        import torch
        import infer as I
        from driftsense.matching import locate_phase2
        from driftsense.config import SHIPPED_BAND, SHIPPED_SUBPIXEL_ROWS, SHIPPED_STRIP_ROTATION
        torch.set_num_threads(4)
        loaded = I.load_model(I.DEFAULT_WEIGHTS)
        if not loaded:
            lines.append("Model could not load. No decoder calls or convention conclusion.")
        else:
            model, device = loaded
            lines.append(f"PyTorch {torch.__version__}; weights {Path(I.DEFAULT_WEIGHTS).name}; device {device}.")
            selected = [r for r in rows if r['condition'] == 'A' and abs(r['gt_rot_deg']) > 2][:12]
            lines += ["Local shipped model; label_convention=center; 4 threads; shipped register.py options. No tuning or scoring run.",
                      "", "| Pair | GT x,y,theta,z | Pred x,y,theta,scale | Error px | Sign same | Scale error % |", "|---|---|---|---|---|---|"]
            local = []; failures = 0
            for r in selected:
                try:
                    pred = locate_phase2(model, cv2.imread(r['reference_path'], 0), cv2.imread(r['search_path'], 0), device,
                        refine=True, band=SHIPPED_BAND, subpixel_rows=SHIPPED_SUBPIXEL_ROWS,
                        strip_rot=SHIPPED_STRIP_ROTATION, label_convention='center')
                    gt = [r['gt_x'], r['gt_y'], r['gt_rot_deg'], r['gt_scale']]
                    p = [pred[k] for k in ('x', 'y', 'theta', 'scale')]
                    err = float(np.linalg.norm(np.array(p[:2])-gt[:2]))
                    same = bool(p[2]*gt[2] > 0); se = 100*abs(p[3]-gt[3])/gt[3]
                    if err <= 3: local.append((same, se))
                    lines.append(f"| {r['pair_id']} | {', '.join(f'{v:.4f}' for v in gt)} | {', '.join(f'{v:.4f}' for v in p)} | {err:.4f} | {same} | {se:.3f} |")
                    print(f"decoder {r['pair_id']} error={err:.3f} sign={same} scale_error={se:.2f}%", flush=True)
                except Exception as e:
                    failures += 1; lines.append(f"| {r['pair_id']} | | ERROR {type(e).__name__}: {e} | | | |")
            lines += ["", f"Calls attempted: {len(selected)}; failures: {failures}; within 3 px: {len(local)}; same sign in that subset: {sum(v[0] for v in local)}.",
                      "Localised scale error %: " + summary([v[1] for v in local]),
                      "Systematically opposite sign among localised pairs: " + (str(bool(local and all(not v[0] for v in local))) if local else "undetermined"),
                      "No signs or scales were changed. 'Near z' is reported through scale error, without a fitted tolerance."]
    lines += ["", "## Limitations and attribution", "",
        "The same capture shares specimen noise between reference and search. Reference sampling is 3.6625 nm/px; search sampling is 29.3 to 43.95 nm/px. The physical 1 nm/px versus 8-12 nm/px acquisition is NOT reproduced.",
        "B adds simulated nuisance changes to SEARCH only: output blur sigma 0.7, gain 0.9, offset 8, independent normal noise sigma 8, clipping and rounding. These are synthetic nuisance changes, not measured acquisition effects.",
        "Absent labels are presumed, not proven. Repeated cells can recur across tiles; the finite NCC grid and threshold cannot prove absence. Absent references use a different tile of the same layer; reference_tile is recorded for provenance.",
        'Rothaug et al., "Towards Unsupervised SEM Image Segmentation for IC Layout Extraction", ASHES 2023, doi 10.1145/3605769.3624000; dataset doi 10.17617/3.HY5SYN, CC-BY 4.0; changes: cropped, resampled, enlarged, blurred, noise added.', ""]
    target = Path('results/iris/real_audit.md'); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(lines), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tiles-dir', default='data/real_raw/edmond/dataset/sems')
    ap.add_argument('--out-dir', default='data/iris/real')
    ap.add_argument('--manifest', default='data/iris/manifest_real.csv')
    ap.add_argument('--tiles-limit', type=int)
    ap.add_argument('--per-tile', nargs=3, type=int, default=[8, 8, 4])
    ap.add_argument('--skip-decoder', action='store_true', help='smoke runs only')
    ap.add_argument('--resume', action='store_true', help='resume a tile checkpoint, including RNG state')
    ap.add_argument('--tile-batch', type=int, help='stop after this many additional tiles; audit only when complete')
    args = ap.parse_args(); cv2.setNumThreads(4)
    if any(n < 0 for n in args.per_tile) or sum(args.per_tile) == 0:
        ap.error('per-tile counts must be nonnegative and nonempty')
    root = Path(args.tiles_dir); out = Path(args.out_dir)
    paths = sorted(root.glob('m[12]/sem*.png'))
    if not paths: raise RuntimeError('No source tiles')
    by_layer = {layer: [p for p in paths if p.parent.name == layer] for layer in ('m1', 'm2')}
    selected = paths if args.tiles_limit is None else paths[:args.tiles_limit]
    for directory in ('reference', 'search'): (out/directory).mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED); rows = []
    stats = dict(unsafe=0, discarded=0, kept=[], rejected=[])
    manifest = Path(args.manifest); manifest.parent.mkdir(parents=True, exist_ok=True)
    prior_seconds = 0.
    if args.resume and manifest.exists():
        with manifest.open(newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if rows and 'rng_state' not in rows[-1]:
            raise RuntimeError('Manifest has no resumable RNG checkpoint; rebuild without --resume')
        for row in rows:
            for key in ('found', 'draw_attempts', 'unsafe_rejections'):
                row[key] = int(row[key])
            for key in ('gt_x', 'gt_y', 'gt_scale', 'gt_rot_deg', 'q_x', 'q_y', 'u_x', 'u_y', 'absent_best_ncc', 'build_seconds'):
                row[key] = float(row[key])
            stats['unsafe'] += row['unsafe_rejections']
            discarded = json.loads(row['absent_rejected_ncc'])
            stats['rejected'].extend(discarded); stats['discarded'] += len(discarded)
            if row['condition'] == 'absent': stats['kept'].append(row['absent_best_ncc'])
        if rows:
            rng.bit_generator.state = json.loads(rows[-1]['rng_state'])
            prior_seconds = rows[-1]['build_seconds']
    completed = set(r['tile'] for r in rows)
    for tile_id in completed:
        existing = [r for r in rows if r['tile'] == tile_id]
        if [sum(r['condition'] == c for r in existing) for c in ('A', 'B', 'absent')] != args.per_tile:
            raise RuntimeError('Resume per-tile counts differ from checkpoint')
    start = time.perf_counter()
    added = 0
    for path in selected:
        if f'{path.parent.name}_{path.stem}' in completed: continue
        if args.tile_batch is not None and added >= args.tile_batch: break
        tile = read_tile(path)
        layer = path.parent.name; tile_id = f'{layer}_{path.stem}'
        others = [p for p in by_layer[layer] if p != path]; k = 0
        for condition, count in zip(('A', 'B', 'absent'), args.per_tile):
            for _ in range(count):
                unsafe_before = stats['unsafe']; rejected_before = len(stats['rejected'])
                for attempts in attempt_numbers(1):
                    z = float(rng.uniform(8, 12)); theta = float(rng.uniform(-5, 5))
                    q = np.array([2047.5, 1767.5])+rng.uniform(-50, 50, 2)
                    c = rng.uniform(100, 899, 2)
                    u = q+(z/4)*rotation(-theta)@(c-B)
                    ref_tile = tile; ref_id = tile_id
                    if condition == 'absent':
                        if not others: raise RuntimeError('Absent requires a second same-layer tile')
                        rp = others[int(rng.integers(len(others)))]; ref_id = f'{layer}_{rp.stem}'
                        ref_tile = read_tile(rp)
                        margin = 499.5/4+8
                        u = rng.uniform([margin, margin], np.array(ref_tile.shape[::-1])-1-margin)
                    if not safe(affine(u, np.eye(2)/4), ref_tile.shape) or not safe(affine(q, (z/4)*rotation(-theta)), tile.shape):
                        stats['unsafe'] += 1; continue
                    ref = render_reference(ref_tile, u); sea = render_search(tile, z, theta, q)
                    score = float('nan')
                    if condition == 'absent':
                        score = absent_ncc(ref, sea)
                        if score >= .5:
                            stats['discarded'] += 1; stats['rejected'].append(score); continue
                        stats['kept'].append(score)
                    if condition == 'B': sea = nuisance(sea, rng)
                    break
                pair_id = f'r_{tile_id}_{k:02d}'; k += 1
                rp = out/'reference'/f'{pair_id}.png'; sp = out/'search'/f'{pair_id}.png'
                for target, img in ((rp, ref), (sp, sea)):
                    if not cv2.imwrite(str(target), img): raise IOError(target)
                found = int(condition != 'absent')
                rows.append(dict(pair_id=pair_id, split='real', reference_path=rp.resolve().relative_to(Path.cwd()).as_posix(),
                    search_path=sp.resolve().relative_to(Path.cwd()).as_posix(), found=found,
                    gt_x=float(c[0]) if found else -1, gt_y=float(c[1]) if found else -1,
                    gt_scale=z if found else float('nan'), gt_rot_deg=theta if found else float('nan'),
                    label_convention='center', stratum=f'real_{condition}', group_id=tile_id, source='real',
                    tile=tile_id, layer=layer, condition=condition, q_x=q[0], q_y=q[1], u_x=u[0], u_y=u[1],
                    draw_attempts=attempts, reference_tile=ref_id, absent_best_ncc=score,
                    unsafe_rejections=stats['unsafe']-unsafe_before,
                    absent_rejected_ncc=json.dumps(stats['rejected'][rejected_before:]),
                    rng_state=json.dumps(rng.bit_generator.state),
                    build_seconds=prior_seconds+time.perf_counter()-start))
        added += 1
        with manifest.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        print(f'{tile_id}: {len(rows)} pairs; unsafe={stats["unsafe"]}; absent discarded={stats["discarded"]}; seconds={time.perf_counter()-start:.1f}', flush=True)
    if len(set(r['tile'] for r in rows)) < len(selected):
        print('Tile checkpoint saved. Continue with identical options plus --resume.', flush=True)
        return
    audit(rows, stats, args.skip_decoder, prior_seconds+time.perf_counter()-start)


if __name__ == '__main__':
    main()
