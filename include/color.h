//
// Created by john on 10/19/22.
//

#ifndef COLOR_H
#define COLOR_H

#include "vec3.h"

#include <iostream>
#include <fstream>

void write_color(std::ofstream &file, color pixel_color) {
    // Write the translated [0,255] value of each color component.
          file << static_cast<int>(255.999 * pixel_color.r()) << ' '
              << static_cast<int>(255.999 * pixel_color.g()) << ' '
              << static_cast<int>(255.999 * pixel_color.b()) << '\n';
}

#endif //COLOR_H
