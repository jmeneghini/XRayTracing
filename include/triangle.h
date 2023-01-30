#ifndef TRIANGLE_H
#define TRIANGLE_H

#include "hittable.h"
#include "vec3.h"
#include "utility.h"

class triangle : public hittable {
public:
    __device__ triangle() {}
    __device__ triangle(vec3 v0, vec3 v1, vec3 v2, device_ptr<material> m) : v0(v0), v1(v1), v2(v2), mat_ptr(m) {};

    __device__ virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

public:
    vec3 v0;
    vec3 v1;
    vec3 v2;
    device_ptr<material> mat_ptr;
};

__device__ bool triangle::hit(const ray &r, float t_min, float t_max, hit_record &rec) const {
    float kEpsilon = 0.0000001;

    vec3 e1 = v1 - v0;
    vec3 e2 = v2 - v0;
    vec3 pvec = cross(r.direction(), e2);
    float det = dot(e1, pvec);

    if (std::abs(det) < kEpsilon) return false;  // ray is parallel to triangle

    float inv_det = 1.0 / det;

    vec3 tvec = r.origin() - v0;
    float u = dot(tvec, pvec) * inv_det;
    if (u < 0.0 || u > 1.0) return false; // hit point is outside of triangle

    vec3 qvec = cross(tvec, e1);
    float v = dot(r.direction(), qvec) * inv_det;
    if (v < 0.0 || u + v > 1.0) return false; // hit point is outside of triangle

    float t = dot(e2, qvec) * inv_det;
    if (t < t_min || t > t_max) return false; // hit point is outside of ray

    rec.t.push_back(t);
    rec.p.push_back(r.at(t));

    return true;
}
#endif //TRIANGLE_H
