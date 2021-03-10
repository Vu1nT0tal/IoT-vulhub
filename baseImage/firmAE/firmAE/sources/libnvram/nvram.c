#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <mntent.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/mount.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include "alias.h"
#include "nvram.h"
#include "config.h"

/* Generate variable declarations for external NVRAM data. */
#define NATIVE(a, b)
#define PATH(a)
#define FIRMAE_PATH(a)
#define FIRMAE_PATH2(a)
#define TABLE(a) \
    extern const char *a[] __attribute__((weak));

    NVRAM_DEFAULTS_PATH
#undef TABLE
#undef FIRMAE_PATH2
#undef FIRMAE_PATH
#undef PATH
#undef NATIVE

// https://lkml.org/lkml/2007/3/9/10
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]) + sizeof(typeof(int[1 - 2 * !!__builtin_types_compatible_p(typeof(arr), typeof(&arr[0]))])) * 0)

#define PRINT_MSG(fmt, ...) do { if (DEBUG) { fprintf(stderr, "%s: "fmt, __FUNCTION__, __VA_ARGS__); } } while (0)

/* Weak symbol definitions for library functions that may not be present */
__typeof__(ftok) __attribute__((weak)) ftok;

/* Global variables */
static int init = 0;
static char temp[BUFFER_SIZE];
static int is_load_env = 0;
static int firmae_nvram = 0;

static void firmae_load_env()
{
    char* env = getenv("FIRMAE_NVRAM");
    if (env && env[0] == 't')
        firmae_nvram = 1;
    is_load_env = 1;
}

static int sem_get() {
    int key, semid = 0;
    unsigned int timeout = 0;
    struct semid_ds seminfo;
    union semun {
        int val;
        struct semid_ds *buf;
        unsigned short *array;
        struct seminfo *__buf;
    } semun;
    struct sembuf sembuf = {
        .sem_num = 0,
        .sem_op = 1,
        .sem_flg = 0,
    };

    // Generate key for semaphore based on the mount point
    if (!ftok || (key = ftok(MOUNT_POINT, IPC_KEY)) == -1) {
        PRINT_MSG("%s\n", "Unable to get semaphore key! Utilize altenative key.. by SR");
        return -1;
    }

    PRINT_MSG("Key: %x\n", key);

    // Get the semaphore using the key
    if ((semid = semget(key, 1, IPC_CREAT | IPC_EXCL | 0666)) >= 0) {
        semun.val = 1;
        // Unlock the semaphore and set the sem_otime field
        if (semop(semid, &sembuf, 1) == -1) {
            PRINT_MSG("%s\n", "Unable to initialize semaphore!");
            // Clean up semaphore
            semctl(semid, 0, IPC_RMID);
            semid = -1;
        }
    }
    else if (errno == EEXIST) {
        // Get the semaphore in non-exclusive mode
        if ((semid = semget(key, 1, 0)) < 0) {
            PRINT_MSG("%s\n", "Unable to get semaphore non-exclusively!");
            return semid;
        }

        semun.buf = &seminfo;
        // Wait for the semaphore to be initialized
        while (timeout++ < IPC_TIMEOUT) {
            semctl(semid, 0, IPC_STAT, semun);

            if (semun.buf && semun.buf->sem_otime != 0) {
                break;
            }
        }
        if  (timeout >= IPC_TIMEOUT)
            PRINT_MSG("Waiting for semaphore timeout (Key: %x, Semaphore: %x)...\n", key, semid);
    }

    return (timeout < IPC_TIMEOUT) ? semid : -1;
}

static void sem_lock() {
    int semid;
    struct sembuf sembuf = {
        .sem_num = 0,
        .sem_op = -1,
        .sem_flg = SEM_UNDO,
    };
    struct mntent entry, *ent;
    FILE *mnt = NULL;

    // If not initialized, check for existing mount before triggering NVRAM init
    if (!init) {
        if ((mnt = setmntent("/proc/mounts", "r"))) {
            while ((ent = getmntent_r(mnt, &entry, temp, BUFFER_SIZE))) {
                if (!strncmp(ent->mnt_dir, MOUNT_POINT, sizeof(MOUNT_POINT) - 2)) {
                    init = 1;
                    PRINT_MSG("%s\n", "Already initialized!");
                    endmntent(mnt);
                    goto cont;
                }
            }
            endmntent(mnt);
        }

        PRINT_MSG("%s\n", "Triggering NVRAM initialization!");
        nvram_init();
    }

cont:
    // Must get sempahore after NVRAM initialization, mounting will change ID
    if ((semid = sem_get()) == -1) {
        PRINT_MSG("%s\n", "Unable to get semaphore!");
        return;
    }

//    PRINT_MSG("%s\n", "Locking semaphore...");

    if (semop(semid, &sembuf, 1) == -1) {
        PRINT_MSG("%s\n", "Unable to lock semaphore!");
    }

    return;
}

