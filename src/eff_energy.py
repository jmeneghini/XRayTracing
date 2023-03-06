import spekpy as sp
import numpy as np
import matplotlib.pyplot as plt

# set xray source parameters
ang = 14
filt = 2.5 # mm Al
z_dist = 44.95 # cm

# generate effective energy spectrum

eff_E_arr = []
avg_E_arr = []

for kvp in np.arange(30, 80, 1):
    s = sp.Spek(kvp = kvp, th = ang, z = z_dist)
    s.filter('Al', filt)
    eff_E = s.get_eeff()
    eff_E_arr.append(eff_E)
    avg_E = s.get_emean()
    avg_E_arr.append(avg_E)


eff_E_arr = np.array(eff_E_arr)
avg_E_arr = np.array(avg_E_arr)
print(eff_E_arr[np.arange(30, 80, 1) == 50]) # 50 kVp
# plot effective energy
plt.plot(np.arange(30, 80, 1), eff_E_arr, label = 'Effective Energy')
plt.plot(np.arange(30, 80, 1), avg_E_arr, label = 'Average Energy')
plt.xlabel("kVp (keV)")
plt.ylabel("Energy (keV)")
plt.legend()
plt.show()

