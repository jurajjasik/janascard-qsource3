import numpy as np
import matplotlib.pyplot as plt
from qsource3.massfilter import interp_fnc

# Define calibration points for mass
calib_pnts_dc = np.array([[100, 0.95], [200, 0.98], [300, 0.955], [400, 0.97]])

# Create the interpolation function using interp_fnc
interp_fnc_dc = interp_fnc(calib_pnts_dc)

# Generate denser data for smoother plot
mz_dense = np.linspace(calib_pnts_dc[:, 0].min(), calib_pnts_dc[:, 0].max(), 1000)

# Interpolate correction factors for denser data points
dc_correction_factor_dense = interp_fnc_dc(mz_dense)

# Plot calibration points and interpolated curve
plt.plot(calib_pnts_dc[:, 0], calib_pnts_dc[:, 1], 'o', label='Calibration Points')
plt.plot(mz_dense, dc_correction_factor_dense, '-', label='Interpolation')
plt.xlabel('m/z')
plt.ylabel('rho(m/z)')
plt.legend()
plt.grid(True)
plt.title('Resolution calibration function rho(m/z) (Interpolated)')
plt.show()
