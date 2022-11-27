#ifndef SPHERE_H
#define SPHERE_H

#include "hittable.h"
#include "vec3.h"

class sphere : public hittable {
public:
    sphere() {}
    sphere(point3 cen, float r) : center(cen), radius(r) {};

    virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

public:
    point3 center;
    float radius;
};

bool sphere::hit(const ray &r, float t_min, float t_max, hit_record &rec) const {
    vec3 oc = r.origin() - center;
    auto a = r.direction().length_squared();
    auto half_b = dot(oc, r.direction());
    auto c = oc.length_squared() - radius * radius;

    auto discriminant = half_b * half_b - a * c;
    if (discriminant < 0) return false;
    auto sqrtd = sqrt(discriminant);

    // Find the nearest root that lies in the acceptable range.
    bool is_hit = false;
    auto root0 = (-half_b + sqrtd) / a;
    auto root1 = (-half_b - sqrtd) / a;
    if (root0 > t_min && t_max > root0) {
        rec.t.push_back(root0);
        rec.p.push_back(r.at(root0));
        is_hit = true;
    };
    if (root1 > t_min && t_max > root1 && root1 != root0) {
        rec.t.push_back(root1);
        rec.p.push_back(r.at(root1));
        is_hit = true;
    };
    return is_hit;
};

#endif //SPHERE_H
