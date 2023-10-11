#ifndef _SNOOPER_STREAM_H_
#define _SNOOPER_STREAM_H_

#include <stdint.h>
#include <stdbool.h>

void stream_init(void);
int stream_write(const uint8_t const * data, const uint32_t len);
bool stream_read(uint8_t *buf);
uint8_t const * stream_get_data(void);
void stream_reset(void);

#endif /* _SNOOPER_STREAM_H_ */
