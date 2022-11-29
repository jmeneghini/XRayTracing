#ifndef RAY_H
#define RAY_H

#include "vec3.h"

class ray {
public:
    ray() {}
    ray(const vec3& origin, const vec3& direction)
        : orig(origin), dir(direction)
    {}

    vec3 origin() const  { return orig; }  // ray origin
    vec3 direction() const { return dir; }  // ray direction

    vec3 at(float t) const {
        return orig + t*dir; // ray equation
    }

    float diff(float t1, float t2) const {
        return std::abs(t1 - t2)*dir.length(); // distance between two points on ray
    }
public:
    vec3 orig;
    vec3 dir;
};


#endif //RAY_H
