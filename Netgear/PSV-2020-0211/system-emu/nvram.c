/* custom_nvram.c
 *
 * Emulates the Netgear 6250/6400's nvram functions
 * by reading key=value pairs from /tmp/nvram.ini
 *
 * by Saumil Shah @therealsaumil
 */

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>

// ./buildroot-2016.11.2/output/host/usr/bin/arm-buildroot-linux-uclibcgnueabi-gcc -shared -fPIC -o nvram.so nvram.c

#define NVRAM_FILE      "/tmp/nvram.ini"
#define NVRAM_ENTRIES   2000
#define NVRAM_KEYLEN    128
#define NVRAM_LINE      256

static int counter = 0;
static int nvram_init = 0;
static int nvram_entries = 0;

// key-value 数组
static char key[NVRAM_ENTRIES][NVRAM_KEYLEN];
static char value[NVRAM_ENTRIES][NVRAM_KEYLEN];

// 函数声明
static int custom_nvram_init();
int read_nvram();
static int (*real_system)(const char *command) = NULL;
static FILE *(*real_fopen)(const char *filename, const char *mode) = NULL;
static int (*real_open)(const char *pathname, int flags) = NULL;

// function will be called only once when any of the acosNvram_* functions get invoked
static int custom_nvram_init() {
   nvram_init = 1;
   printf("custom_nvram initialised\n");
   nvram_entries = read_nvram();
   printf("Read %d entries from %s\n", nvram_entries, NVRAM_FILE);
}

// 将 nvram.ini 读到一个全局数组
int read_nvram() {
   int i = 0;
   FILE *fp;
   char line[NVRAM_LINE], *k, *v;

   fp = fopen(NVRAM_FILE, "r");
   if(fp == (FILE *) NULL) {
      printf("Cannot open %s\n", NVRAM_FILE);
      exit(-1);
   }

   while(!feof(fp)) {
      fgets(line, NVRAM_LINE, fp);
      k = strtok(line, "=");
      v = strtok(NULL, "\n");
      memset(key[i], '\0', NVRAM_KEYLEN);
      memset(value[i], '\0', NVRAM_KEYLEN);
      if(k != NULL)
         strncpy(key[i], k, NVRAM_KEYLEN - 1);
      if(v != NULL)
         strncpy(value[i], v, NVRAM_KEYLEN - 1);

      printf("[nvram %d] %s = %s\n", i, key[i], value[i]);
      i++;

      if(i >= NVRAM_ENTRIES) {
         printf("** WARNING: nvram entries exceeds %d\n", NVRAM_ENTRIES);
         break;
      }
   }

   fclose(fp);
   return(i);
}

char *nvram_get(char *k) {
   char *v = "";
   int i;

   for(i = 0; i < nvram_entries; i++) {
      if(strcmp(key[i], k) == 0) {
         //v = strdup(value[i]);
         v = value[i];
         break;
      }
   }
   return(v);
}

int nvram_set(char *k, char *v) {
   int i;

   for(i = 0; i < nvram_entries; i++) {
      if(strcmp(key[i], k) == 0) {
         strncpy(value[i], v, NVRAM_KEYLEN - 1);
         break;
      }
   }
   return(i);
}

// hook system()
int system(const char *command) {
   int r;
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   real_system = dlsym(RTLD_NEXT, "system");
   r = real_system(command);
   printf("system('%s') = %d\n", command, r);
   return(r);
}

// hook fopen()
FILE *fopen(const char *filename, const char *mode) {
   FILE *fp;
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   real_fopen = dlsym(RTLD_NEXT, "fopen");
   fp = real_fopen(filename, mode);
   printf("fopen('%s', '%s') = 0x%08x\n", filename, mode, (unsigned int) fp);
   return(fp);
}

// hook open()
int open(const char *pathname, int flags) {
   int r;
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   real_open = dlsym(RTLD_NEXT, "open");
   r = real_open(pathname, flags);
   printf("open('%s', %d) = %d\n", pathname, flags, r);
   return(r);
}

