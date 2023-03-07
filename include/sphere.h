#ifndef SPHERE_H
#define SPHERE_H

#include "hittable.h"
#include "vec3.h"

class sphere : public hittable {
public:
    __device__ sphere() {}
    __device__ sphere(vec3 cen, float r, material* m) : center(cen), radius(r), mat_ptr(m) {};

    __device__ virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

public:
    vec3 center;
    float radius;
    material* mat_ptr;
};

__device__ bool sphere::hit(const ray &r, float t_min, float t_max, hit_record &rec) const {
    vec3 oc = r.origin() - center;
    auto a = r.direction().length_squared();
    auto half_b = dot(oc, r.direction());
    auto c = oc.length_squared() - radius * radius;

    auto discriminant = half_b * half_b - a * c;
    if (discriminant < 0) return false;
    auto sqrtd = sqrt(discriminant);

    // Find all roots that lie in the acceptable range.
    float dist;
    bool is_hit = false;
    auto root0 = (-half_b + sqrtd) / a;  // calculate both possible roots
    auto root1 = (-half_b - sqrtd) / a;
    if (root0 > t_min && t_max > root0) { // check if root0 is in the acceptable range
        rec.t.push_back(root0); // store root0
        rec.p.push_back(r.at(root0)); // store the point of root0
        dist = 0; // distance travelled through material is zero
        is_hit = true;
    };
    if (root1 > t_min && t_max > root1 && root1 != root0) { // check if root1 is in the acceptable range
        rec.t.push_back(root1); // store root1
        rec.p.push_back(r.at(root1)); // store the point of root1
        dist = r.diff(root0, root1); // calculate the distance travelled through material
        is_hit = true;
    };
    rec.trans_prob = mat_ptr->transmission(dist);  // calculate the transmission probability
    return is_hit;
};

#endif //SPHERE_H
