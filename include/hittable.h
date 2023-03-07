#ifndef HITTABLE_H
#define HITTABLE_H
#include "vector"
#include "ray.h"
#include "material.h"
#include "utility.h"

struct hit_record {
    thrust::device_vector<vec3> p;
    thrust::device_vector<float> t;
    float trans_prob;
};

class hittable {
public:
    __device__ virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const = 0;
};

#endif //HITTABLE_H
