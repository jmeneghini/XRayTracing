import numpy as np
import cv2
import os
import pandas as pd
from uncertainties import ufloat
import uncertainties.unumpy as unp
import spekpy as sp
from material import Material
from matplotlib import pyplot as plt
# use wayland backend
import matplotlib

# dictionary of materials and their thicknesses in cm
materials = {"Al": 0.2286, "Fe": 0.01, "Mg": 0.1, "Plastic Scintillator (Vinyltoluene-based)": 1.98, "Water, Liquid": 5.80}

'''array of air intensities for each kvp found by manually measuring 8 sections of the background of the 
scintillator images; reported value is the mean of the 8 sections. Source of error note: std is not reported for 
air intensities; sections were towards the center of the image. For large objects, the background intensity is 
not constant'''

air_intensities = np.array([[40, 84.63], [42, 105.90], [44, 146.76], [46, 201.16],
                            [48, 244.40], [50, 255], [52, 255], [54, 255], [56, 255], [58, 255], [60, 255]])
air_intensities[:, 1] = air_intensities[:, 1]/255 # normalize air intensities


def set_style():
    """Set matplotlib style."""
    """Could instead use a .mplstyle file, but that requires everyone to have it locally"""
    tex_fonts = {
        # Use LaTeX to write all text
        "text.usetex": True,
        "font.family": "serif",
        # Use 12pt font in plots, to match 12pt font in document
        "axes.labelsize": 12,
        "font.size": 12,
        # Make the legend/label fonts a little smaller
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }

    plt.rcParams.update(tex_fonts)

def set_size(width, fraction=1, subplots=(1, 1)):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float or string
            Document width in points, or string of predined document type
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    if width == 'default':
        width_pt = 469.75502
    else:
        width_pt = width

    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)


def get_relative_intensity(path, background_intensity=0):
    """
    Calculates the relative intensity of a square in the center of an image.
    :param path: Path to image
    :param background_intensity: Intensity of background
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
        return False

    # obtain relative intensity by normalizing by background intensity (I_square = I_background * I_object -> I_object = I_square / I_background)
    mean[0][0] = mean[0][0] / background_intensity


    # convert image to rgb
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # draw red square on image and relative intensity and std on image
    cv2.rectangle(img, (int(center[0]-length/2), int(center[1]-length/2)), (int(center[0]+length/2), int(center[1]+length/2)), (0, 0, 255), 3)
    cv2.putText(img, f"Intensity: {mean[0][0]:.3f} +- {std[0][0]:.3f}", (int(center[0]-length/2), int(center[1]-length/2)-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # save image
    #path_split = path.split("/")
    #cv2.imwrite(f"{path_split[0]}/{path_split[1]}Processed/{path_split[2]}/{path_split[3][:-4]}_Processed.png", img*255)

    return ufloat(mean[0][0], std[0][0])

def get_eff_energy(material, thickness, intensity):
    """
    Calculates the effective energy of a material given the thickness, intensity, and intensity standard deviation.
    :param material: Material object
    :param thickness: Thickness of material
    :param intensity: Relative intensity ufloat/unumpy object
    :return: Effective energy of material
    """
    # calculate mu_over_rho
    mu_over_rho_u = unp.log(1/intensity) / (thickness*material.rho)

    # calculate effective energy
    eff_energy, eff_energy_min, eff_energy_max = material.get_eff_energy_from_mu_over_rho(mu_over_rho_u)

    return eff_energy, [eff_energy_max - eff_energy, eff_energy - eff_energy_min]

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

def export_data(material, kvps, intensities, intensity_stds, eff_energies, eff_energy_ranges):
    """
    Exports data to csv file.
    :param material: Material object
    :param kvps: List of kvps
    :param intensities: List of intensities
    :param intensity_stds: List of intensity standard deviations
    :param eff_energies: List of effective energies
    :param eff_energy_ranges: List of effective energy ranges
    :return: None
    """
    # create dataframe
    df = pd.DataFrame({"kVp (keV)": kvps, "Relative Intensity": intensities, "Relative Intensity Standard Deviation": intensity_stds, "Effective Energy (keV)": eff_energies*1E3,
                       "Effective Energy Max (keV)": (eff_energies + eff_energy_ranges[:, 0])*1E3, "Effective Energy Min (keV)": (eff_energies - eff_energy_ranges[:, 1])*1E3})

    # round and cut off values at 3 decimal places
    df = df.round(3)

    # export to csv
    df.to_latex(f"xrays/effEnergyImagingSessionProcessed/{material}/{material}_table.tex", index = False, escape = False, column_format='cccccc')



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
    eff_energy_ranges_dict = {}

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
        eff_energy_ranges = []

        # loop through files
        for file in files:
            # get kvp from file name
            kvp = get_kvp_from_file_name(file)

            # get air intensity
            air_intensity = air_intensities[np.where(air_intensities[:, 0] == kvp)][0][1]

            # get relative intensity and intensity std
            intensity_u = get_relative_intensity(folder + "/" + directory + "/" + file, air_intensity)
            # if intensity is false, skip file
            if not intensity_u:
                continue

            # get effective energy
            eff_energy, eff_energy_range = get_eff_energy(material, thickness, intensity_u)
            # if effective energy is 0.1, then the energy is above the spline range, so skip
            if eff_energy == 1E-1:
                continue

            # append to lists
            kvps.append(kvp)
            intensities.append(intensity_u.n)
            intensity_stds.append(intensity_u.s)
            eff_energies.append(eff_energy)
            eff_energy_ranges.append(eff_energy_range)

        # add lists to dictionaries and sort
        kvps_dict[directory] = np.sort(np.array(kvps))

        intensities = np.array(intensities)
        p = intensities.argsort()
        intensities_dict[directory] = intensities[p]

        intensity_stds = np.array(intensity_stds)
        intensity_stds_dict[directory] = intensity_stds[p]

        eff_energies = np.array(eff_energies)
        p = eff_energies.argsort()
        eff_energies_dict[directory] = eff_energies[p]

        eff_energy_ranges = np.array(eff_energy_ranges)
        eff_energy_ranges_dict[directory] = eff_energy_ranges[p]


    # plot effective energies
    markers = ["o", "v", "^", "*", "x"]
    plt.figure(figsize = set_size("default", fraction = 1))
    for material in materials:
        plt.errorbar(kvps_dict[material], eff_energies_dict[material]*1E3, yerr = eff_energy_ranges_dict[material].T*1E2, label=material, marker=markers.pop(0),
                     linestyle="None", capsize=3, capthick=1, elinewidth=1, markersize=3)
        export_data(material, kvps_dict[material], intensities_dict[material], intensity_stds_dict[material], eff_energies_dict[material], eff_energy_ranges_dict[material])

    plt.xlabel("kVp (keV)")
    plt.ylabel("Effective Energy (keV)")
    plt.legend()
    plt.savefig("experiments/effEnergy/experiment/effEnergy.pdf")

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
    set_style()
    main()




