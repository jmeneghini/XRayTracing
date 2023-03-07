#ifndef MATERIAL_H
#define MATERIAL_H
#include "utility.h"
#include "json.h"


using nlohmann::json;

class material {
public:
    __host__ material(const char *matName, const float effectiveEnergy) :
            name(matName),
            energy(effectiveEnergy / 1E3),
            composition(),
            mu_m(0.0f) {
        extractComposition();
        findMassAttenuationCoefficient();
    }


    __device__ float transmission(float d) const {
        return exp(-mu_m * rho * d);
    }


private:
    struct ElementalContribution {
        int atomicNumber;
        float fractionWeight;
    };

    std::string name;
    float energy;
    std::vector<ElementalContribution> composition;
    float mu_m;
    float rho;


    __host__ void extractComposition() {
        std::string compFile = std::string("materials/mat_def/") + name + ".comp";  // find the composition file
        std::ifstream file(compFile);
        if (!file) {
            std::cerr << "Error opening file " << compFile << std::endl;
            exit(1);
        }

        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string contents = buffer.str();

        if (contents.empty()) {
            std::cerr << "File " << compFile << " is empty" << std::endl;
            exit(1);
        }

        json j;
        try {
            j = json::parse(contents);
        } catch (json::parse_error& e) {
            std::cerr << "Failed to parse file " << compFile << ": " << e.what() << std::endl;
            exit(1);
        }

        rho = j["composition"]["density"];

        for (auto &element: j["composition"]["elements"]) {
            ElementalContribution e;
            e.atomicNumber = element[0];
            e.fractionWeight = element[1];
            composition.push_back(e);
        }
    }

    __host__ void findMassAttenuationCoefficient() {
        std::ifstream file("/home/john/XRayTracing/materials/nist_mu.dat");
        json j;
        file >> j;

        mu_m = 0;
        // loop over all elements in composition
        for (auto &e: composition) {
            int atomicNumber = e.atomicNumber;
            float fractionWeight = e.fractionWeight;

            // find the mass attenuation coefficient for the current element
            int elementIndex = atomicNumber - 1;
            std::vector<float> photonEnergy = j["photon energy"][elementIndex];
            std::vector<float> mu_over_rho = j["mu_over_rho"][elementIndex];

            // interpolate the mass attenuation coefficient at the effective energy
            float mu_m_i = interpolate(photonEnergy, mu_over_rho, energy);

            // Add the contribution of the current element to the total mass attenuation coefficient
            mu_m += mu_m_i * fractionWeight;
        }
        std::cout << "<Mass Attenuation Coefficient>" << std::endl;
        std::cout << name << ": Effective Energy = " << energy*1E3<< " keV, mu/rho = " << mu_m << " cm^2/g" << ", rho = " << rho << " g/cm^2\n" << std::endl;
    }
};



#endif //MATERIAL_H
