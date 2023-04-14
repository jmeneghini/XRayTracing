import numpy as np
import cv2
import os
import spekpy as sp
from material import Material
from matplotlib import pyplot as plt
# use wayland backend
import matplotlib
matplotlib.use('TkAgg')

# dictionary of materials and their thicknesses in cm
materials = {"Al": 0.2286, "Fe": 0.01, "Mg": 0.1, "Plastic Scintillator (Vinyltoluene-based)": 1.98, "Water, Liquid": 5.80}

'''array of air intensities for each kvp found by manually measuring 8 sections of the background of the 
scintillator images; reported value is the mean of the 8 sections. Source of error note: std is not reported for 
air intensities; sections were towards the center of the image. For large objects, the background intensity is 
not constant'''

air_intensities = np.array([[40, 84.63], [42, 105.90], [44, 146.76], [46, 201.16],
                            [48, 244.40], [50, 255], [52, 255], [54, 255], [56, 255], [58, 255], [60, 255]])
air_intensities[:, 1] = air_intensities[:, 1]/255 # normalize air intensities


def get_relative_intensity(path, backround_intensity=0):
    """
    Calculates the relative intensity of a square in the center of an image.
    :param path: Path to image
    :param backround_intensity: Intensity of background
    :return: Relative intensity
    """
    # load image
    img = cv2.imread(path, 0)

    # convert to float and normalize
    img = img.astype(np.float32)/255

    # get mean pixel value and std dev of square in center of image
    center = (int(img.shape[0]/2), int(img.shape[1]/2))
    length = 100
    square = img[int(center[0]-length/2):int(center[0]+length/2), int(center[1]-length/2):int(center[1]+length/2)]
    mean, std = cv2.meanStdDev(square)

    # if intensity is 1 or 0, return False, so they are not used as data points
    if mean[0][0] >= 0.999 or mean[0][0] <= 0.001:
        return False, False

    # obtain relative intensity by normalizing by background intensity (I_square = I_background * I_object -> I_object = I_square / I_background)
    mean[0][0] = mean[0][0] / backround_intensity


    # convert image to rgb
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # draw red square on image and relative intensity and std on image
    cv2.rectangle(img, (int(center[0]-length/2), int(center[1]-length/2)), (int(center[0]+length/2), int(center[1]+length/2)), (0, 0, 255), 3)
    cv2.putText(img, f"Intensity: {mean[0][0]:.3f} +- {std[0][0]:.3f}", (int(center[0]-length/2), int(center[1]-length/2)-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # save image
    #path_split = path.split("/")
    #cv2.imwrite(f"{path_split[0]}/{path_split[1]}Processed/{path_split[2]}/{path_split[3][:-4]}_Processed.png", img*255)

    return mean[0][0], std[0][0]

def get_eff_energy(material, thickness, intensity):
    """
    Calculates the effective energy of a material given the thickness, intensity, and intensity standard deviation.
    :param material: Material object
    :param thickness: Thickness of material
    :param intensity: Relative intensity
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
            # if effective energy is 0.1, then the energy is above the spline range, so skip
            if eff_energy == 1E-1:
                continue

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
    markers = ["o", "v", "^", "*", "x"]
    for material in materials:
        plt.scatter(kvps_dict[material], eff_energies_dict[material]*1E2, label=material, marker=markers.pop(0))
    plt.xlabel("kVp (keV)")
    plt.ylabel("Effective Energy (keV)")
    plt.legend()
    plt.show()

def offsetTest():
    alCenter = "xrays/effEnergyImagingSession/Al/Al-N-40kvp.png"

    air40 = air_intensities[np.where(air_intensities[:, 0] == 40)][0][1]
    alCenterIntensity, alCenterIntensityStd = get_relative_intensity(alCenter, air40)
    alOffsetIntensity, alOffsetIntensityStd = ((12.10/255)/air40, 0.047) # manually calculated with ImageJ

    alCenterEffEnergy = get_eff_energy(Material("Al"), materials["Al"], alCenterIntensity)
    alOffsetEffEnergy = get_eff_energy(Material("Al"), materials["Al"], alOffsetIntensity)

    print(f"Center: Effective Energy = {alCenterEffEnergy*1E2} keV, Intensity = {alCenterIntensity}")
    print(f"Offset: Effective Energy = {alOffsetEffEnergy*1E2} keV, Intensity = {alOffsetIntensity}")


def varyThicknessTest():
    alN = "xrays/effEnergyImagingSession/Al/Al-N-40kvp.png"
    alI = "xrays/otherTests/Al-I-40kvp.png"

    air40 = air_intensities[np.where(air_intensities[:, 0] == 40)][0][1]
    alNIntensity, alNIntensityStd = get_relative_intensity(alN, air40)
    alIIntensity, alIIntensityStd = get_relative_intensity(alI, air40)

    alNEffEnergy = get_eff_energy(Material("Al"), materials["Al"], alNIntensity)
    alIEffEnergy = get_eff_energy(Material("Al"), 0.08128, alIIntensity)

    print(f"Al-N: Effective Energy = {alNEffEnergy*1E2} keV, Intensity = {alNIntensity}")
    print(f"Al-I: Effective Energy = {alIEffEnergy*1E2} keV, Intensity = {alIIntensity}")

if __name__ == "__main__":
    main()




