#ifndef HITTABLE_LIST_H
#define HITTABLE_LIST_H

#include "hittable.h"



class hittable_list : public hittable {
public:
    __device__ hittable_list() {}
    __device__ hittable_list(device_ptr<hittable> object) { add(object); }

    __device__ void clear() { objects.clear(); }
    __device__ void add(device_ptr<hittable> object) { objects.push_back(object); }

    __device__ virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

public:
    device_vector<device_ptr<hittable>> objects;
};

__device__ bool hittable_list::hit(const ray& r, float t_min, float t_max, hit_record& rec) const {
    hit_record temp_rec; // temp_rec is used to store the hit_record of all objects
    bool hit_anything = false;  // hit_anything is used to check if any object is hit
    float total_prob = 1.0;  // total_prob is used to store the total probability of the transmission

    for (const auto &object: objects) { // loop through all objects
        if (object.get()->hit(r, t_min, t_max, temp_rec)) {
            hit_anything = true;
            total_prob *= temp_rec.trans_prob; // update the total_prob
            temp_rec.trans_prob = total_prob;
            rec = temp_rec;
        }
    }
    return hit_anything;
}
#endif //HITTABLE_LIST_H
