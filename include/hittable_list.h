#ifndef HITTABLE_LIST_H
#define HITTABLE_LIST_H

#include "hittable.h"

#include <memory>
#include <vector>

using std::shared_ptr;
using std::make_shared;

class hittable_list : public hittable {
public:
    hittable_list() {}
    hittable_list(shared_ptr<hittable> object) { add(object); }

    void clear() { objects.clear(); }
    void add(shared_ptr<hittable> object) { objects.push_back(object); }

    virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

public:
    std::vector<shared_ptr<hittable>> objects;
};

bool hittable_list::hit(const ray& r, float t_min, float t_max, hit_record& rec) const {
    hit_record temp_rec; // temp_rec is used to store the hit_record of all objects
    bool hit_anything = false;  // hit_anything is used to check if any object is hit
    float total_prob = 1.0;  // total_prob is used to store the total probability of the transmission

    for (const auto &object: objects) { // loop through all objects
        if (object->hit(r, t_min, t_max, temp_rec)) {
            hit_anything = true;
            total_prob *= temp_rec.trans_prob; // update the total_prob
            temp_rec.trans_prob = total_prob;
            rec = temp_rec;
        }
    }
    return hit_anything;
}
#endif //HITTABLE_LIST_H
