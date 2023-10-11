#ifndef _DEVICE_H_
#define _DEVICE_H_
#include <stdbool.h>

struct Twinkie;

struct Twinkie * open_twinkie(char *uart0, char *uart1);
void close_twinkie(struct Twinkie *device);
bool is_snooper(struct Twinkie *device);
int write_twinkie_shell(struct Twinkie *device, char *buf, int num);
int read_twinkie_snooper(struct Twinkie *device, char *buf, int num);

#endif // _DEVICE_H_
