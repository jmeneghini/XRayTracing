#include <iostream>
#include "vec3.h"
#include "color.h"
#include <fstream>

int main() {

    // Image
    const int image_width = 256;
    const int image_height = 256;

    // Render

    std::ofstream render;
    render.open("examples/test.ppm");
    render << "P3\n" << image_width << ' ' << image_height << "\n255\n";
    for (int j = image_height-1; j >= 0; --j) {
        std::cerr << "\rScanlines remaining: " << j << ' ' << std::flush;
        for (int i = 0; i < image_width; ++i) {
            color pixel_color = color(double(i) / (image_width - 1), double(j) / (image_height - 1), 0.25);
            write_color(render, pixel_color);
        }
    }
    render.close();
    std::cerr << "\nDone.\n";
    return 0;
}
