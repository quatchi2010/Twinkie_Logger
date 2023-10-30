#include "log.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

#include "crc32.h"
#include "snooper_packet.h"
#include "usbc_pd.h"
#include "usbc_tc.h"

#define COLOR_NORMAL "\033[0m"
#define COLOR_BLACK "\033[;30m"
#define COLOR_RED "\033[;31m"
#define COLOR_GREEN "\033[;32m"
#define COLOR_YELLOW "\033[;33m"
#define COLOR_BLUE "\033[;34m"
#define COLOR_MAGENTA "\033[;35m"
#define COLOR_CYAN "\033[;36m"
#define COLOR_WHITE "\033[;37m"

static bool color = true;
static enum log_verbose verbose;
static bool file_is_open = false;
FILE *file_ptr;

static uint16_t cc1_voltage;
static uint16_t cc2_voltage;
static uint16_t vconn_current;
static uint16_t vbus_voltage;
static uint16_t vbus_current;
static bool lost;
static bool partial;
static uint16_t version;
static uint16_t data_len;
static uint8_t const *data;

static bool show_rev;
static uint32_t crc_rec;
static uint32_t crc_cal;
static bool extended;
static uint32_t data_object_num;
static union pd_header header;

#define REV1_COLOR COLOR_RED
#define REV2_COLOR COLOR_YELLOW
#define REV3_COLOR COLOR_GREEN
static enum pd_rev_type rev;
static const char *rev_str[] = {"V1.0", "V2.0", "V3.0"};

static void log_rev(FILE *f) {
  if (show_rev) {
    if (color) {
      switch (rev) {
        case PD_REV10:
          fprintf(f, "%s", REV1_COLOR);
          break;
        case PD_REV20:
          fprintf(f, "%s", REV2_COLOR);
          break;
        case PD_REV30:
          fprintf(f, "%s", REV3_COLOR);
          break;
      }
    }

    fprintf(f, "%s", rev_str[rev]);

    if (color) {
      fprintf(f, "%s", COLOR_NORMAL);
    }
  } else {
    fprintf(f, "    ");
  }

  fprintf(f, " ");
}

#define SEQUENCE_COLOR COLOR_WHITE
static uint32_t sequence;
static void log_sequence(FILE *f) {
  if (color) {
    fprintf(f, "%s", SEQUENCE_COLOR);
  }

  fprintf(f, "S%08x", sequence);

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }

  fprintf(f, " ");
}

#define TYPE_COLOR COLOR_YELLOW
static enum pd_packet_type type;
static const char *type_str[] = {"SOP  ", "SOP' ", "SOP''", "DBG' ",
                                 "DBG''", "HRST ", "CRST ", "BIST "};

static void log_type(FILE *f) {
  if (color) {
    fprintf(f, "%s", TYPE_COLOR);
  }

  fprintf(f, "%s", type_str[type]);

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }

  fprintf(f, " ");
}

#define ROLE_COLOR COLOR_CYAN
static enum tc_power_role prole;
static const char *prole_str[] = {
    "SNK",
    "SRC",
};

static const char *cable_str[] = {
    "DFP/UFP",
    "Cable  ",
};

static enum tc_data_role drole;
static const char *drole_str[] = {"UFP", "DFP"};

static void log_role(FILE *f) {
  if (color) {
    fprintf(f, "%s", ROLE_COLOR);
  }

  if (type == PD_PACKET_SOP_PRIME || type == PD_PACKET_SOP_PRIME) {
    fprintf(f, "%s", cable_str[prole]);
  } else {
    fprintf(f, "%s:%s", prole_str[prole], drole_str[drole]);
  }

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }

  fprintf(f, " ");
}

#define POL_COLOR COLOR_WHITE
static enum tc_cc_polarity pol;
static const char *pol_str[] = {"---", "CC1", "CC2"};

static void log_pol(FILE *f) {
  if (color) {
    fprintf(f, "%s", POL_COLOR);
  }

  fprintf(f, "%s", pol_str[pol]);

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }

  fprintf(f, " ");
}

