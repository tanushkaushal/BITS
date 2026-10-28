#ifndef BITS_STOCK_RULES_H
#define BITS_STOCK_RULES_H
/* Small C helper shared with the BITS stock-policy demo/CLI. */
int bits_valid_quantity(int quantity);
int bits_apply_stock_delta(int current_quantity, int delta, int *new_quantity);
#endif
