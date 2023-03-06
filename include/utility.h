#ifndef UTILITY_H
#define UTILITY_H

#include <cmath>
#include <limits>
#include <memory>
#include <array>
#include <vector>
#include <string>


// Usings

using std::shared_ptr;
using std::make_shared;
using std::sqrt;
using std::array;
using std::string;
using std::vector;

// Constants

const double infinity = std::numeric_limits<double>::infinity();
const double pi = 3.1415926535897932385;

// Utility Functions

inline double degrees_to_radians(double degrees) {
    return degrees * pi / 180.0;
}

float interpolate(const std::vector<float>& x, const std::vector<float>& y, float x_val) {
    // find the index i such that x[i] <= x_val <= x[i+1]
    int i = 0;
    while (i < x.size() - 1 && x[i+1] < x_val) {
        i++;
    }

    // linear interpolation of y[i] and y[i+1] at x_val
    float x1 = x[i];
    float x2 = x[i+1];
    float y1 = y[i];
    float y2 = y[i+1];
    return y1 + (x_val - x1) * (y2 - y1) / (x2 - x1);
}

// Common Headers

#include "ray.h"
#include "vec3.h"
#endif //UTILITY_H
