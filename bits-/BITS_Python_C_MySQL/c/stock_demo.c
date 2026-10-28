#include <stdio.h>
#include <stdlib.h>
#include "stock_rules.h"

int main(int argc, char **argv) {
    int current, delta, result;
    if (argc != 3) {
        fprintf(stderr, "Usage: stock_demo <current_quantity> <delta>\nExample: stock_demo 5 -1\n");
        return 2;
    }
    current = atoi(argv[1]); delta = atoi(argv[2]);
    if (!bits_apply_stock_delta(current, delta, &result)) {
        puts("Rejected: stock must not become negative.");
        return 1;
    }
    printf("Accepted: new quantity = %d\n", result);
    return 0;
}
