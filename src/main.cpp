#include "utility.h"

#include "color.h"
#include "hittable_list.h"
#include "sphere.h"
#include "mesh.h"
#include "camera.h"
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
    cout << "\n<Config File Settings>" << endl;
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
    int viewport_height = viewport_width / aspect_ratio;
    int focal_length = config["viewport"]["focal_length"].get<float>();


    cout << "\n<Image Settings>" << endl;
    cout << "Image resolution: " << image_width << "x" << image_height << endl;
    cout << "Viewport dimensions: " << viewport_width << "x" << viewport_height << " cm\n" << endl;
    camera camera(viewport_width, aspect_ratio, focal_length);

    // World
    hittable_list world; // list of objects in the world;
    world.add(make_shared<mesh>("stl/Soda_Can.stl", vec3(0, 0, -focal_length),
                                make_shared<material>("Al", 40))); // Plastic Container


    // Render
    std::ofstream render;
    render.open(string(argv[2]) + ".pgm"); // open pgm file for writing greyscale image
    render << "P2\n" << image_width << ' ' << image_height << "\n255\n";
    for (int j = image_height-1; j >= 0; --j) {
        std::cerr << "\rScanlines remaining: " << j << ' ' << std::flush;
        for (int i = 0; i < image_width; ++i) {
            auto u = float(i) / (image_width-1);
            auto v = float(j) / (image_height-1);
            ray r = camera.get_ray(u, v); // ray from camera to pixel;
            float intensity = ray_intensity(r, world);
            write_color(render, intensity);
        }
    }
    render.close();
    system((string("convert") + " " + argv[2] + ".pgm " + argv[2] + ".png").c_str()); // convert pgm to png
    system((string("rm") + " " + argv[2] + ".pgm").c_str()); // remove pgm file
    std::cerr << "\nDone.\n";
    return 0;
}
