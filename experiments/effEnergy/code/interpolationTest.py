import numpy as np
import matplotlib.pyplot as plt
from material import Material

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer
from sklearn.pipeline import make_pipeline

# mass attenuation data for Al from NIST
mat = Material("Fe")
photon_energy_arr, mu_over_rho_arr = mat.get_mu_over_rho()

# train over all data
x_train = np.log10(photon_energy_arr)
y_train = np.log10(mu_over_rho_arr)

x_plot = np.linspace(np.log10(0.008), np.log10(0.1), 1000)

# test over a range of energies
X_train = x_train[:, np.newaxis]
X_plot = x_plot[:, np.newaxis]

# plot data points
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# plot data in log-log space
ax[0].plot(10**x_train, 10**y_train, "o", label="Data")
ax[0].set_xlabel("Photon Energy (keV)")
ax[0].set_ylabel("Mass Attenuation Coefficient (cm$^2$/g)")
ax[0].set_xscale("log")
ax[0].set_yscale("log")

# plot data in linear space
ax[1].plot(10**x_train, 10**y_train, "o", label="Data")
ax[1].set_xlabel("Photon Energy (keV)")
ax[1].set_ylabel("Mass Attenuation Coefficient (cm$^2$/g)")




# plot spline fit
model = make_pipeline(SplineTransformer(degree=2, n_knots=4), Ridge(alpha=1E-3))
model.fit(X_train, y_train)

y_plot = model.predict(X_plot)

# plot fit in log-log space
ax[0].plot(10**x_plot, 10**y_plot, label="Spline Fit, degree=2, n_knots=4")
ax[0].legend()

# plot fit in linear space
ax[1].plot(10**x_plot, 10**y_plot, label="Spline Fit, degree=2, n_knots=4")
ax[1].legend()

# make title
fig.suptitle("Mass Attenuation Coefficients of Al", fontsize=20)

#plt.savefig("experiments/effEnergy/experiment/spline_fit.png", dpi=300)




