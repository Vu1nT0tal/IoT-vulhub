#ifndef INCLUDE_ALIAS_C
#define INCLUDE_ALIAS_C

/* Aliased base functions */

int true() {
    return E_SUCCESS;
}

int false() {
    return E_FAILURE;
}

int nvram_load(void) __attribute__ ((alias ("nvram_init")));
int nvram_loaddefault(void) __attribute__ ((alias ("nvram_set_default")));
char *_nvram_get(const char *key) __attribute__ ((alias ("nvram_get")));
int nvram_get_state(const char *key) __attribute__ ((alias ("nvram_get_int")));
int nvram_set_state(const char *key, const int val) __attribute__ ((alias ("nvram_set_int")));
int nvram_restore_default(void) __attribute__ ((alias ("nvram_reset")));
int nvram_upgrade(void* ptr) __attribute__ ((alias ("nvram_commit")));

/* Atheros/Broadcom NVRAM */

int nvram_get_nvramspace(void) {
    return NVRAM_SIZE;
}

int foreach_nvram_from(const char *file, void (*fp)(const char *, const char *, void *), void *data) {
    char *key, *val, *tmp;
    FILE *f;

    if (!fp) {
        PRINT_MSG("%s\n", "NULL function pointer!");
        return E_FAILURE;
    }

    if ((f = fopen(file, "r")) == NULL) {
        PRINT_MSG("Unable to open file: %s!\n", file);
        return E_FAILURE;
    }

    while (fgets(temp, BUFFER_SIZE, f) == temp) {
        if (!(val = strchr(temp, '='))) {
            continue;
        }

        key = temp;
        *val = '\0';
        val += 1;

        if ((tmp = strchr(val, '\n')) != NULL) {
            *tmp = '\0';
        }

        if (data) {
            fp(key, val, data);
        }
        else {
            ((void (*)(const char *, const char *)) fp)(key, val);
        }
    }

    fclose(f);
    return E_SUCCESS;
}

char *nvram_nget(const char *fmt, ...) {
    va_list va;

    va_start(va, fmt);
    vsnprintf(temp, BUFFER_SIZE, fmt, va);
    va_end(va);

    return nvram_get(temp);
}

int nvram_nset(const char *val, const char *fmt, ...) {
    va_list va;

    va_start(va, fmt);
    vsnprintf(temp, BUFFER_SIZE, fmt, va);
    va_end(va);

    return nvram_set(temp, val);
}

int nvram_nset_int(const int val, const char *fmt, ...) {
    va_list va;

    va_start(va, fmt);
    vsnprintf(temp, BUFFER_SIZE, fmt, va);
    va_end(va);

    return nvram_set_int(temp, val);
}

int nvram_nmatch(const char *val, const char *fmt, ...) {
    va_list va;

    va_start(va, fmt);
    vsnprintf(temp, BUFFER_SIZE, fmt, va);
    va_end(va);

    return nvram_match(temp, val);
}

int get_default_mac() __attribute__ ((alias ("true")));

/* D-Link */

char *artblock_get(const char *key) __attribute__ ((alias ("nvram_get")));
char *artblock_fast_get(const char *key) __attribute__ ((alias ("nvram_safe_get")));
char *artblock_safe_get(const char *key) __attribute__ ((alias ("nvram_safe_get")));
int artblock_set(const char *key, const char *val) __attribute__ ((alias ("nvram_set")));
int nvram_flag_set(int unk) __attribute__ ((alias ("true")));
int nvram_flag_reset(int unk) __attribute__ ((alias ("true")));

/* D-Link ARM */
int nvram_master_init() __attribute__ ((alias ("false")));
int nvram_slave_init() __attribute__ ((alias ("false")));

/* Realtek */
// These functions expect integer keys, so we convert to string first.
// Unfortunately, this implementation is not entirely correct because some
// values are integers and others are string, but we treat all as integers.
int apmib_init() __attribute__ ((alias ("true")));
int apmib_reinit() __attribute__ ((alias ("true")));
// int apmib_hwconf() __attribute__ ((alias ("true")));
// int apmib_dsconf() __attribute__ ((alias ("true")));
// int apmib_load_hwconf() __attribute__ ((alias ("true")));
// int apmib_load_dsconf() __attribute__ ((alias ("true")));
// int apmib_load_csconf() __attribute__ ((alias ("true")));
int apmib_update(const int key) __attribute__((alias ("true")));

int apmib_get(const int key, void *buf) {
    int res;

    snprintf(temp, BUFFER_SIZE, "%d", key);
    if ((res = nvram_get_int(temp))) {
        (*(int32_t *) buf) = res;
    }

    return res;
}

int apmib_set(const int key, void *buf) {
    snprintf(temp, BUFFER_SIZE, "%d", key);
    return nvram_set_int(temp, ((int32_t *) buf)[0]);
}

/* Netgear ACOS */

