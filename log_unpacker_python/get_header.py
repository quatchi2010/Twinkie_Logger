import struct
from pathlib import Path

ctrl_msg_str = [
	"",
	"GOOD_CRC",
	"GOTO_MIN",
	"ACCEPT",
	"REJECT",
	"PING",
	"PS_RDY",
	"GET_SRC_CAP",
	"GET_SNK_CAP",
	"DR_SWAP",
	"PR_SWAP",
	"VCONN_SWAP",
	"WAIT",
	"SOFT_RESET",
	"DATA_RESET",
	"DATA_RESET_COMPLETE",
	"NOT_SUPPORTED",
	"GET_SRC_CAP_EXT",
	"GET_STATUS",
	"FR_SWAP",
	"GET_PPS_STATUS",
	"GET_COUNTRY_CODES",
	"GET_SNK_CAP_EXT"
]

data_msg_str = [
	"",
	"SRC_CAP",
	"REQUEST",
	"BIST",
	"SNK_CAP",
	"BATTERY_STATUS",
	"ALERT",
	"GET_COUNTRY_INFO",
	"ENTER_USB",
	"",
	"",
	"",
	"",
	"",
	"",
	"VDM"
]

ext_msg_str = [
	"",
	"EXT_SRC_CAP",
	"EXT_STATUS",
	"EXT_GET_BATTERY_CAP",
	"EXT_BATTERY_CAP",
	"EXT_GET_MANUF_INFO",
	"EXT_MANUF_INFO",
	"EXT_SECURITY_REQUEST",
	"EXT_SECURITY_RESPONSE",
	"EXT_FW_UPDATE_REQUEST",
	"EXT_FW_UPDATE_RESPONSE",
	"EXT_PPS_STATUS",
	"EXT_COUNTRY_INFO",
	"EXT_COUNTRY_CODES"
]

type_str = [
	"SOP  ",
	"SOP' ",
	"SOP''",
	"DBG' ",
	"DBG''",
	"HRST ",
	"CRST ",
	"BIST "
]

rev_str = [
	"V1.0",
	"V2.0",
	"V3.0"
]

prole_str = [
	"SNK",
	"SRC"
]

cable_str = [
	"DFP/UFP",
	"Cable  "
]

drole_str = [
	"UFP",
	"DFP"
]

pol_str = [
	"---",
	"CC1",
	"CC2"
]

def format_date_num(num):
	return f'{int(num / 1000 / 60 / 60 / 24)},'

def format_time_num(num):
	return f'{int(num / 1000 / 60 / 60 % 24):02d}:{int(num / 1000 / 60 % 60):02d}:{int(num / 1000 % 60):02d}:{int(num % 1000):03d}'

def format_date_time_num(num):
	return format_date_num(num) + " " + format_time_num(num)

def format_cc(cc_line):
	return pol_str[cc_line]

def format_sop_role(sop, role):
	p_role = role >> 3
	spec = (role >> 1) & int("11", 2)
	d_role = role & 1
	
	ret = rev_str[spec] + " " + type_str[sop]
	
	if (sop == 1 or sop == 2):
		ret = ret + cable_str[p_role]
	else:
		ret = ret + prole_str[p_role] + ":" + drole_str[d_role]
	
	return ret
		

def format_msg(extended, num_of_data_obj, msg_typ):
     if (num_of_data_obj == 0):
     	return "ctrl msg: " + ctrl_msg_str[msg_typ]
     elif (extended != 0):
     	return "extd msg: " + ext_msg_str[msg_typ]
     else:
     	return "data msg: " + data_msg_str[msg_typ]

class pd_packet_header:
	def __init__(self, index, time, cc_line, sop, msg_typ, role, msg_id, num_d_obj, ext):
		self.index = index
		self.time = time
		self.cc_line = cc_line
		self.sop = sop
		self.msg_typ = msg_typ
		self.role = role
		self.msg_id = msg_id
		self.num_d_obj = num_d_obj
		self.ext = ext
	
	def __str__(self):
		return str((self.index, format_time_num(self.time), format_cc(self.cc_line), format_sop_role(self.sop, self.role), format_msg(self.ext, self.num_d_obj, self.msg_typ), self.msg_id))

class twinkie_header:
	def __init__(self, h_tuple):
		self.time = h_tuple[0]
		self.cc1_v = h_tuple[1]
		self.cc2_v = h_tuple[2]
		self.cc2_c = h_tuple[3]
		self.vbus_v = h_tuple[4]
		self.vbus_c = h_tuple[5]
		self.packet_bin = h_tuple[6]
		self.data_length = h_tuple[7]

	def __str__(self):
		return format_time_num(self.time) + f', CC1 = {self.cc1_v}, CC2 = {self.cc2_v}, VBUS voltage = {self.vbus_v}, VBUS current = {self.vbus_c}'

def get_header_list(path_str):
	data = Path(path_str).read_bytes()
	head = []
	pd = []

	for i in range(int(len(data) / 512)):
		header = struct.unpack('IHHHHHHHH', data[512*i:512*i+20])
		head.append(twinkie_header(header))
	     
		if (header[7] != 0):
			sop = (header[6] >> 12) & int("1111", 2)
			cc_line = (header[6] >> 4) & int("11", 2)
			
			pd_header = struct.unpack('H', data[512*i+20:512*i+22])
			msg_typ = pd_header[0] & int("11111", 2)
			role = (pd_header[0] >> 5) & int("1111", 2)
			msg_id = (pd_header[0] >> 9) & int("111", 2)
			num_d_obj = (pd_header[0] >> 12) & int("111", 2)
			ext = pd_header[0] >> 15
			
			pd.append(pd_packet_header(i, header[0], cc_line, sop, msg_typ, role, msg_id, num_d_obj, ext))

	return (head, pd)



