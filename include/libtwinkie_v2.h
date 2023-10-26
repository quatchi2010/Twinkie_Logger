#ifndef _LIBTWINKIE_V2_H_
#define _LIBTWINKIE_V2_H_

#include <vector>

#include "device.h"

class LibTwinkieV2 {
 public:
  LibTwinkieV2();
  ~LibTwinkieV2();
  int init();
  void xray();

 private:
  std::vector<Device *> devices;
};

#endif  // _LIBTWINKIE_V2_H_