static void sem_unlock() {
    int semid;
    struct sembuf sembuf = {
        .sem_num = 0,
        .sem_op = 1,
        .sem_flg = SEM_UNDO,
    };

    if ((semid = sem_get(NULL)) == -1) {
        PRINT_MSG("%s\n", "Unable to get semaphore!");
        return;
    }

//    PRINT_MSG("%s\n", "Unlocking semaphore...");

    if (semop(semid, &sembuf, 1) == -1) {
        PRINT_MSG("%s\n", "Unable to unlock semaphore!");
    }

    return;
}

int nvram_init(void) {
    FILE *f;

    PRINT_MSG("%s\n", "Initializing NVRAM...");

    if (init) {
        PRINT_MSG("%s\n", "Early termination!");
        return E_SUCCESS;
    }
    init = 1;

    sem_lock();

    if (mount("tmpfs", MOUNT_POINT, "tmpfs", MS_NOEXEC | MS_NOSUID | MS_SYNCHRONOUS, "") == -1) {
        sem_unlock();
        PRINT_MSG("Unable to mount tmpfs on mount point %s!\n", MOUNT_POINT);
        return E_FAILURE;
    }

    // Checked by certain Ralink routers
    if ((f = fopen("/var/run/nvramd.pid", "w+")) == NULL) {
        PRINT_MSG("Unable to touch Ralink PID file: %s!\n", "/var/run/nvramd.pid");
    }
    else {
        fclose(f);
    }

    sem_unlock();

    return nvram_set_default();
}

int nvram_reset(void) {
    PRINT_MSG("%s\n", "Reseting NVRAM...");

    if (nvram_clear() != E_SUCCESS) {
        PRINT_MSG("%s\n", "Unable to clear NVRAM!");
        return E_FAILURE;
    }

    return nvram_set_default();
}

int nvram_clear(void) {
    char path[PATH_MAX] = MOUNT_POINT;
    struct dirent *entry;
    int ret = E_SUCCESS;
    DIR *dir;

    PRINT_MSG("%s\n", "Clearing NVRAM...");

    sem_lock();

    if (!(dir = opendir(MOUNT_POINT))) {
        sem_unlock();
        PRINT_MSG("Unable to open directory %s!\n", MOUNT_POINT);
        return E_FAILURE;
    }

    while ((entry = readdir(dir))) {
        if (!strncmp(entry->d_name, ".", 1) || !strcmp(entry->d_name, "..")) {
            PRINT_MSG("Skipping %s\n", entry->d_name);
            continue;
        }

        strncpy(path + strlen(MOUNT_POINT), entry->d_name, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);
        path[PATH_MAX - 1] = '\0';

        PRINT_MSG("%s\n", path);

        if (unlink(path) == -1 && errno != ENOENT) {
            PRINT_MSG("Unable to unlink %s!\n", path);
            ret = E_FAILURE;
        }
    }

    closedir(dir);
    sem_unlock();
    return ret;
}

int nvram_close(void) {
    PRINT_MSG("%s\n", "Closing NVRAM...");
    return E_SUCCESS;
}

int nvram_list_add(const char *key, const char *val) {
    char *pos;

    PRINT_MSG("%s = %s + %s\n", val, temp, key);

    if (nvram_get_buf(key, temp, BUFFER_SIZE) != E_SUCCESS) {
        return nvram_set(key, val);
    }

    if (!key || !val) {
        return E_FAILURE;
    }

    if (strlen(temp) + 1 + strlen(val) + 1 > BUFFER_SIZE) {
        return E_FAILURE;
    }

    // This will overwrite the temp buffer, but it is OK
    if (nvram_list_exist(key, val, LIST_MAGIC) != NULL) {
        return E_SUCCESS;
    }

    // Replace terminating NULL of list with LIST_SEP
    pos = temp + strlen(temp);
    if (pos != temp) {
        *pos++ = LIST_SEP[0];
    }

    if (strcpy(pos, val) != pos) {
        return E_FAILURE;
    }

    return nvram_set(key, temp);
}

