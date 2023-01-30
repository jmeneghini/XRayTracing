#ifndef UTILITY_H
#define UTILITY_H

#include <cmath>
#include "thrust/limits.h"
#include "thrust/device_vector.h"
#include "thrust/host_vector.h"
#include "thrust/device_ptr.h"



// Usings

using thrust::device_ptr;
using thrust::device_vector;
using thrust::host_vector;
using std::sqrt;

// Constants

const double infinity = std::numeric_limits<double>::infinity();
const double pi = 3.1415926535897932385;

// Utility Functions

inline double degrees_to_radians(double degrees) {
    return degrees * pi / 180.0;
}

// Common Headers

#include "ray.h"
#include "vec3.h"
#endif //UTILITY_H