#define MSG_COLOR COLOR_MAGENTA
static uint8_t msgid;
static enum pd_ctrl_msg_type ctrl_msg;
static const char *ctrl_msg_str[] = {
    "",
    "GOOD_CRC\t\t",
    "GOTO_MIN\t\t",
    "ACCEPT\t\t",
    "REJECT\t\t",
    "PING\t\t",
    "PS_RDY\t\t",
    "GET_SRC_CAP\t",
    "GET_SNK_CAP\t",
    "DR_SWAP\t\t",
    "PR_SWAP\t\t",
    "VCONN_SWAP\t",
    "WAIT\t\t",
    "SOFT_RESET\t\t",
    "DATA_RESET\t\t",
    "DATA_RESET_COMPLETE\t",
    "NOT_SUPPORTED\t",
    "GET_SRC_CAP_EXT\t",
    "GET_STATUS\t\t",
    "FR_SWAP\t\t",
    "GET_PPS_STATUS\t\t",
    "GET_COUNTRY_CODES\t",
    "GET_SNK_CAP_EXT\t\t",
};

static enum pd_data_msg_type data_msg;
static const char *data_msg_str[] = {"",
                                     "SRC_CAP\t\t",
                                     "REQUEST\t\t",
                                     "BIST\t\t",
                                     "SNK_CAP\t\t",
                                     "BATTERY_STATUS\t\t",
                                     "ALERT\t\t",
                                     "GET_COUNTRY_INFO\t",
                                     "ENTER_USB\t\t",
                                     "",
                                     "",
                                     "",
                                     "",
                                     "",
                                     "",
                                     "VDM"};

static enum pd_ext_msg_type ext_msg;
static const char *ext_msg_str[] = {
    "",
    "EXT_SRC_CAP\t\t",
    "EXT_STATUS\t\t",
    "EXT_GET_BATTERY_CAP\t",
    "EXT_BATTERY_CAP\t\t",
    "EXT_GET_MANUF_INFO\t",
    "EXT_MANUF_INFO\t\t",
    "EXT_SECURITY_REQUEST\t",
    "EXT_SECURITY_RESPONSE\t",
    "EXT_FW_UPDATE_REQUEST\t",
    "EXT_FW_UPDATE_RESPONSE\t",
    "EXT_PPS_STATUS\t\t",
    "EXT_COUNTRY_INFO\t",
    "EXT_COUNTRY_CODES\t",
};

static const char *structured_vdm_command_str[] = {
    "",           "DiscID\t",   "DiscSVIDS\t", "DiscMODES\t", "EnterMODE\t",
    "ExitMODE\t", "ATTENTION\t"};

static const char *unstructured_vdm_command_str = "CUSTOM\t\t";

static void log_vdm(FILE *f) {
  union structured_vdm_header v;

  v.raw_value = *(uint32_t *)(data + 2);

  if (v.type == 1) {
    fprintf(f, "[%d]%s:%s", msgid, data_msg_str[data_msg],
            structured_vdm_command_str[v.command]);
  } else {
    fprintf(f, "[%d]%s:%s", msgid, data_msg_str[data_msg],
            unstructured_vdm_command_str);
  }
}

static void log_msg(FILE *f) {
  if (color) {
    fprintf(f, "%s", MSG_COLOR);
  }

  if (ctrl_msg) {
    fprintf(f, "[%d]%s", msgid, ctrl_msg_str[ctrl_msg]);
  } else if (data_msg) {
    if (data_msg == PD_DATA_VENDOR_DEF) {
      log_vdm(f);
    } else {
      fprintf(f, "[%d]%s", msgid, data_msg_str[data_msg]);
    }
  } else {
    fprintf(f, "[%d]%s", msgid, ext_msg_str[ext_msg]);
  }

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }

  fprintf(f, " ");
}

#define HEADER_COLOR COLOR_WHITE
static void log_header(FILE *f) {
  if (color) {
    fprintf(f, "%s", HEADER_COLOR);
  }

  fprintf(f, "H=%04x", header.raw_value);

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }

  fprintf(f, " ");
}

#define CRC_COLOR COLOR_MAGENTA
#define DATA_COLOR COLOR_GREEN
static void log_data(FILE *f) {
  uint32_t *obj;

  fprintf(f, "<");
  log_type(f);
  log_header(f);

  if (color) {
    fprintf(f, "%s", DATA_COLOR);
  }

  if (data_object_num > 0) {
    if (extended) {
      obj = (uint32_t *)(data + 4);
    } else {
      obj = (uint32_t *)(data + 2);
    }

    for (int i = 0; i < data_object_num; i++) {
      fprintf(f, "0x%08x ", obj[i]);
    }
  }

  if (color) {
    fprintf(f, "%s", CRC_COLOR);
  }

  fprintf(f, "CRC=0x%08x>\n", crc_cal);

  if (color) {
    fprintf(f, "%s", COLOR_NORMAL);
  }
}

