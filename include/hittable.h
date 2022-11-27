#ifndef HITTABLE_H
#define HITTABLE_H
#include "vector"
#include "ray.h"

struct hit_record {
    std::vector<point3> p;
    std::vector<float> t;
};

class hittable {
public:
    virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const = 0;
};

#endif //HITTABLE_H