int WAN_ith_CONFIG_GET(char *buf, const char *fmt, ...) {
    va_list va;

    va_start(va, fmt);
    vsnprintf(temp, BUFFER_SIZE, fmt, va);
    va_end(va);

    return nvram_get_buf(temp, buf, USER_BUFFER_SIZE);
}

int WAN_ith_CONFIG_SET_AS_STR(const char *val, const char *fmt, ...) __attribute__ ((alias ("nvram_nset")));

int WAN_ith_CONFIG_SET_AS_INT(const int val, const char *fmt, ...) __attribute__ ((alias ("nvram_nset_int")));

int acos_nvram_init(void) __attribute__ ((alias ("nvram_init")));
char *acos_nvram_get(const char *key) __attribute__ ((alias ("nvram_get")));
int acos_nvram_read (const char *key, char *buf, size_t sz) __attribute__ ((alias ("nvram_get_buf")));
int acos_nvram_set(const char *key, const char *val) __attribute__ ((alias ("nvram_set")));
int acos_nvram_loaddefault(void) __attribute__ ((alias ("nvram_set_default")));
int acos_nvram_unset(const char *key) __attribute__ ((alias ("nvram_unset")));
int acos_nvram_commit(void) __attribute__ ((alias ("nvram_commit")));

int acosNvramConfig_init(char *mount) __attribute__ ((alias ("nvram_init")));
char *acosNvramConfig_get(const char *key) __attribute__ ((alias ("nvram_get")));
int acosNvramConfig_read (const char *key, char *buf, size_t sz) __attribute__ ((alias ("nvram_get_buf")));
int acosNvramConfig_set(const char *key, const char *val) __attribute__ ((alias ("nvram_set")));
int acosNvramConfig_write(const char *key, const char *val) __attribute__ ((alias ("nvram_set")));
int acosNvramConfig_unset(const char *key) __attribute__ ((alias ("nvram_unset")));
int acosNvramConfig_match(const char *key, const char *val) __attribute__ ((alias ("nvram_match")));
int acosNvramConfig_invmatch(const char *key, const char *val) __attribute__ ((alias ("nvram_invmatch")));
int acosNvramConfig_save(void) __attribute__ ((alias ("nvram_commit")));
int acosNvramConfig_save_config(void) __attribute__ ((alias ("nvram_commit")));
int acosNvramConfig_loadFactoryDefault(const char* key);

/* ZyXel / Edimax */
// many functions expect the opposite return values: (0) success, failure (1/-1)

int nvram_getall_adv(int unk, char *buf, size_t len) {
    return nvram_getall(buf, len) == E_SUCCESS ? E_FAILURE : E_SUCCESS;
}

char *nvram_get_adv(int unk, const char *key) {
    return nvram_get(key);
}

int nvram_set_adv(int unk, const char *key, const char *val) {
    return nvram_set(key, val);
}

int nvram_commit_adv(int) __attribute__ ((alias ("nvram_commit")));
int nvram_unlock_adv(int) __attribute__ ((alias ("true")));
int nvram_lock_adv(int) __attribute__ ((alias ("true")));
int nvram_check(void) __attribute__ ((alias ("true")));

int nvram_state(int unk1, void *unk2, void *unk3) {
    return E_FAILURE;
}

int envram_commit(void) {
    return !nvram_commit();
}

int envram_default(void) {
    return !nvram_set_default();
}

int envram_load(void)  {
    return !nvram_init();
}

int envram_safe_load(void)  {
    return !nvram_init();
}

int envram_match(const char *key, const char *val)  {
    return !nvram_match(key, val);
}

int envram_get(const char* key, char *buf) {
    // may be incorrect
    return !nvram_get_buf(key, buf, USER_BUFFER_SIZE);
}
int envram_get_func(const char* key, char *buf) __attribute__ ((alias ("envram_get")));
int envram_getf(const char* key, const char *fmt, ...) {
    va_list va;
    char *val = nvram_get(key);

    if (!val) {
        return !E_SUCCESS;
    }

    va_start(va, fmt);
    vsscanf(val, fmt, va);
    va_end(va);

    free(val);
    return !E_FAILURE;
}
int nvram_getf(const char* key, const char *fmt, ...) __attribute__ ((alias ("envram_getf")));

int envram_set(const char *key, const char *val) {
    return !nvram_set(key, val);
}
int envram_set_func(const char *key, const char *val) __attribute__ ((alias ("envram_set")));

int envram_setf(const char* key, const char* fmt, ...) {
    va_list va;

    va_start(va, fmt);
    vsnprintf(temp, BUFFER_SIZE, fmt, va);
    va_end(va);

    return !nvram_set(key, temp);
}
int nvram_setf(const char* key, const char* fmt, ...) __attribute__ ((alias ("envram_setf")));

int envram_unset(const char *key) {
    return !nvram_unset(key);
}
int envram_unset_func(void) __attribute__ ((alias ("envram_unset")));

/* Ralink */

char *nvram_bufget(int idx, const char *key) {
    return nvram_safe_get(key);
}

int nvram_bufset(int idx, const char *key, const char *val) {
    return nvram_set(key, val);
}

#endif
