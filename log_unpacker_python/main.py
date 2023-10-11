import matplotlib.pyplot as plt
import sys
from get_header import *

(header, pd_msg) = get_header_list(sys.argv[1])
xval = []
xticks = []
for i in range(len(header)):
	if (i % 2000 == 0):
		xval.append(header[i].time)
		xticks.append(format_time_num(header[i].time))

plt.xticks(xval, xticks)
plt.plot([x.time for x in header],[x.vbus_v for x in header])
plt.plot([x.time for x in header],[x.vbus_c for x in header])
plt.show()
