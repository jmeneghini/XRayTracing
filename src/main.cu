#include "utility.h"

#include "color.h"
#include "hittable_list.h"
#include "sphere.h"
#include "mesh.h"

#include <iostream>

// limited version of checkCudaErrors from helper_cuda.h in CUDA examples
#define checkCudaErrors(val) check_cuda( (val), #val, __FILE__, __LINE__ )

void check_cuda(cudaError_t result, char const *const func, const char *const file, int const line) {
    if (result) {
        std::cerr << "CUDA error = " << static_cast<unsigned int>(result) << " at " <<
                  file << ":" << line << " '" << func << "' \n";
        // Make sure we call CUDA Device Reset before exiting
        cudaDeviceReset();
        exit(99);
    }
}

__device__ float ray_intensity(const ray r, const hittable_list world) {
    hit_record rec;
      if (world.hit(r, 0, infinity, rec)) {
            return rec.trans_prob; // if hit, return the probability of transmission
        }
      else {
          return 1.0f; // if not hit, return 1 (vacuum)
      }
}
__global__ void render(float *fb, int image_width, int image_height, hittable_list **world, vec3 origin, vec3 lower_left_corner, vec3 horizontal, vec3 vertical) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    int j = threadIdx.y + blockIdx.y * blockDim.y;
    if ((i >= image_width) || (j >= image_height)) return;
    int pixel_index = j * image_width + i;
    float u = float(i) / (image_width - 1);
    float v = float(j) / (image_height - 1);
    ray r(origin, lower_left_corner + u * horizontal + v * vertical);
    fb[pixel_index] = ray_intensity(r, **world);
}

__global__ void create_world(hittable_list **world) {
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        material bone_mtr = material(3.148E-01, 1.8); // material of the bone
        mesh mesh1 = mesh("stl/ancient_chinese_coin.stl", vec3(0, 0, 0), device_ptr<material>(&bone_mtr)); // create the mesh
        (**world).add(device_ptr<hittable>(&mesh1)); // add the mesh to the world
    }
}



int main() {

    // Image
    const float aspect_ratio = 16.0 / 9.0;
    const int image_width = 800;
    const int image_height = static_cast<int>(image_width / aspect_ratio);
    const int thread_width = 8;
    const int thread_height = 8;
    const int num_pixels = image_width * image_height;

    size_t fb_size = num_pixels * sizeof(float); // framebuffer size
    float *fb;
    checkCudaErrors(cudaMallocManaged((void **)&fb, fb_size)); // allocate framebuffer

    // World
    hittable_list **d_world; // list of objects in the world;
    checkCudaErrors(cudaMallocManaged((void **)&d_world, sizeof(hittable))); // allocate memory for the world
    create_world<<<1, 1>>>(d_world); // create the world
    checkCudaErrors(cudaGetLastError());
    checkCudaErrors(cudaDeviceSynchronize());


    // Camera
    const float viewport_height = 12.0;
    const float viewport_width = aspect_ratio * viewport_height;
    const float focal_length = 6.0;

    vec3 origin = vec3(0, 0, 0);
    vec3 horizontal = vec3(viewport_width, 0, 0);
    vec3 vertical = vec3(0, viewport_height, 0);
    vec3 lower_left_corner = origin - horizontal/2 - vertical/2 - vec3(-1, 0, focal_length);

    // Render our buffer
    dim3 blocks(image_width/thread_width + 1, image_height/thread_height + 1);
    dim3 threads(thread_width, thread_height);
    render<<<blocks, threads>>>(fb, image_width, image_height, d_world, origin, lower_left_corner, horizontal, vertical);
    checkCudaErrors(cudaGetLastError());
    checkCudaErrors(cudaDeviceSynchronize());

    // Output FB as Image
    std::ofstream render;
    render.open("examples/ancient_chinese_coin.pgm"); // open pgm file for writing greyscale image
    render << "P2\n" << image_width << ' ' << image_height << "\n255\n";
    for (int j = image_height-1; j >= 0; --j) {
        std::cerr << "\rScanlines remaining: " << j << ' ' << std::flush;
        for (int i = 0; i < image_width; ++i) {
            size_t pixel_index = j*image_width+ i;
            write_color(render, fb[pixel_index]);
        }
    }
    render.close();
    std::cerr << "\nDone.\n";

    // clean up
    checkCudaErrors(cudaDeviceSynchronize());
    checkCudaErrors(cudaGetLastError());
    checkCudaErrors(cudaFree(fb));
    checkCudaErrors(cudaFree(&d_world));



    // useful for cuda-memcheck --leak-check full
    cudaDeviceReset();
    return 0;
}