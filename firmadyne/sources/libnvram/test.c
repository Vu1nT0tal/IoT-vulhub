#include <stdio.h>

#include "nvram.h"

// Prototypes from "alias.c"
char *nvram_nget(const char *fmt, ...);
int nvram_nset(const char *val, const char *fmt, ...);
int foreach_nvram_from(const char *file, void (*fp)(const char *, const char *, void *), void *data);


void test(const char *key, const char*val, void* data) {
    printf("%s = %s, %s\n", key, val, (char *) data);
}

int main(int argc, char** argv) {
    char buf[256], *ptr;
    int tmp;

    nvram_init();

    nvram_clear();

    nvram_set_default();

    nvram_getall(buf, 256);

    nvram_set("str", "test");

    nvram_set_int("int", 2048);

    ptr = nvram_get("str");

    tmp = nvram_get_int("int");

    nvram_commit();

    nvram_getall(buf, 256);

    nvram_reset();

    ptr = nvram_get("is_default");

    nvram_close();

    nvram_unset("is_default");

    ptr = nvram_get("is_default");

    nvram_nset("test", "%s_file", "a");

    ptr = nvram_nget("%s_file", "a");

    foreach_nvram_from("/tmp/test.ini", test, "5");

    return 0;
}
