#ifndef MESH_H
#define MESH_H

#include "hittable_list.h"
#include "vec3.h"
#include "triangle.h"
#include "stl_reader.h"
#include <algorithm>


using namespace std;

class mesh : public hittable {
    public:
    __device__ mesh() {}
    __device__ mesh(const char* filename, vec3 position, material* m) : mat_ptr(m), pos(position) { read_obj(filename); }

    __host__ virtual void read_obj(const char* filename);

    __device__ virtual bool hit(const ray& r, float t_min, float t_max, hit_record& rec) const override;

public:
    material *mat_ptr;
    hittable **list;

    int list_size;
    vec3 pos;
};

__host__ void mesh::read_obj(const char* filename) {
    try {
        stl_reader::StlMesh<float, unsigned int> mesh (filename);

        list_size = mesh.num_tris();
        list = new hittable*[list_size];
        for (int i = 0; i < mesh.num_tris(); i++) {
            vec3 v0 = vectortoVec3(mesh.tri_corner_coords(i, 0)) + pos;
            vec3 v1 = vectortoVec3(mesh.tri_corner_coords(i, 1)) + pos;
            vec3 v2 = vectortoVec3(mesh.tri_corner_coords(i, 2)) + pos;
            list[i] = new triangle(v0, v1, v2, mat_ptr);
        }
    }
    catch (const std::exception &e) {
        std::cerr << e.what() << std::endl;
    }
}

__device__ bool mesh::hit(const ray &r, float t_min, float t_max, hit_record &rec) const {
    bool is_hit = false;
    hit_record mesh_rec;
    float d = 0; // d is used to store the distance travelled through the object

    for (int i = 0; i < list_size; i++) {
        if (list[i]->hit(r, t_min, t_max, mesh_rec)) {
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
