#include "utility.h"

#include "color.h"
#include "hittable_list.h"
#include "sphere.h"

#include <iostream>

float ray_intensity(const ray& r, const hittable& world) {
    hit_record rec;
      if (world.hit(r, 0, infinity, rec)) {
            return rec.trans_prob; // if hit, return the probability of transmission
        }
      else {
          return 1; // if not hit, return 1 (vacuum)
      }
}


int main() {

    // Image
    const float aspect_ratio = 16.0 / 9.0;
    const int image_width = 800;
    const int image_height = static_cast<int>(image_width / aspect_ratio);

    // World
    hittable_list world; // list of objects in the world;
    world.add(make_shared<sphere>(point3(0,0,-1), 0.5, make_shared<material>(2.059E-01, 1.0))); // sphere of water
    world.add(make_shared<sphere>(point3(0,0.5,-3), 0.5, make_shared<material>(3.843E+00, 11.29))); // sphere of lead
    world.add(make_shared<sphere>(point3(0,-0.5,-3), 0.5, make_shared<material>(3.148E-01, 1.8))); // sphere of cortical bone


    // Camera
    const float viewport_height = 1.5;
    const float viewport_width = aspect_ratio * viewport_height;
    const float focal_length = 1.0;

    point3 origin = point3(0, 0, 0);
    vec3 horizontal = vec3(viewport_width, 0, 0);
    vec3 vertical = vec3(0, viewport_height, 0);
    vec3 lower_left_corner = origin - horizontal/2 - vertical/2 - vec3(0, 0, focal_length);

    // Render
    std::ofstream render;
    render.open("examples/sphere_of_water_w_lead_and_bone.pgm"); // open pgm file for writing greyscale image
    render << "P2\n" << image_width << ' ' << image_height << "\n255\n";
    for (int j = image_height-1; j >= 0; --j) {
        std::cerr << "\rScanlines remaining: " << j << ' ' << std::flush;
        for (int i = 0; i < image_width; ++i) {
            auto u = float(i) / (image_width-1);
            auto v = float(j) / (image_height-1);
            ray r(origin, lower_left_corner + u*horizontal + v*vertical); // ray from camera to pixel;
            float intensity = ray_intensity(r, world);
            write_color(render, intensity);
        }
    }
    render.close();
    std::cerr << "\nDone.\n";
    return 0;
}