#ifndef MESH_H
#define MESH_H

#include "hittable_list.h"
#include "vec3.h"
#include "triangle.h"
#include "stl_reader.h"
#include <algorithm>

using std::shared_ptr;
using std::make_shared;
using namespace std;

class mesh : public hittable {
    public:
    mesh() {}
    mesh(const char* filename, vec3 position, shared_ptr<material> m) : mat_ptr(m), pos(position) { read_obj(filename); }

    virtual void read_obj(const char* filename);

    virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

    void clear() { objects.clear(); }
    void add(shared_ptr<hittable> object) { objects.push_back(object); }

public:
    shared_ptr<material> mat_ptr;
    std::vector<shared_ptr<hittable>> objects;
    vec3 pos;
};

void mesh::read_obj(const char* filename) {
    try {
        stl_reader::StlMesh<float, unsigned int> mesh (filename);

        for (int i = 0; i < mesh.num_tris(); i++) {
            vec3 v0 = vectortoVec3(mesh.tri_corner_coords(i, 0)) + pos;
            vec3 v1 = vectortoVec3(mesh.tri_corner_coords(i, 1)) + pos;
            vec3 v2 = vectortoVec3(mesh.tri_corner_coords(i, 2)) + pos;
            add(make_shared<triangle>(v0, v1, v2, mat_ptr));
        }
    }
    catch (const std::exception &e) {
        std::cerr << e.what() << std::endl;
    }
}

bool mesh::hit(const ray &r, float t_min, float t_max, hit_record &rec) const {
    bool is_hit = false;
    hit_record mesh_rec;
    float d = 0; // d is used to store the distance travelled through the object

    for (const auto &object: objects) {
        if (object->hit(r, t_min, t_max, mesh_rec)) {
            is_hit = true;
        }
    }

    if (!is_hit) return false; // if no object is hit, return false

    sort(mesh_rec.t.begin(), mesh_rec.t.end());  // sort the hit points from smallest to largest
    int inc = 2;
    for (int i = 0; i < mesh_rec.t.size(); i+=inc) {
        d += r.diff(mesh_rec.t[i], mesh_rec.t[i + 1]);  // calculate the distance travelled through section of object and add to d
    }
    mesh_rec.trans_prob = mat_ptr->transmission(d);  // calculate the transmission probability
    rec = mesh_rec; // update the hit_record
    return true;
}
#endif //MESH_H
