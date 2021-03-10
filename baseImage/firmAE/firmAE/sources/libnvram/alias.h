#ifndef INCLUDE_ALIAS_H
#define INCLUDE_ALIAS_H

// Iterates through each NVRAM key-value pair, and calls *fp with optional third data parameter.
int foreach_nvram_from(const char *file, void (*fp)(const char *, const char *, void *), void *data);

#endif
