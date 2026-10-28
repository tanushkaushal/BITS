#include "stock_rules.h"

int bits_valid_quantity(int quantity) {
    return quantity >= 0;
}

/* Returns 1 on success, 0 if the change would produce a negative quantity. */
int bits_apply_stock_delta(int current_quantity, int delta, int *new_quantity) {
    if (new_quantity == 0 || !bits_valid_quantity(current_quantity)) return 0;
    if (delta < -current_quantity) return 0;
    *new_quantity = current_quantity + delta;
    return bits_valid_quantity(*new_quantity);
}
