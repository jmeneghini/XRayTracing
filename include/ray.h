#ifndef RAY_H
#define RAY_H

#include "vec3.h"

class ray {
public:
    ray() {}
    ray(const point3& origin, const vec3& direction)
        : orig(origin), dir(direction)
    {}

    point3 origin() const  { return orig; }  // ray origin
    vec3 direction() const { return dir; }  // ray direction

    point3 at(float t) const {
        return orig + t*dir; // ray equation
    }
public:
    point3 orig;
    vec3 dir;
};


#endif //RAY_H
