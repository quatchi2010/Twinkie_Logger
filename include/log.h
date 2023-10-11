#ifndef _LOG_H_
#define _LOG_H_

#include "snooper_packet.h"

enum log_verbose {
	VERBOSE_DEFAULT,
	VERBOSE_LOW,
	VERBOSE_MEDIUM,
	VERBOSE_HIGH
};

enum log_color {
	COLOR_OFF,
	COLOR_ON
};

void set_log_color(enum log_color o);
void set_log_verbose(enum log_verbose o);
int log_packet(struct SnooperPacket const * sp);
void log_raw(struct SnooperPacket const * sp);
void log_file(uint8_t *buf);
void file_open(char *file_name);
void file_close();

#endif /* _LOG_H_ */
