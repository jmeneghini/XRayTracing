#include "utility.h"

#include "color.h"
#include "hittable_list.h"
#include "sphere.h"
#include "mesh.h"
#include "json.h"
#include "camera.h"
#include "json.h"
#include <string>
#include <fstream>

using nlohmann::json;

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


int main(int argc, char *argv[]) {

    if (argc == 1) {
        cout << "Please provide a config file" << endl;
        return 1;
    }
    if (argc == 2) {
        cout << "Please provide an output file location" << endl;
    }
    if (argc > 3) {
        cout << "Too many arguments" << endl;
        return 1;
    }
    cout << "Reading config file: " << argv[1] << endl;
    cout << "Output file name: " << argv[2] << endl;

    // Read camera config file
    string file_loc = argv[1];
    std::ifstream config_file(file_loc);
    json config = json::parse(config_file);



    // Image
    int aspect_ratio = config["camera"]["aspect_ratio"].get<float>();

    int image_width =  config["camera"]["image"]["width"].get<int>();
    int image_height = image_width * aspect_ratio;
    int viewport_width = config["viewport"]["width"].get<int>();
    int viewport_height = viewport_width * aspect_ratio;

    int focal_length = config["viewport"]["focal_length"].get<float>();


    camera cam(image_width, viewport_width, aspect_ratio, focal_length);



    // World
    hittable_list world; // list of objects in the world;
//    world.add(make_shared<mesh>("stl/glass_slab.stl", vec3(0, 0, -focal_length),
//                                make_shared<material>(1.890E-01, 2.23))); // pyrex glass at 80 keV
//    world.add(make_shared<mesh>("stl/plastic_slab.stl", vec3(0, 0, -focal_length),
//                                make_shared<material>(1.751E-01, 1.19000E+00))); // acrylic at 80 keV
//    world.add(make_shared<mesh>("stl/plastic_container.stl", vec3(0, 0, -focal_length),
//                                make_shared<material>(1.751E-01, 1.19000E+00))); //  acrylic container at 80 keV
//    world.add(make_shared<mesh>("stl/plastic_container_liquid.stl", vec3(0, 0, -focal_length),
//                                make_shared<material>(1.837E-01, 1.0))); //  water at 80 keV
    world.add(make_shared<mesh>("stl/aluminum_G.stl", vec3(0.1f, 0, -focal_length),
                                make_shared<material>(2.018E-01, 2.699E+00))); //  aluminum at 80 keV

    // Render
    std::ofstream render;
    render.open(argv[2]); // open pgm file for writing greyscale image
    render << "P2\n" << image_width << ' ' << image_height << "\n255\n";
    for (int j = image_height-1; j >= 0; --j) {
        std::cerr << "\rScanlines remaining: " << j << ' ' << std::flush;
        for (int i = 0; i < image_width; ++i) {
            auto u = float(i) / (image_width-1);
            auto v = float(j) / (image_height-1);
            ray r = cam.get_ray(u, v); // ray from camera to pixel;
            float intensity = ray_intensity(r, world);
            write_color(render, intensity);
        }
    }
    render.close();
    std::cerr << "\nDone.\n";
    return 0;
}
