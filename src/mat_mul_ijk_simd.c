#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <immintrin.h>  /* AVX intrinsics */

int usage(void) {
    printf("\tUsage: ./mat_mul <N>\n");
    return -1;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        return usage();
    }

    uint32_t N = atoi(argv[1]);
    int64_t *m1 = malloc(N * N * sizeof(int64_t));
    int64_t *m2 = malloc(N * N * sizeof(int64_t));
    int64_t *r = malloc(N * N * sizeof(int64_t));

    /* Initialize matrices */
    for (uint32_t i = 0; i < N * N; ++i) {
        m1[i] = i;
        m2[i] = i;
    }

    memset(r, 0, N * N * sizeof(int64_t));

    /* Optimized matrix multiplication */
    for (uint32_t i = 0; i < N; ++i) {
        for (uint32_t j = 0; j < N; ++j) {
            int64_t sum = 0;
            for (uint32_t k = 0; k < N; k += 4) {  // Process 4 elements at a time
                __m256i m1_vec = _mm256_loadu_si256((__m256i*)&m1[i * N + k]);
                __m256i m2_vec = _mm256_loadu_si256((__m256i*)&m2[k * N + j]);
                __m256i prod_lo = _mm256_mul_epu32(m1_vec, m2_vec);  // Multiply even indices
                __m256i m1_shifted = _mm256_srli_epi64(m1_vec, 32);  // Shift high parts
                __m256i m2_shifted = _mm256_srli_epi64(m2_vec, 32);
                __m256i prod_hi = _mm256_mul_epu32(m1_shifted, m2_shifted);  // Multiply odd indices

                __m256i sum_vec = _mm256_add_epi64(prod_lo, prod_hi);  // Combine
                int64_t temp[4];
                _mm256_storeu_si256((__m256i*)temp, sum_vec);
                sum += temp[0] + temp[1] + temp[2] + temp[3];
            }
            r[i * N + j] = sum;
        }
    }

    free(m1);
    free(m2);
    free(r);

    return 0;
}
