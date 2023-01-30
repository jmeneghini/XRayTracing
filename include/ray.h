#ifndef RAY_H
#define RAY_H

#include "vec3.h"

class ray {
public:
    __device__ ray() {}
    __device__ ray(const vec3& origin, const vec3& direction)
        : orig(origin), dir(direction)
    {}

    __device__ vec3 origin() const  { return orig; }  // ray origin
    __device__ vec3 direction() const { return dir; }  // ray direction

    __device__ vec3 at(float t) const {
        return orig + t*dir; // ray equation
    }

    __device__ float diff(float t1, float t2) const {
        return std::abs(t1 - t2)*dir.length(); // distance between two points on ray
    }
public:
    vec3 orig;
    vec3 dir;
};


#endif //RAY_H
