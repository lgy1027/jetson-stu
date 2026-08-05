// Day 3 CUDA smoke test for Jetson AGX Thor.
//
// This program intentionally does two things:
//   1. prints CUDA device and unified-memory capabilities;
//   2. runs and verifies a real GPU vector-add kernel using managed memory.

#include <cuda_runtime.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>

#define CUDA_CHECK(call)                                                        \
  do {                                                                          \
    const cudaError_t status = (call);                                          \
    if (status != cudaSuccess) {                                                \
      std::fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__, \
                   cudaGetErrorString(status));                                 \
      return EXIT_FAILURE;                                                      \
    }                                                                           \
  } while (0)

__global__ void vector_add(const float* a, const float* b, float* c,
                           std::size_t count) {
  const std::size_t index =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (index < count) {
    c[index] = a[index] + b[index];
  }
}

int main() {
  int device_count = 0;
  CUDA_CHECK(cudaGetDeviceCount(&device_count));
  if (device_count < 1) {
    std::fprintf(stderr, "FAIL: no CUDA device detected.\n");
    return EXIT_FAILURE;
  }

  constexpr int kDevice = 0;
  CUDA_CHECK(cudaSetDevice(kDevice));

  cudaDeviceProp properties{};
  CUDA_CHECK(cudaGetDeviceProperties(&properties, kDevice));

  int driver_version = 0;
  int runtime_version = 0;
  CUDA_CHECK(cudaDriverGetVersion(&driver_version));
  CUDA_CHECK(cudaRuntimeGetVersion(&runtime_version));

  std::size_t device_free_bytes = 0;
  std::size_t device_total_bytes = 0;
  CUDA_CHECK(cudaMemGetInfo(&device_free_bytes, &device_total_bytes));

  std::printf("CUDA smoke test: Day 3\n");
  std::printf("GPU name: %s\n", properties.name);
  std::printf("Compute Capability: %d.%d\n", properties.major, properties.minor);
  std::printf("CUDA driver version: %d.%d\n", driver_version / 1000,
              (driver_version % 1000) / 10);
  std::printf("CUDA runtime version: %d.%d\n", runtime_version / 1000,
              (runtime_version % 1000) / 10);
  std::printf("Global memory reported by CUDA: %.2f GiB\n",
              static_cast<double>(properties.totalGlobalMem) / (1024.0 * 1024.0 * 1024.0));
  std::printf("CUDA free / total memory: %.2f / %.2f GiB\n",
              static_cast<double>(device_free_bytes) / (1024.0 * 1024.0 * 1024.0),
              static_cast<double>(device_total_bytes) / (1024.0 * 1024.0 * 1024.0));
  std::printf("Unified memory supported: %s\n", properties.managedMemory ? "yes" : "no");
  std::printf("Concurrent managed access: %s\n",
              properties.concurrentManagedAccess ? "yes" : "no");

  if (!properties.managedMemory) {
    std::fprintf(stderr, "FAIL: this exercise requires CUDA managed memory.\n");
    return EXIT_FAILURE;
  }

  constexpr std::size_t kElementCount = 8U * 1024U * 1024U;
  const std::size_t bytes = kElementCount * sizeof(float);
  float* a = nullptr;
  float* b = nullptr;
  float* c = nullptr;
  CUDA_CHECK(cudaMallocManaged(&a, bytes));
  CUDA_CHECK(cudaMallocManaged(&b, bytes));
  CUDA_CHECK(cudaMallocManaged(&c, bytes));

  for (std::size_t index = 0; index < kElementCount; ++index) {
    a[index] = static_cast<float>(index % 1024U) * 0.25F;
    b[index] = static_cast<float>(index % 256U) * 0.5F;
  }

  cudaStream_t stream{};
  CUDA_CHECK(cudaStreamCreate(&stream));
  // CUDA 13.2 uses cudaMemLocation rather than the older device-ordinal API.
  cudaMemLocation gpu_location{};
  gpu_location.type = cudaMemLocationTypeDevice;
  gpu_location.id = kDevice;
  CUDA_CHECK(cudaMemPrefetchAsync(a, bytes, gpu_location, 0, stream));
  CUDA_CHECK(cudaMemPrefetchAsync(b, bytes, gpu_location, 0, stream));
  CUDA_CHECK(cudaMemPrefetchAsync(c, bytes, gpu_location, 0, stream));

  constexpr int kThreadsPerBlock = 256;
  const int blocks = static_cast<int>((kElementCount + kThreadsPerBlock - 1) /
                                      kThreadsPerBlock);
  cudaEvent_t start{};
  cudaEvent_t stop{};
  CUDA_CHECK(cudaEventCreate(&start));
  CUDA_CHECK(cudaEventCreate(&stop));
  CUDA_CHECK(cudaEventRecord(start, stream));
  vector_add<<<blocks, kThreadsPerBlock, 0, stream>>>(a, b, c, kElementCount);
  CUDA_CHECK(cudaGetLastError());
  CUDA_CHECK(cudaEventRecord(stop, stream));
  CUDA_CHECK(cudaEventSynchronize(stop));

  float elapsed_ms = 0.0F;
  CUDA_CHECK(cudaEventElapsedTime(&elapsed_ms, start, stop));
  cudaMemLocation cpu_location{};
  cpu_location.type = cudaMemLocationTypeHost;
  cpu_location.id = 0;  // Ignored for cudaMemLocationTypeHost.
  CUDA_CHECK(cudaMemPrefetchAsync(c, bytes, cpu_location, 0, stream));
  CUDA_CHECK(cudaStreamSynchronize(stream));

  std::size_t mismatches = 0;
  float max_absolute_error = 0.0F;
  for (std::size_t index = 0; index < kElementCount; ++index) {
    const float expected = a[index] + b[index];
    const float absolute_error = std::fabs(c[index] - expected);
    if (absolute_error > 1.0e-6F) {
      ++mismatches;
      if (absolute_error > max_absolute_error) {
        max_absolute_error = absolute_error;
      }
    }
  }

  std::printf("Managed-memory allocation: %.2f MiB across three arrays\n",
              3.0 * static_cast<double>(bytes) / (1024.0 * 1024.0));
  std::printf("Kernel: vector_add (%zu elements, %d blocks x %d threads)\n",
              kElementCount, blocks, kThreadsPerBlock);
  std::printf("Kernel time: %.3f ms\n", elapsed_ms);
  std::printf("Verification mismatches: %zu, max absolute error: %.8f\n", mismatches,
              max_absolute_error);

  CUDA_CHECK(cudaEventDestroy(start));
  CUDA_CHECK(cudaEventDestroy(stop));
  CUDA_CHECK(cudaStreamDestroy(stream));
  CUDA_CHECK(cudaFree(a));
  CUDA_CHECK(cudaFree(b));
  CUDA_CHECK(cudaFree(c));

  if (mismatches != 0) {
    std::fprintf(stderr, "FAIL: GPU results do not match CPU verification.\n");
    return EXIT_FAILURE;
  }

  std::printf("PASS: CUDA kernel executed and managed-memory results verified.\n");
  return EXIT_SUCCESS;
}