char *nvram_list_exist(const char *key, const char *val, int magic) {
    char *pos = NULL;

    if (nvram_get_buf(key, temp, BUFFER_SIZE) != E_SUCCESS) {
        return E_FAILURE;
    }

    PRINT_MSG("%s ?in %s (%s)\n", val, key, temp);

    if (!val) {
        return (magic == LIST_MAGIC) ? NULL : (char *) E_FAILURE;
    }

    while ((pos = strtok(!pos ? temp : NULL, LIST_SEP))) {
        if (!strcmp(pos + 1, val)) {
            return (magic == LIST_MAGIC) ? pos + 1 : (char *) E_SUCCESS;
        }
    }

    return (magic == LIST_MAGIC) ? NULL : (char *) E_FAILURE;
}

int nvram_list_del(const char *key, const char *val) {
    char *pos;

    if (nvram_get_buf(key, temp, BUFFER_SIZE) != E_SUCCESS) {
        return E_SUCCESS;
    }

    PRINT_MSG("%s = %s - %s\n", key, temp, val);

    if (!val) {
        return E_FAILURE;
    }

    // This will overwrite the temp buffer, but it is OK.
    if ((pos = nvram_list_exist(key, val, LIST_MAGIC))) {
        while (*pos && *pos != LIST_SEP[0]) {
            *pos++ = LIST_SEP[0];
        }
    }

    return nvram_set(key, temp);
}

char *nvram_get(const char *key) {
// Some routers pass the key as the second argument, instead of the first.
// We attempt to fix this directly in assembly for MIPS if the key is NULL.
#if defined(mips)
    if (!key) {
        asm ("move %0, $a1" :"=r"(key));
    }
#endif

    return (nvram_get_buf(key, temp, BUFFER_SIZE) == E_SUCCESS) ? strndup(temp, BUFFER_SIZE) : NULL;
}

char *nvram_safe_get(const char *key) {
    char* ret = nvram_get(key);
    return ret ? ret : strdup("");
}

char *nvram_default_get(const char *key, const char *val) {
    char *ret = nvram_get(key);

    PRINT_MSG("%s = %s || %s\n", key, ret, val);

    if (ret) {
        return ret;
    }

    if (val && nvram_set(key, val)) {
        return nvram_get(key);
    }

    return NULL;
}

int nvram_get_buf(const char *key, char *buf, size_t sz) {
    char path[PATH_MAX] = MOUNT_POINT;
    FILE *f;
    if (!is_load_env) firmae_load_env();

    if (!buf) {
        PRINT_MSG("NULL output buffer, key: %s!\n", key);
        return E_FAILURE;
    }

    if (!key) {
        PRINT_MSG("NULL input key, buffer: %s!\n", buf);
        if (firmae_nvram)
            return E_SUCCESS;
        else
            return E_FAILURE;
    }

    PRINT_MSG("%s\n", key);

    strncat(path, key, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);

    sem_lock();

    if ((f = fopen(path, "rb")) == NULL) {
        sem_unlock();
        PRINT_MSG("Unable to open key: %s! Set default value to \"\"\n", path);
        if (firmae_nvram)
        {
            //If key value is not found, make the default value to ""
            if (!strcmp(key, "noinitrc"))
                return E_FAILURE;
            strcpy(buf,"");
            return E_SUCCESS;
        }
        else
            return E_FAILURE;
    }
    else
    {
        PRINT_MSG("\n\n[NVRAM] %d %s\n\n", strlen(key), key);
    }

    if (fgets(buf, sz, f) != buf) {
        buf[0] = '\0';
    }

    fclose(f);
    sem_unlock();

    PRINT_MSG("= \"%s\"\n", buf);

    return E_SUCCESS;
}

