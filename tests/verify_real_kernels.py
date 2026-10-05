"""Explicit real-kernel integration check; run with the installed package."""
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import spiceypy as spice
from juice_orbit import prepare_juice, make_times, get_positions, save_csv, plot_orbits


def main():
    root = Path(__file__).resolve().parents[1]
    workspace = prepare_juice(root / 'data/JUICE', results_subdir='output/verification')
    # Cached operation must not need network access, including a new process load.
    with patch('juice_orbit.core.urlopen', side_effect=AssertionError('unexpected network')):
        prepare_juice(workspace.data_dir)
    times = make_times('2032-01-01T00:00:00Z', '2032-01-02T00:00:00Z', 10, 'minutes')
    for observer in ['JUPITER', 'IO', 'EUROPA', 'GANYMEDE', 'CALLISTO']:
        targets = ['JUICE', 'IO', 'EUROPA', 'GANYMEDE', 'CALLISTO'] if observer == 'JUPITER' else ['JUICE', 'JUPITER']
        frame = 'IAU_' + observer
        data = get_positions(times, targets=targets, observer=observer, frame=frame)
        assert len(data) == len(times) * len(targets)
        xyz = data[['x_km', 'y_km', 'z_km']].to_numpy()
        assert np.isfinite(data.select_dtypes('number')).all().all()
        np.testing.assert_allclose(np.linalg.norm(xyz, axis=1), data.r_km)
        for mode in ['xyz', 'r_lat_lon']:
            compact = get_positions(times[0], targets=targets, observer=observer, frame=frame, output=mode)
            assert len(compact) == len(targets)
        # Frame transformation of an independently queried inertial state.
        et = spice.str2et(times[0])
        inertial, _ = spice.spkezr('JUICE', et, 'J2000', 'NONE', observer)
        expected = spice.sxform('J2000', frame, et) @ inertial
        np.testing.assert_allclose(data.iloc[0][['x_km','y_km','z_km','vx_km_s','vy_km_s','vz_km_s']].to_numpy(dtype=float), expected, atol=1e-7)
        # Central differences verify rotating-frame velocity, including subsecond times.
        nearby = get_positions(['2031-12-31T23:59:59.5Z', '2032-01-01T00:00:00.5Z'], targets=['JUICE'], observer=observer, frame=frame)
        delta = nearby[['x_km','y_km','z_km']].to_numpy()
        np.testing.assert_allclose(delta[1]-delta[0], expected[3:], rtol=1e-5, atol=1e-4)
        csv = save_csv(data, workspace.results_dir / (observer.lower() + '.csv'))
        pd.testing.assert_frame_equal(pd.read_csv(csv), data, check_exact=False)
        # Only JUICE is labelled in the figure to keep times readable.
        plot_orbits(data[data.target == 'JUICE'], workspace.results_dir / (observer.lower() + '.png'), time_markers=3, title=f'JUICE / {frame} / {observer} center')
        print(f'PASS {frame}: {len(data)} rows; CSV, PNG, frame transform, velocity')
    for moon in ['IO', 'EUROPA', 'GANYMEDE', 'CALLISTO']:
        custom_times = make_times('2035-06-01', '2035-06-01T06:00:00Z', 2, 'minutes')
        custom = get_positions(custom_times, targets=['JUICE', 'JUPITER'],
                               observer=moon, frame='JUPITER_FACING')
        iau = get_positions(custom_times, targets=['JUICE', 'JUPITER'],
                            observer=moon, frame='IAU_' + moon)
        np.testing.assert_allclose(custom.r_km, iau.r_km)
        np.testing.assert_allclose(custom.z_km, iau.z_km, atol=1e-9)
        jupiter = custom[custom.target == 'JUPITER']
        assert (jupiter.x_km > 0).all()
        np.testing.assert_allclose(jupiter.y_km, 0, atol=1e-8)
        from juice_orbit.core import _jupiter_facing_rotation
        et = spice.str2et(custom_times[0])
        state, _ = spice.spkezr('JUPITER', et, 'IAU_' + moon, 'NONE', moon)
        rotation, derivative = _jupiter_facing_rotation(state)
        np.testing.assert_allclose(rotation @ rotation.T, np.eye(3), atol=1e-14)
        np.testing.assert_allclose(np.linalg.det(rotation), 1, atol=1e-14)
        nearby = get_positions(['2035-05-31T23:59:59.5Z', '2035-06-01T00:00:00.5Z'],
                               targets=['JUICE'], observer=moon, frame='JUPITER_FACING')
        positions = nearby[['x_km','y_km','z_km']].to_numpy()
        np.testing.assert_allclose(positions[1]-positions[0],
                                   custom.iloc[0][['vx_km_s','vy_km_s','vz_km_s']].to_numpy(dtype=float),
                                   rtol=1e-4, atol=1e-4)
        save_csv(custom, workspace.results_dir / (moon.lower() + '_jupiter_facing.csv'))
        plot_orbits(custom[custom.target == 'JUICE'],
                    workspace.results_dir / (moon.lower() + '_jupiter_facing.png'),
                    time_markers=3, title=f'JUICE / {moon} center / Jupiter-facing (+X)')
        print(f'PASS {moon} JUPITER_FACING: axes, distances, velocities, CSV, PNG')
    coverage = spice.spkcov(str(workspace.data_dir / 'kernels/spk/juice_crema_5_2_v01.bsp'), -28)
    print('JUICE coverage:', [spice.et2utc(t, 'ISOC', 3) for t in coverage])
    try:
        get_positions('2040-01-01', targets=['JUICE'])
    except spice.utils.exceptions.SpiceSPKINSUFFDATA:
        print('PASS out-of-coverage request raises SPKINSUFFDATA')
    else:
        raise AssertionError('out-of-coverage date unexpectedly succeeded')
    print('Output:', workspace.results_dir)


if __name__ == '__main__':
    main()
