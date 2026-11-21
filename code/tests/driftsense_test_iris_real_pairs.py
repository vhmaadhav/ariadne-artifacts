"""Independent geometric checks for the real SEM renderer."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location('iris_real', Path(__file__).resolve().parents[1]/'scripts/iris_make_real.py')
real = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real)


class RealGeometry(unittest.TestCase):
    def test_source_positions_and_affines(self):
        rng = np.random.default_rng(20261010)
        maximum = 0.
        for _ in range(100):
            z = rng.uniform(8, 12); theta = rng.uniform(-5, 5)
            c = rng.uniform(100, 899, 2); q = rng.uniform(1600, 2200, 2)
            # Independent Q construction, not the renderer's helper.
            t = np.deg2rad(theta)
            Q = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
            u = q+(z/4)*Q.T@(c-real.B)
            pixels = np.vstack(([0, 0], [999, 999], real.B, rng.uniform(0, 999, (20, 2))))
            landed = c+(pixels-real.B)@Q.T/z
            ref_source = u+(pixels-real.B)/4
            search_source = q+(z/4)*(landed-real.B)@Q
            err = np.max(np.abs(ref_source-search_source)); maximum = max(maximum, err)
            self.assertLess(err, 1e-9)
            mr = real.affine(u, np.eye(2)/4); ms = real.affine(q, (z/4)*real.rotation(-theta))
            np.testing.assert_allclose(pixels@mr[:, :2].T+mr[:, 2], ref_source, atol=1e-9, rtol=0)
            np.testing.assert_allclose(landed@ms[:, :2].T+ms[:, 2], ref_source, atol=1e-9, rtol=0)
        print(f'Algebra maximum source-coordinate discrepancy: {maximum:.3g} px')

    def test_footprint_filter_support(self):
        self.assertTrue(real.safe(real.affine([499.5, 499.5], np.eye(2)/4), (1000, 1000)))
        self.assertFalse(real.safe(real.affine([130, 130], np.eye(2)/4), (1000, 1000)))

    def test_opencv_integer_pixel_centres(self):
        # A source ramp exposes a half-pixel convention error. Select integer
        # source samples to avoid testing bicubic's fractional kernel shape.
        y, x = np.mgrid[:1000, :1000]
        tile = (2*x+3*y).astype(np.float32)
        u = np.array([400., 500.])+real.B/4
        ref = real.render_reference(tile, u)
        for j in (0, 4, 500, 996):
            for i in (0, 4, 500, 996):
                self.assertAlmostEqual(float(ref[j, i]), 2*(400+i/4)+3*(500+j/4), places=4)


if __name__ == '__main__':
    unittest.main()
