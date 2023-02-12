#ifndef CAMERA_H
#define CAMERA_H

#include "utility.h"

class camera {
public:
    camera() {}
    camera(int image_width, float viewport_width, float aspect_ratio, float focal_length) {
        float viewport_height = viewport_width * aspect_ratio;


        vec3 origin = vec3(0, 0, 0);
        vec3 horizontal = vec3(viewport_width, 0, 0);
        vec3 vertical = vec3(0, viewport_height, 0);
        vec3 lower_left_corner = origin - horizontal/2 - vertical/2 - vec3(0, 0, focal_length);



    }
    ray get_ray(float u, float v) const {
        return ray(origin, lower_left_corner + u*horizontal + v*vertical - origin);
    }
private:

    vec3 origin;
    vec3 lower_left_corner;
    vec3 horizontal;
    vec3 vertical;
};

#endif //CAMERA_H