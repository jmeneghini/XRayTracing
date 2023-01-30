//
// Created by john on 10/19/22.
//

#ifndef COLOR_H
#define COLOR_H

#include "vec3.h"

#include <iostream>
#include <fstream>

__host__ void write_color(std::ofstream &file, float intensity) {
    // Write the translated [0,255] value of pixel intensity
          file << static_cast<int>(255.999 * (1.0-intensity)) << '\n';
}

#endif //COLOR_H