int nvram_get_int(const char *key) {
    char path[PATH_MAX] = MOUNT_POINT;
    FILE *f;
    int ret;

    if (!key) {
        PRINT_MSG("%s\n", "NULL key!");
        return E_FAILURE;
    }

    PRINT_MSG("%s\n", key);

    strncat(path, key, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);

    sem_lock();

    if ((f = fopen(path, "rb")) == NULL) {
        sem_unlock();
        PRINT_MSG("Unable to open key: %s!\n", path);
        return E_FAILURE;
    }

    if (fread(&ret, sizeof(ret), 1, f) != 1) {
        fclose(f);
        sem_unlock();
        PRINT_MSG("Unable to read key: %s!\n", path);
        return E_FAILURE;
    }
    fclose(f);
    sem_unlock();

    PRINT_MSG("= %d\n", ret);

    return ret;
}

int nvram_getall(char *buf, size_t len) {
    char path[PATH_MAX] = MOUNT_POINT;
    struct dirent *entry;
    size_t pos = 0, ret;
    DIR *dir;
    FILE *f;

    if (!buf || !len) {
        PRINT_MSG("%s\n", "NULL buffer or zero length!");
        return E_FAILURE;
    }

    sem_lock();

    if (!(dir = opendir(MOUNT_POINT))) {
        sem_unlock();
        PRINT_MSG("Unable to open directory %s!\n", MOUNT_POINT);
        return E_FAILURE;
    }

    while ((entry = readdir(dir))) {
        if (!strncmp(entry->d_name, ".", 1) || !strcmp(entry->d_name, "..")) {
            continue;
        }

        strncpy(path + strlen(MOUNT_POINT), entry->d_name, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);
        path[PATH_MAX - 1] = '\0';

        if ((ret = snprintf(buf + pos, len - pos, "%s=", entry->d_name)) != strlen(entry->d_name) + 1) {
            closedir(dir);
            sem_unlock();
            PRINT_MSG("Unable to append key %s!\n", buf + pos);
            return E_FAILURE;
        }

        pos += ret;

        if ((f = fopen(path, "rb")) == NULL) {
            closedir(dir);
            sem_unlock();
            PRINT_MSG("Unable to open key: %s!\n", path);
            return E_FAILURE;
        }

        if (!(ret = fread(temp, sizeof(*temp), BUFFER_SIZE, f))) {
            fclose(f);
            closedir(dir);
            sem_unlock();
            PRINT_MSG("Unable to read key: %s!\n", path);
            return E_FAILURE;
        }

        memcpy(buf + pos, temp, ret);
        buf[pos + ret] = '\0';
        pos += ret + 1;

        fclose(f);
    }

    closedir(dir);
    sem_unlock();
    return E_SUCCESS;
}

int nvram_set(const char *key, const char *val) {
    char path[PATH_MAX] = MOUNT_POINT;
    FILE *f;

    if (!key || !val) {
        PRINT_MSG("%s\n", "NULL key or value!");
        return E_FAILURE;
    }

    PRINT_MSG("%s = \"%s\"\n", key, val);

    strncat(path, key, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);

    sem_lock();

    if ((f = fopen(path, "wb")) == NULL) {
        sem_unlock();
        PRINT_MSG("Unable to open key: %s!\n", path);
        return E_FAILURE;
    }

    if (fwrite(val, sizeof(*val), strlen(val), f) != strlen(val)) {
        fclose(f);
        sem_unlock();
        PRINT_MSG("Unable to write value: %s to key: %s!\n", val, path);
        return E_FAILURE;
    }

    fclose(f);
    sem_unlock();
    return E_SUCCESS;
}

int nvram_set_int(const char *key, const int val) {
    char path[PATH_MAX] = MOUNT_POINT;
    FILE *f;

    if (!key) {
        PRINT_MSG("%s\n", "NULL key!");
        return E_FAILURE;
    }

    PRINT_MSG("%s = %d\n", key, val);

    strncat(path, key, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);

    sem_lock();

    if ((f = fopen(path, "wb")) == NULL) {
        sem_unlock();
        PRINT_MSG("Unable to open key: %s!\n", path);
        return E_FAILURE;
    }

    if (fwrite(&val, sizeof(val), 1, f) != 1) {
        fclose(f);
        sem_unlock();
        PRINT_MSG("Unable to write value: %d to key: %s!\n", val, path);
        return E_FAILURE;
    }

    fclose(f);
    sem_unlock();
    return E_SUCCESS;
}

