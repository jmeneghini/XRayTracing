import numpy as np
import json
import os

from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import max_error
from matplotlib import pyplot as plt


class Material:
    def __init__(self, mat_name):
        self.rho = None
        self.name = mat_name
        self.composition = []
        self.extract_composition()

    def extract_composition(self):
        comp_file = os.path.join("materials", "mat_def", f"{self.name}.comp")
        with open(comp_file, "r") as file:
            contents = file.read()

        if not contents:
            print(f"File {comp_file} is empty")
            exit(1)

        j = json.loads(contents)

        self.rho = j["composition"]["density"]

        for element in j["composition"]["elements"]:
            e = self.ElementalContribution()
            e.atomicNumber = element[0]
            e.fractionWeight = element[1]
            self.composition.append(e)


    def get_mu_over_rho(self):
        mu_data_file = "/home/john/XRayTracing/materials/nist_mu.dat"
        with open(mu_data_file, "r") as file:
            j = json.load(file)

        material_mu_over_rho = []
        for e in self.composition:
            atomic_number = e.atomicNumber
            fraction_weight = e.fractionWeight

            element_index = atomic_number - 1
            photon_energy_arr = np.array(j["photon energy"][element_index])
            mu_over_rho_arr = np.array(j["mu_over_rho"][element_index])

            # truncate both arrays from 8E-3 kev to 1E-1 kev
            photon_energy_arr_trunc = photon_energy_arr[np.logical_and(8E-3 <= photon_energy_arr, photon_energy_arr <= 1E-1)]
            mu_over_rho_arr_trunc = mu_over_rho_arr[np.logical_and(8E-3 <= photon_energy_arr, photon_energy_arr <= 1E-1)]

            material_mu_over_rho.append(mu_over_rho_arr_trunc * fraction_weight)

        material_mu_over_rho = np.sum(material_mu_over_rho, axis=0)

        return photon_energy_arr_trunc, material_mu_over_rho

    def get_mu_over_rho_from_eff_energy(self, eff_energy):
        photon_energy_arr, mu_over_rho_arr = self.get_mu_over_rho()
        # train over all data
        x_train = np.log10(photon_energy_arr)
        y_train = np.log10(mu_over_rho_arr)
        X_train = x_train[:, np.newaxis]

        # make spline fit
        model = make_pipeline(SplineTransformer(degree=2, n_knots=4), Ridge(alpha=1E-3))
        model.fit(X_train, y_train)
        predicted_mu_over_rho = 10**model.predict(np.log10(eff_energy[:, np.newaxis]))


        # get error
        y_pred = model.predict(X_train)
        y_pred = 10**y_pred
        y_train = 10**y_train
        error = max_error(y_train, y_pred)


        return predicted_mu_over_rho, error

    def get_eff_energy_from_mu_over_rho(self, mu_over_rho_u):
        range = np.linspace(8E-3, 1E-1, 10000)

        predicted_mu_over_rho, error = self.get_mu_over_rho_from_eff_energy(range)

        # find the index of the closest value in predicted_mu_over_rho to mu_over_rho (max and min to obtain a range)
        max_index = np.argmin(np.abs(predicted_mu_over_rho - (mu_over_rho_u.n  + mu_over_rho_u.s)))
        min_index = np.argmin(np.abs(predicted_mu_over_rho - (mu_over_rho_u.n - mu_over_rho_u.s)))
        index = np.argmin(np.abs(predicted_mu_over_rho - mu_over_rho_u.n))

        return range[index], range[max_index], range[min_index]


    class ElementalContribution:
        def __init__(self):
            self.atomicNumber = 0
            self.fractionWeight = 0.0
