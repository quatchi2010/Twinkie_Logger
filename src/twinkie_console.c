#include <getopt.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "device.h"
#include "discover.h"
#include "log.h"
#include "snooper_packet.h"
#include "snooper_stream.h"

static uint8_t tmpbuf[SNOOPER_PACKET_SIZE];
static char *dir_name;

void *read_f(void *p) {
  struct Twinkie *t = (struct Twinkie *)p;
  int r;
  int k = 0;

  while (read_twinkie_snooper(t, tmpbuf, SNOOPER_PACKET_SIZE)) {
  }

  while (1) {
    r = read_twinkie_snooper(t, tmpbuf, SNOOPER_PACKET_SIZE - k);
    k += r;
    if (k == SNOOPER_PACKET_SIZE) k = 0;
    if (r > 0) {
      stream_write(tmpbuf, r);
    }
  }
  return 0;
}

static uint8_t buf[512];

void *read_d(void *p) {
  struct Twinkie *t = (struct Twinkie *)p;
  int r;
  int ret = 0;
  while (ret == 0) {
    if (stream_read(buf)) {
      //			ret = log_packet((struct SnooperPacket const
      //*)buf);
      log_file(buf);
    }
  }
  return 0;
}

void *control_d(void *p) {
  struct Twinkie *t = (struct Twinkie *)p;
  char start[6] = {'s', 't', 'a', 'r', 't', '\n'};
  char stop[5] = {'s', 't', 'o', 'p', '\n'};
  int ret = 0;
  time_t timer;
  time(&timer);
  struct tm *tm = localtime(&timer);
  char file_name[40];

  char dir_command[25];
  sprintf(dir_command, "mkdir %s", dir_name);
  system(dir_command);

  /*
          char speed_command[20];
          sprintf(speed_command, "sleep_time %i\n", 500); //time between packets
          ret = write_twinkie_shell(t, speed_command, 20);
  */

  sleep(2);  // wait 2 second to allow the stream buffer to clear
  ret = write_twinkie_shell(t, start, 6);
  bool file_is_open = false;
  do {
    file_is_open = !file_is_open;
    if (file_is_open) {
      time(&timer);
      tm = localtime(&timer);
      /* alternatively read file name from something */
      sprintf(file_name, "./%s/%d_%d_%d_%d_%d_%d.bin", dir_name,
              tm->tm_year + 1900, tm->tm_mon, tm->tm_mday, tm->tm_hour,
              tm->tm_min, tm->tm_sec);
      file_open(file_name);
    } else {
      file_close();
    }
  } while (
      getchar());  // The condition for waiting for the next input goes here.
}

void print_usage(FILE *stream, int exit_code) {}

int main(int argc, char **argv) {
  struct Twinkie *t;
  int r;
  pthread_t thread1, thread2, thread3;
  char uart0[25], uart1[25];

  r = discover_devices();
  for (int i = 0; i < r; i++) {
    get_device(i, uart0, uart1);
  }

  t = open_twinkie((char *)uart0, (char *)uart1);
  if (t == NULL) {
    printf("ERROR1\n");
    return -1;
  }

  if (is_snooper(t) == false) {
    close_twinkie(t);
    t = open_twinkie((char *)uart1, (char *)uart0);
    if (t == NULL) {
      printf("ERROR2\n");
      return -1;
    }
    printf("shell: %s\n", uart0);
  } else {
    printf("shell: %s\n", uart1);
  }

  stream_init();
  dir_name = argv[1];

  pthread_create(&thread2, NULL, &read_f, (void *)t);
  pthread_create(&thread3, NULL, &read_d, (void *)t);
  pthread_create(&thread1, NULL, &control_d, (void *)t);

  while (1) {
    sleep(5);
  }

  close_twinkie(t);

  return 0;
}
