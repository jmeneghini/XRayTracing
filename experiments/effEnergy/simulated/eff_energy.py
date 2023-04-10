import spekpy as sp
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("science")

# set xray source parameters
ang = 14
filt = 2.5 # mm Al
z_dist = 44.95 # cm



s_50 = sp.Spek(kvp = 50, th = ang, z = z_dist)
s_50.filter('Al', filt)

s_80 = sp.Spek(kvp = 80, th = ang, z = z_dist)
s_80.filter('Al', filt)


# generate energy spectrum
E_50_spec = s_50.get_spectrum()

E_80_spec = s_80.get_spectrum()

eff_E_50 = s_50.get_eeff()
eff_E_80 = s_80.get_eeff()

# drawing delta function at effective energy
dE = 0.001
eff_E_50_arr = np.array([eff_E_50 - dE, eff_E_50, eff_E_50 + dE])
eff_E_80_arr = np.array([eff_E_80 - dE, eff_E_80, eff_E_80 + dE])



# plot effective energy spectrum
fig, ax = plt.subplots(figsize = (11, 6))
ax.plot(E_50_spec[0], E_50_spec[1], label = '50 kVp, Effective Energy = {:.2f} keV'.format(eff_E_50), color = 'blue')
ax.plot(E_80_spec[0], E_80_spec[1], label = '80 kVp, Effective Energy = {:.2f} keV'.format(eff_E_80), color = 'green')
ax.plot(eff_E_50_arr, [0, 1E8, 0], color = 'blue', linestyle = '--', dashes = (5, 8))
ax.plot(eff_E_80_arr, [0, 1E8, 0], color = 'green', linestyle = '--', dashes = (5, 8))
ax.set_xlabel('Energy (keV)', fontsize = 22)
ax.set_ylabel('Intensity (a.u.)', fontsize = 22)
ax.legend(fontsize = 16)
ax.set_xlim(0, 90)
ax.set_ylim(0, 2.65E7)
ax.tick_params(axis = 'both', which = 'major', labelsize = 18)

plt.savefig('../docs/xray_energy_spectrum.png', dpi = 300)
plt.show()