/* intercepted libnvram.so functions */
char *acosNvramConfig_get(char *k) {
   char *v = "";

   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address

   if(!nvram_init)
      custom_nvram_init();

   v = nvram_get(k);

   printf("acosNvramConfig_get('%s') = '%s'\n", k, v);
   return(v);
}

int acosNvramConfig_set(char *k, char *v) {
   int i;

   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address

   if(!nvram_init)
      custom_nvram_init();

   i = nvram_set(k, v);

   printf("[nvram %d] acosNvramConfig_set('%s', '%s')\n", i, k, v);
   return(0);
}

void acosNvramConfig_read(char *k, char *r, int len) {
   char* v = "";

   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address

   if(!nvram_init)
      custom_nvram_init();

   v = nvram_get(k);

   strncpy(r, v, len);
   printf("acosNvramConfig_read('%s', '%s', %d)\n", k, r, len);
}

int acosNvramConfig_match(char *k, char *v) {
   // return 0 (False) by default
   int r = 0;
   char *s;

   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address

   if(!nvram_init)
      custom_nvram_init();

   s = nvram_get(k);

   if(strcmp(s, v) == 0)
      r = 1;

   printf("acosNvramConfig_match('%s', '%s') = %d\n", k, v, r);
   return(r);
}

/* intercepted other libacos_shared.so functions */

int agApi_fwServiceAdd(char *k, int a, int b, int c) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   counter++;
   printf("agApi_fwServiceAdd('%s', %d, %d, %d) = %d\n", k, a, b, c, counter);
   return(counter);
}

int agApi_fwURLFilterEnableTmSch_Session2(int x) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwURLFilterEnableTmSch_Session2(%d) = 0\n", x);
   return(0);
}

int agApi_fwURLFilterEnable_Session2(int x) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwURLFilterEnable_Session2(%d) = 0\n", x);
   return(0);
}

int agApi_tmschDelConf(char *k) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_tmschDelConf('%s') = 0\n", k);
   return(0);
}

int agApi_tmschAddConf(char *a, char *b, char *c, char *d, char *e, int f, int g, int h) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_tmschAddConf('%s', '%s', '%s', '%s', '%s', %d, %d, %d)\n", a, b, c, d, e, f, g, h);
   return(0);
}

int agApi_tmschDelConf_Session2(char *k) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_tmschDelConf_Session2('%s') = 0\n", k);
   return(0);
}

int agApi_tmschAddConf_Session2(char *a, char *b, char *c, char *d, char *e, int f, int g, int h) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_tmschAddConf_Session2('%s', '%s', '%s', '%s', '%s', %d, %d, %d)\n", a, b, c, d, e, f, g, h);
   return(0);
}

int agApi_fwBlkServModAction(char *k) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwBlkServModAction('%s') = 0\n", k);
   return(0);
}

int agApi_fwBlkServModAction_Session2(char *k) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwBlkServModAction('%s') = 0\n", k);
   return(0);
}

int agApi_fwEchoRespSet(int x) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwEchoRespSet(%d) = 1\n", x);
   return(1);
}

int agApi_fwURLFilterEnable(int x) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwURLFilterEnable(%d) = 0\n", x);
   return(0);
}

int agApi_fwURLFilterEnableTmSch() {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwURLFilterEnableTmSch() = 0\n");
   return(0);
}

int agApi_fwGetAllServices(char *k, int a) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwGetAllServices('%s', %d) = %d\n", k, a, counter);
   return(counter);
}

void agApi_fwDelTriggerConf2(char *k) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwDelTriggerConf2('%s')\n", k);
}

int agApi_fwGetNextTriggerConf(int a) {
   printf("[0x%08x] ", __builtin_return_address(0));  // get caller's address
   printf("agApi_fwGetNextTriggerConf(0x%08x) = 1\n", a);
   return(1);
}
