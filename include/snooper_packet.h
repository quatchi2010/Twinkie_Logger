#ifndef _SNOOPER_PACKET_H_
#define _SNOOPER_PACKET_H_

#include <stdint.h>

#define SNOOPER_PACKET_SIZE (sizeof(struct SnooperPacket))
#define SNOOPER_MAX_DATA_SIZE 488

struct PacketType {
  uint16_t unused1 : 4;
  uint16_t polarity : 2;
  uint16_t lost : 1;
  uint16_t partial : 1;
  uint16_t version : 4;
  uint16_t type : 4;
};

struct SnooperPacket {
  uint32_t sequence;
  uint16_t cc1_voltage;
  uint16_t cc2_voltage;
  uint16_t vconn_current;
  uint16_t vbus_voltage;
  uint16_t vbus_current;
  struct PacketType type;
  uint16_t data_len;
  uint16_t unused;
  uint8_t data[SNOOPER_MAX_DATA_SIZE];
  uint32_t crc;
};

#endif /* _SNOOPER_PACKET_H_ */