static void process_header(void) {
  header.raw_value = *(uint16_t *)data;

  drole = header.port_data_role;
  prole = header.port_power_role;
  msgid = header.message_id;
  data_object_num = header.number_of_data_objects;
  extended = header.extended;

  show_rev = false;
  if (header.message_type != PD_CTRL_GOOD_CRC || data_object_num > 0) {
    show_rev = true;
    rev = header.specification_revision;
  }

  ctrl_msg = 0;
  ext_msg = 0;
  data_msg = 0;

  if (data_object_num == 0) {
    ctrl_msg = header.message_type;
  } else {
    if (extended) {
      ext_msg = header.message_type;
    } else {
      data_msg = header.message_type;
    }
  }
}

void set_log_color(enum log_color o) {
  if (o) {
    color = true;
  } else {
    color = false;
  }
}

void set_log_verbose(enum log_verbose o) { verbose = o; }

void log_raw(struct SnooperPacket const *sp) {
  uint16_t *hd = (uint16_t *)sp->data;
  uint32_t *pd = (uint32_t *)(sp->data + 2);

  data = sp->data;
  data_len = sp->data_len;  //(data_object_num * 4) + 2;
  sequence = sp->sequence;
  process_header();

  printf("%i: ", sequence);

  for (int i = 0; i < 5; i++) {
    printf("%08x ", pd[i]);
  }
  printf("\n");
}

void dump_packet(struct SnooperPacket const *sp) {
  uint32_t *packet = (uint32_t *)sp;

  for (int i = 0; i < SNOOPER_PACKET_SIZE / sizeof(uint32_t); i++) {
    printf("%08x ", packet[i]);
  }

  if (color) {
    printf("%s", CRC_COLOR);
  }

  printf("<CRC expected: 0x%08x>\n", crc_cal);

  if (color) {
    printf("%s", COLOR_NORMAL);
  }
}

int log_packet(struct SnooperPacket const *sp) {
  crc32_init();

#if 0
	for (int i = 1; i <23; i++) {
		printf("%sx\n", ctrl_msg_str[i]);
	}
	for (int i = 1; i <16; i++) {
		printf("%sx\n", data_msg_str[i]);
	}
	for (int i = 1; i <13; i++) {
		printf("%sx\n", ext_msg_str[i]);
	}

	for (int i = 1; i <6; i++) {
		printf("%sx\n", structured_vdm_command_str[i]);
	}

	printf("\n");
#endif
  sequence = sp->sequence;
  cc1_voltage = sp->cc1_voltage;
  cc2_voltage = sp->cc2_voltage;
  vconn_current = sp->vconn_current;
  vbus_voltage = sp->vbus_voltage;
  vbus_current = sp->vbus_current;
  lost = sp->type.lost;
  partial = sp->type.partial;
  version = sp->type.version;
  type = sp->type.type;
  pol = sp->type.polarity;
  data = sp->data;
  crc_rec = sp->crc;

  process_header();

  crc32_hash((uint8_t *)sp, SNOOPER_PACKET_SIZE - sizeof(crc_rec));

  crc_cal = crc32_result();

  log_rev(stdout);
  log_sequence(stdout);
  log_pol(stdout);
  log_role(stdout);
  log_msg(stdout);
  log_data(stdout);

  return 0;
}

static struct timeval curTime;

void log_file(uint8_t *buf) {
  gettimeofday(&curTime, NULL);
  struct tm *tm = localtime(&curTime.tv_sec);
  uint32_t timer =
      curTime.tv_usec / 1000 +
      1000 * (tm->tm_sec +
              60 * (tm->tm_min + 60 * (tm->tm_hour + 24 * tm->tm_mday)));

  for (int i = 0; i < 4; i++) {
    buf[i] = (timer >> (8 * i)) & 0xFF;
  }

  //	printf("log file\n");
  if (file_open) {
    fwrite(buf, 1, 512, file_ptr);
  }
  //	printf("log end\n");
}

void file_open(char *file_name) {
  file_ptr = fopen(file_name, "wb+");
  file_is_open = true;

  printf("File created: %s\n", file_name);
  if (file_ptr == NULL) {
    printf("NULL file pointer\n");
  }
}

void file_close() {
  file_is_open = false;
  fclose(file_ptr);

  printf("File closed.\n");
}
