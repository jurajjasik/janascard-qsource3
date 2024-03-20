import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from qsource3.massfilter import interp_fnc

# Define calibration points for mass
calib_pnts_rf = np.array([[100, 0.95], [200, 0.98], [300, 0.955], [400, 0.97]])

# Create the interpolation function using interp_fnc
interp_fnc_rf = interp_fnc(calib_pnts_rf)

# Generate denser data for smoother plot
mz_dense = np.linspace(calib_pnts_rf[:, 0].min(), calib_pnts_rf[:, 0].max(), 100)

# Interpolate correction factors for denser data points
rf_correction_factor_dense = interp_fnc_rf(mz_dense)

# Plot calibration points and interpolated curve
plt.plot(calib_pnts_rf[:, 0], calib_pnts_rf[:, 1], 'o', label='Calibration Points')
plt.plot(mz_dense, rf_correction_factor_dense, '-', label='Interpolation')
plt.xlabel('m/z')
plt.ylabel('RF Correction Factor')
plt.legend()
plt.grid(True)
plt.title('Mass Calibration Curve (Interpolated)')
plt.show()
