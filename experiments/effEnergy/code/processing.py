import numpy as np
import cv2
import os
import spekpy as sp
import json
from material import Material
from matplotlib import pyplot as plt
# use wayland backend
import matplotlib
matplotlib.use('TkAgg')


def get_relative_intensity(path, backround_intensity=0):
    """
    Calculates the relative intensity of a square in the center of an image.
    :param path: Path to image
    :return: Relative intensity
    """
    # load image
    img = cv2.imread(path, 0)
    # convert to float and normalize
    img = img.astype(np.float32)/255
    # invert image
    img = 1 - img
    # get mean pixel value and std dev of square
    center = (int(img.shape[0]/2), int(img.shape[1]/2))
    length = 100
    square = img[int(center[0]-length/2):int(center[0]+length/2), int(center[1]-length/2):int(center[1]+length/2)]
    mean, std = cv2.meanStdDev(square)

    # if intensity is 1, return False
    if mean[0][0] >= 0.999:
        return False, False
    # subtract background intensity
    mean -= backround_intensity
    if mean < 0:
        mean = 0

    # convert image to rgb
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    # draw red square on image and relative intensity and std on image
    cv2.rectangle(img, (int(center[0]-length/2), int(center[1]-length/2)), (int(center[0]+length/2), int(center[1]+length/2)), (0, 0, 255), 3)
    cv2.putText(img, f"Intensity: {mean[0][0]:.3f} +- {std[0][0]:.3f}", (int(center[0]-length/2), int(center[1]-length/2)-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # save image
    cv2.imwrite(path[:-4] + "_Processed.png", img*255)

    return mean[0][0], std[0][0]

def get_eff_energy(material, thickness, intensity):
    """
    Calculates the effective energy of a material given the thickness, intensity, and intensity standard deviation.
    :param material: Material object
    :param thickness: Thickness of material
    :param intensity: Relative intensity of material
    :param intensity_std: Standard deviation of relative intensity
    :return: Effective energy of material
    """
    # calculate mu_over_rho
    mu_over_rho = np.log(1/intensity) / (thickness*material.rho)

    # calculate effective energy
    eff_energy = material.get_eff_energy_from_mu_over_rho(mu_over_rho)

    return eff_energy

def get_kvp_from_file_name(file_name):
    """
    Gets the KVP from the file name
    :param file_name: File name
    :return: KVP
    """
    # split file name by kvp
    split = file_name.split("kvp")
    # return kvp
    return float(split[0][-2:])



def main():
    # dictionary of materials and their thicknesses in cm
    materials = {"Al": 0.2286, "Fe": 0.01, "Mg": 0.1, "Plastic Scintillator (Vinyltoluene-based)": 1.98*2, "Water, Liquid": 5.80}

    # array of air intensities for each kvp found by manually measuring 8 sections of the background of the scintillator images; reported value is the mean of the 8 sections
    # error note: std is not reported for air intensities; section were towards the center of the image. For large objects, the background intensity is not constant
    air_intensities = np.array([[40, 84.63], [42, 105.90], [44, 146.76], [46, 201.16], [48, 244.40], [50, 255], [52, 255], [54, 255], [56, 255], [58, 255], [60, 255]])
    air_intensities[:, 1] = 1 - air_intensities[:, 1]/255 # normalize air intensities and invert


    # get directory of images
    folder = "xrays/effEnergyImagingSession"
    # get directories in folder
    directories = os.listdir(folder)
    # initialize dictionaries of kvp, intensity, intensity std, and effective energy lists for each material
    kvps_dict = {}
    intensities_dict = {}
    intensity_stds_dict = {}
    eff_energies_dict = {}

    # loop through directories
    for directory in directories:
        # get files in directory
        files = os.listdir(folder + "/" + directory)
        # get material
        material = Material(directory)
        # get thickness
        thickness = materials[directory]
        # initialize list of kvp, intensity, intensity std, and effective energy
        kvps = []
        intensities = []
        intensity_stds = []
        eff_energies = []
        # loop through files
        for file in files:
            if "_Processed" in file:
                continue
            # get kvp from file name
            kvp = get_kvp_from_file_name(file)
            # get air intensity
            air_intensity = air_intensities[np.where(air_intensities[:, 0] == kvp)][0][1]
            # get relative intensity
            intensity, intensity_std = get_relative_intensity(folder + "/" + directory + "/" + file, air_intensity)
            # if intensity is false, skip file
            if not intensity:
                continue
            # get effective energy
            eff_energy = get_eff_energy(material, thickness, intensity)
            # append to lists
            kvps.append(kvp)
            intensities.append(intensity)
            intensity_stds.append(intensity_std)
            eff_energies.append(eff_energy)
        # add lists to dictionaries and sort
        kvps_dict[directory] = np.sort(np.array(kvps))

        intensities = np.array(intensities)
        p = intensities.argsort()
        intensities = np.flip(intensities[p])
        intensities_dict[directory] = intensities

        intensity_stds = np.array(intensity_stds)
        intensity_stds_dict[directory] = np.flip(intensity_stds[p])

        eff_energies_dict[directory] = np.sort(np.array(eff_energies))

    # plot effective energies
    for material in materials:
        if material != "Water, Liquid":
            plt.scatter(kvps_dict[material], eff_energies_dict[material], label=material)
    plt.xlabel("KVP")
    plt.ylabel("Effective Energy (MeV)")
    plt.legend()
    plt.show()







if __name__ == "__main__":
    main()




