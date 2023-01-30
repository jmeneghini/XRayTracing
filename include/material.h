#ifndef MATERIAL_H
#define MATERIAL_H
#include "utility.h"

class material {
public:
    __device__ material() {}
    __device__ material(float mass_atten, float density) : mu_m(mass_atten), rho(density) {}

    __device__ virtual float transmission(float d) const {
        return exp(-mu_m * rho * d); // Beer-Lambert law
    }
public:
    float mu_m;
    float rho;
};



#endif //MATERIAL_H
