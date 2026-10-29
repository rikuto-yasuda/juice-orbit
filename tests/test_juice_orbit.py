import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

import juice_orbit
from juice_orbit import core


class OrbitToolsTest(unittest.TestCase):
    def test_load_relative_metakernel_from_elsewhere(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mk').mkdir()
            kernel = root / 'values.tpc'
            kernel.write_text('KPL/PCK\n\\begindata\nORBIT_TEST_VALUE = 42\n\\begintext\n')
            meta = root / 'mk/local.tm'
            meta.write_text("KPL/MK\n\\begindata\nPATH_VALUES = ( '..' )\nPATH_SYMBOLS = ( 'KERNELS' )\nKERNELS_TO_LOAD = ( '$KERNELS/values.tpc' )\n\\begintext\n")
            try:
                juice_orbit.load_kernels(meta)
                self.assertEqual(core.spice.gdpool('ORBIT_TEST_VALUE', 0, 1)[0], 42)
            finally:
                core.spice.kclear()

    def test_fractional_utc_preserved(self):
        self.assertEqual(core._as_utc_string('2032-01-01T00:00:00.5Z'),
                         '2032-01-01T00:00:00.500000Z')

    def test_make_times(self):
        result = juice_orbit.make_times("2031-01-01T00:00:00Z", "2031-01-02T00:00:00Z", 12, "hours")
        self.assertEqual(len(result), 3)

    def test_prepare_requires_absolute_data_dir(self):
        with self.assertRaises(ValueError):
            juice_orbit.prepare_juice("relative/JUICE", load=False)

    @patch.object(core, "load_kernels")
    @patch.object(core, "download_orbit_kernels")
    def test_prepare_downloads_missing_kernels(self, download, load):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "JUICE"
            expected_meta = root / "kernels/mk/juice_crema_5_2_orbit.tm"
            download.return_value = expected_meta
            workspace = juice_orbit.prepare_juice(root, results_subdir="result/test")
            self.assertEqual(workspace.results_dir, root.resolve() / "result/test")
            download.assert_called_once_with(root.resolve())
            load.assert_called_once_with(expected_meta)

    @patch.object(core.spice, "reclat", return_value=(5.0, 0.0, 0.0))
    @patch.object(core.spice, "spkezr", return_value=(np.array([3., 4., 0., 1., 2., 2.]), 0.0))
    @patch.object(core.spice, "str2et", return_value=0.0)
    def test_get_positions_full(self, *_):
        data = juice_orbit.get_positions("2031-01-01T00:00:00Z", targets="JUICE")
        self.assertEqual(data.loc[0, "target"], "JUICE")
        self.assertEqual(data.loc[0, "r_km"], 5.0)
        self.assertEqual(data.loc[0, "speed_km_s"], 3.0)

    def test_two_vector_axes_rates(self):
        def vectors(t):
            return (np.array([np.cos(t), np.sin(t), 0.3]),
                    np.array([-np.sin(t), np.cos(t), 0.1 * t]))

        t, h = 0.2, 1e-6
        primary, secondary = vectors(t)
        rates = (np.array([-np.sin(t), np.cos(t), 0.]), np.array([-np.cos(t), -np.sin(t), 0.1]))
        a, da, b, db = core._two_vector_axes(primary, rates[0], secondary, rates[1])
        self.assertAlmostEqual(a @ b, 0.0)
        self.assertAlmostEqual(np.linalg.norm(b), 1.0)
        after = core._two_vector_axes(*vectors(t + h)[:1], rates[0], vectors(t + h)[1], rates[1])
        before = core._two_vector_axes(*vectors(t - h)[:1], rates[0], vectors(t - h)[1], rates[1])
        np.testing.assert_allclose((after[0] - before[0]) / (2 * h), da, atol=1e-6)
        np.testing.assert_allclose((after[2] - before[2]) / (2 * h), db, atol=1e-6)

    def test_custom_frames_require_moon_observer(self):
        for frame in core.CUSTOM_FRAMES:
            with self.assertRaises(ValueError):
                juice_orbit.get_positions("2031-01-01T00:00:00Z", targets="JUICE",
                                          observer="JUPITER", frame=frame)

    def test_plot_orbits(self):
        data = pd.DataFrame({
            "utc": ["2031-01-01T00:00:00Z", "2031-01-02T00:00:00Z"],
            "target": ["JUICE", "JUICE"], "x_km": [0., 1.], "y_km": [0., 1.], "z_km": [0., 0.],
        })
        with tempfile.TemporaryDirectory() as directory:
            image = juice_orbit.plot_orbits(data, Path(directory) / "orbit.png")
            self.assertTrue(image.is_file())


if __name__ == "__main__":
    unittest.main()
