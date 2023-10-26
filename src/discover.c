#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#define DEVICE_PATH "/dev"
#define DEVICE_NAME "twinkiev2-"
#define NAME_SIZE 20
#define DIR_AND_NAME_SIZE 25
#define MAX_NUM_DEVICES 4

static int found;
static char device_name[MAX_NUM_DEVICES * 2][NAME_SIZE];

struct Device {
  char uart0[DIR_AND_NAME_SIZE];
  char uart1[DIR_AND_NAME_SIZE];
};

static int device_num;
static struct Device devices[MAX_NUM_DEVICES];

static int cmp_device_name(const void *a, const void *b) {
  return strcmp((char const *)a, (char const *)b);
}

int discover_devices(void) {
  DIR *dp;
  struct dirent *dirp;
  int i;

  dp = opendir(DEVICE_PATH);
  if (dp == NULL) {
    return -1;
  }

  found = 0;
  for (int i = 0; i < MAX_NUM_DEVICES * 2; i++) {
    device_name[i][0] = 0;
  }

  while ((dirp = readdir(dp)) != NULL) {
    if (strncmp(DEVICE_NAME, dirp->d_name, strlen(DEVICE_NAME)) == 0) {
      strcpy(device_name[found], dirp->d_name);
      found++;
    }
  }

  closedir(dp);

  qsort(device_name, found, NAME_SIZE, cmp_device_name);

  device_num = 0;
  for (int i = 0; i < found; i += 2) {
    sprintf(devices[device_num].uart0, "%s/%s", DEVICE_PATH, device_name[i]);
    sprintf(devices[device_num].uart1, "%s/%s", DEVICE_PATH,
            device_name[i + 1]);
    device_num++;
  }

  return device_num;
}

int get_num_device(void) { return device_num; }

int get_device(unsigned int d, char *uart0, char *uart1) {
  if (uart0 == NULL || uart1 == NULL || (d >= device_num)) {
    return -1;
  }

  strcpy(uart0, devices[d].uart0);
  strcpy(uart1, devices[d].uart1);

  return 0;
}
