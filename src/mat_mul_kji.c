#include <stdio.h>      /* printf                         */
#include <stdlib.h>     /* malloc, calloc, free, atoi     */
#include <string.h>     /* memset                         */
#include <stdint.h>     /* uint32_t, uint64_t             */

int usage(void) {
    printf("\tUsage: ./mat_mul <N>\n");
    return -1;  // Return -1 to indicate an error
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        return usage();  // Return the result of usage() which is -1
    }
    /* allocate space for matrices */
    uint32_t N   = atoi(argv[1]);
    int64_t  *m1 = malloc(N * N * sizeof(int64_t));
    int64_t  *m2 = malloc(N * N * sizeof(int64_t));
    int64_t  *r  = malloc(N * N * sizeof(int64_t));

    /* initialize matrices */
    for (uint32_t i=0; i<N*N; ++i) {
        m1[i] = i;
        m2[i] = i;
    }

    /* result matrix clear; clock init */
    memset(r, 0, N * N * sizeof(int64_t));
  
    /* perform slow multiplication */
    for (uint32_t k=0; k<N; ++k)
        for (uint32_t j=0; j<N; ++j)         /* column */
            for (uint32_t i=0; i<N; ++i)             /* line   */
                r[i*N + j] += m1[i*N + k] * m2[k*N + j];
  
    return 0;
}
