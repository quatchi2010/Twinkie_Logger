#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "device.h"
#include "discover.h"
#include "snooper_packet.h"

#define MAX_STREAM_BUFFERS 20

static uint8_t stream_buffer[MAX_STREAM_BUFFERS][SNOOPER_PACKET_SIZE];
static uint32_t wsp;
static uint32_t rsp;
static uint32_t num;

int stream_init(void) {
  wsp = 0;
  rsp = 0;
  num = 0;
}

int stream_write(const uint8_t const *data, const uint32_t len) {
  if (data == NULL) {
    return -1;
  }

  memcpy(stream_buffer[wsp] + num, data, len);
  num += len;

  if (num == SNOOPER_PACKET_SIZE) {
    num = 0;
    wsp++;
    if (wsp == MAX_STREAM_BUFFERS) {
      wsp = 0;
    }
  }

  return 0;
}

bool stream_read(uint8_t *buf) {
  if (wsp != rsp) {
    memcpy(buf, stream_buffer[rsp], SNOOPER_PACKET_SIZE);
    rsp++;
    if (rsp == MAX_STREAM_BUFFERS) {
      rsp = 0;
    }
    return true;
  }
  return false;
}
