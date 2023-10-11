#include "device.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/file.h>

struct Twinkie {
	/* Console File descriptor */
	int fd_uart0;
	struct termios tty_uart0;
	/* Snooper File descriptor */
	int fd_uart1;
	struct termios tty_uart1;
} twinkie;

struct Twinkie * open_twinkie(char *uart0, char *uart1)
{
	struct Twinkie *device;

	if (uart0 == NULL) {
		return NULL;
	}

	device = (struct Twinkie *)malloc(sizeof (struct Twinkie));
	if (device == NULL) {
		return NULL;
	}

	device->fd_uart0 = open(uart0, O_RDWR | O_NOCTTY);
	if (device->fd_uart0 < 1) {
		close_twinkie(device);
		return NULL;
	}

	if (flock(device->fd_uart0, LOCK_EX | LOCK_NB) == -1) {
		close_twinkie(device);
		return NULL;
	}

	if (tcgetattr(device->fd_uart0, &device->tty_uart0) != 0) {
		close_twinkie(device);
		return NULL;
	}

	device->tty_uart0.c_cflag &= ~PARENB;
	device->tty_uart0.c_cflag &= ~CSTOPB;
	device->tty_uart0.c_cflag &= ~CSIZE;
	device->tty_uart0.c_cflag |= CS8;
	device->tty_uart0.c_cflag &= ~CRTSCTS;
	device->tty_uart0.c_cflag |= CREAD | CLOCAL;

	device->tty_uart0.c_lflag &= ~ICANON;
	device->tty_uart0.c_lflag &= ~ECHO;
	device->tty_uart0.c_lflag &= ~ECHOE;
	device->tty_uart0.c_lflag &= ~ECHONL;
	device->tty_uart0.c_lflag &= ~ISIG;

	device->tty_uart0.c_iflag &= ~(IXON | IXOFF | IXANY);
	device->tty_uart0.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL);

	device->tty_uart0.c_cc[VTIME] = 10;
	device->tty_uart0.c_cc[VMIN] = 0;

	cfsetispeed(&device->tty_uart0, B115200);

	if (tcsetattr(device->fd_uart0, TCSANOW, &device->tty_uart0) != 0) {
		close_twinkie(device);
		return NULL;
	}


#if 1
	device->fd_uart1 = open(uart1, O_RDWR | O_NOCTTY);//O_RDONLY);
	if (device->fd_uart1 < 1) {
		close_twinkie(device);
		return NULL;
	}

	if (flock(device->fd_uart1, LOCK_EX | LOCK_NB) == -1) {
		close_twinkie(device);
		return NULL;
	}

	if (tcgetattr(device->fd_uart1, &device->tty_uart1) != 0) {
		close_twinkie(device);
		return NULL;
	}

	device->tty_uart1.c_cflag &= ~PARENB;
	device->tty_uart1.c_cflag &= ~CSTOPB;
	device->tty_uart1.c_cflag &= ~CSIZE;
	device->tty_uart1.c_cflag |= CS8;
	device->tty_uart1.c_cflag &= ~CRTSCTS;
	device->tty_uart1.c_cflag |= CREAD | CLOCAL;

	device->tty_uart1.c_lflag &= ~ICANON;
	device->tty_uart1.c_lflag &= ~ECHO;
	device->tty_uart1.c_lflag &= ~ECHOE;
	device->tty_uart1.c_lflag &= ~ECHONL;
	device->tty_uart1.c_lflag &= ~ISIG;

	device->tty_uart1.c_iflag &= ~(IXON | IXOFF | IXANY);
	device->tty_uart1.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL);

	device->tty_uart1.c_cc[VTIME] = 10;
	device->tty_uart1.c_cc[VMIN] = 0;

	cfsetispeed(&device->tty_uart1, B115200);

	if (tcsetattr(device->fd_uart1, TCSANOW, &device->tty_uart1) != 0) {
		close_twinkie(device);
		return NULL;
	}
#endif
	return device;
}

void close_twinkie(struct Twinkie *device)
{
	if (device == NULL) {
		return;
	}

	if (device->fd_uart0 > -1) {
		close(device->fd_uart0);
	}

	if (device->fd_uart1 > -1) {
		close(device->fd_uart1);
	}

	free(device);
}

bool is_snooper(struct Twinkie *device)
{
	char buf[1];

	if (device == NULL) {
		return false;
	}

	write(device->fd_uart0, "\r\n", 2);
	if (read(device->fd_uart0, buf, 1)) {
		return false;
	}

	return true;
}

int write_twinkie_shell(struct Twinkie *device, char *buf, int num)
{
	if (device == NULL || buf == NULL) {
		return -1;
	}

	return write(device->fd_uart1, buf, num);
}

#if 0
int read_twinkie_shell(struct Twinkie *device, char *buf, int num)
{
	if (device == NULL || buf == NULL) {
		return -1;
	}

	return read(device->fd_uart1, buf, num);
}
#endif

int read_twinkie_snooper(struct Twinkie *device, char *buf, int num)
{
	if (device == NULL || buf == NULL) {
		return -10;
	}

	return read(device->fd_uart0, buf, num);
}