int nvram_set_default(void) {
    int ret = nvram_set_default_builtin();
    PRINT_MSG("Loading built-in default values = %d!\n", ret);
    if (!is_load_env) firmae_load_env();

#define NATIVE(a, b) \
    if (!system(a)) { \
        PRINT_MSG("Executing native call to built-in function: %s (%p) = %d!\n", #b, b, b); \
    }

#define TABLE(a) \
    PRINT_MSG("Checking for symbol \"%s\"...\n", #a); \
    if (a) { \
        PRINT_MSG("Loading from native built-in table: %s (%p) = %d!\n", #a, a, nvram_set_default_table(a)); \
    }

#define PATH(a) \
    if (!access(a, R_OK)) { \
        PRINT_MSG("Loading from default configuration file: %s = %d!\n", a, foreach_nvram_from(a, (void (*)(const char *, const char *, void *)) nvram_set, NULL)); \
    }
#define FIRMAE_PATH(a) \
    if (firmae_nvram && !access(a, R_OK)) { \
        PRINT_MSG("Loading from default configuration file: %s = %d!\n", a, foreach_nvram_from(a, (void (*)(const char *, const char *, void *)) nvram_set, NULL)); \
    }
#define FIRMAE_PATH2(a) \
    if (firmae_nvram && !access(a, R_OK)) { \
        PRINT_MSG("Loading from default configuration file: %s = %d!\n", a, parse_nvram_from_file(a)); \
    }

    NVRAM_DEFAULTS_PATH
#undef FIRMAE_PATH2
#undef FIRMAE_PATH
#undef PATH
#undef NATIVE
#undef TABLE

    // /usr/etc/default in DGN3500-V1.1.00.30_NA.zip
    FILE *file;
    if (firmae_nvram &&
        !access("/firmadyne/nvram_files", R_OK) &&
        (file = fopen("/firmadyne/nvram_files", "r")))
    {
        char line[256];
        char *nvram_file;
        char *file_type;
        while (fgets(line, sizeof line, file) != NULL)
        {
            line[strlen(line) - 1] = '\0';
            nvram_file = strtok(line, " ");
            file_type = strtok(NULL, " ");
            file_type = strtok(NULL, " ");

            if (access(nvram_file, R_OK) == -1)
                continue;

            if (strstr(file_type, "ELF") == NULL)
                PRINT_MSG("Loading from default configuration file: %s = %d!\n", nvram_file, parse_nvram_from_file(nvram_file));
        }
    }

    return nvram_set_default_image();
}

static int nvram_set_default_builtin(void) {
    int ret = E_SUCCESS;
    char nvramKeyBuffer[100]="";
    int index=0;
    if (!is_load_env) firmae_load_env();

    PRINT_MSG("%s\n", "Setting built-in default values!");

#define ENTRY(a, b, c) \
    if (b(a, c) != E_SUCCESS) { \
        PRINT_MSG("Unable to initialize built-in NVRAM value %s!\n", a); \
        ret = E_FAILURE; \
    }

#define FIRMAE_ENTRY(a, b, c) \
    if (firmae_nvram && b(a, c) != E_SUCCESS) { \
        PRINT_MSG("Unable to initialize built-in NVRAM value %s!\n", a); \
        ret = E_FAILURE; \
    }

#define FIRMAE_FOR_ENTRY(a, b, c, d, e) \
    index = d; \
    if (firmae_nvram) { \
        while (index != e) { \
            snprintf(nvramKeyBuffer, 0x1E, a, index++); \
            ENTRY(nvramKeyBuffer, b, c) \
        } \
    }

    NVRAM_DEFAULTS
#undef FIRMAE_FOR_ENTRY
#undef FIRMAE_ENTRY
#undef ENTRY

    return ret;
}

static int nvram_set_default_image(void) {
    PRINT_MSG("%s\n", "Copying overrides from defaults folder!");
    sem_lock();
    system("/bin/cp "OVERRIDE_POINT"* "MOUNT_POINT);
    sem_unlock();
    return E_SUCCESS;
}

static int nvram_set_default_table(const char *tbl[]) {
    size_t i = 0;

    while (tbl[i]) {
        nvram_set(tbl[i], tbl[i + 1]);
        i += (tbl[i + 2] != 0 && tbl[i + 2] != (char *) 1) ? 2 : 3;
    }

    return E_SUCCESS;
}

int nvram_unset(const char *key) {
    char path[PATH_MAX] = MOUNT_POINT;

    if (!key) {
        PRINT_MSG("%s\n", "NULL key!");
        return E_FAILURE;
    }

    PRINT_MSG("%s\n", key);

    strncat(path, key, ARRAY_SIZE(path) - ARRAY_SIZE(MOUNT_POINT) - 1);

    sem_lock();
    if (unlink(path) == -1 && errno != ENOENT) {
        sem_unlock();
        PRINT_MSG("Unable to unlink %s!\n", path);
        return E_FAILURE;
    }
    sem_unlock();
    return E_SUCCESS;
}

int nvram_match(const char *key, const char *val) {
    if (!key) {
        PRINT_MSG("%s\n", "NULL key!");
        return E_FAILURE;
    }

    if (nvram_get_buf(key, temp, BUFFER_SIZE) != E_SUCCESS) {
        return !val ? E_SUCCESS : E_FAILURE;
    }

    PRINT_MSG("%s (%s) ?= \"%s\"\n", key, temp, val);

    if (strncmp(temp, val, BUFFER_SIZE)) {
        PRINT_MSG("%s\n", "false");
        return E_FAILURE;
    }

    PRINT_MSG("%s\n", "true");
    return E_SUCCESS;
}

int nvram_invmatch(const char *key, const char *val) {
    if (!key) {
        PRINT_MSG("%s\n", "NULL key!");
        return E_FAILURE;
    }

    PRINT_MSG("%s ~?= \"%s\"\n", key, val);
    return !nvram_match(key, val);
}

int nvram_commit(void) {
    sem_lock();
    sync();
    sem_unlock();

    return E_SUCCESS;
}

int parse_nvram_from_file(const char *file)
{
    FILE *f;
    char *buffer;
    int fileLen=0;

    if((f = fopen(file, "rb")) == NULL){
        PRINT_MSG("Unable to open file: %s!\n", file);
        return E_FAILURE;
    }

    /* Get file length */
    fseek(f, 0, SEEK_END);
    fileLen = ftell(f);
    rewind(f);

    /* Allocate memory */
    buffer = (char*)malloc(sizeof(char) *fileLen);
    fread(buffer, 1, fileLen, f);
    fclose(f);

    /* split the buffer including null byte */
    #define LEN 1024
    int i=0,j=0,k=0; int left = 1;
    char *key="", *val="";
    char larr[LEN]="", rarr[LEN]="";

    for(i=0; i < fileLen; i++)
    {
        char tmp[4];
        sprintf(tmp, "%c", *(buffer+i));

        if (left==1 && j<LEN)
            larr[j++] = tmp[0];
        else if(left==0 && k<LEN)
            rarr[k++] = tmp[0];

        if(!memcmp(tmp,"=",1)){
            left=0;
            larr[j-1]='\0';
        }
        if (!memcmp(tmp,"\x00",1)){
            key = larr; val = rarr;
            nvram_set(key, val);
            j=0; k=0; left=1;
            memset(larr, 0, LEN); memset(rarr, 0, LEN);
        }
    }
    return E_SUCCESS;
}

#ifdef FIRMAE_KERNEL
//DIR-615I2, DIR-615I3, DIR-825C1 patch
int VCTGetPortAutoNegSetting(char *a1, int a2){
    PRINT_MSG("%s\n", "Dealing wth ioctl ...");
    return 0;
}

// netgear 'Rxxxx' series patch to prevent infinite loop in httpd
int agApi_fwGetFirstTriggerConf(char *a1)
{
    PRINT_MSG("%s\n", "agApi_fwGetFirstTriggerConf called!");
    return 1;
}

// netgear 'Rxxxx' series patch to prevent infinite loop in httpd
int agApi_fwGetNextTriggerConf(char *a1)
{
    PRINT_MSG("%s\n", "agApi_fwGetNextTriggerConf called!");
    return 1;
}
#endif

// Hack to use static variables in shared library
#include "alias.c"
