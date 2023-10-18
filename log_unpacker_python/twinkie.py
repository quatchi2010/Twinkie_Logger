"""The data package for the twinkie and top layer of the Power Delivery."""

import enum
import pathlib

import construct as ct
import data_mesg
import util


@enum.unique
class SoPEnum(enum.IntEnum):
  SOP = 0
  SOP_ = 1
  SOP__ = 2
  DBG_ = 3
  DBG__ = 4
  HRST = 5
  CRST = 6
  BIST = 7


@enum.unique
class CtrlMesgEnum(enum.IntEnum):
  """The Enum for Control Message Types.

  Revision 3.1 Version 1.8 Table 6-5 Control Message Types
  """

  GOOD_CRC = 1
  GOTO_MIN = 2
  ACCEPT = 3
  REJECT = 4
  PING = 5
  PS_RDY = 6
  GET_SRC_CAP = 7
  GET_SNK_CAP = 8
  DR_SWAP = 9
  PR_SWAP = 10
  VCONN_SWAP = 11
  WAIT = 12
  SOFT_RESET = 13
  DATA_RESET = 14
  DATA_RESET_COMPLETE = 15
  NOT_SUPPORTED = 16
  GET_SRC_CAP_EXT = 17
  GET_STATUS = 18
  FR_SWAP = 19
  GET_PPS_STATUS = 20
  GET_COUNTRY_CODES = 21
  GET_SNK_CAP_EXT = 22


@enum.unique
class DataMesgEnum(enum.IntEnum):
  """The Enum for Data Message Types.

  Revision 3.1 Version 1.8 Table 6-6 Data Message Types
  """

  SRC_CAP = 1
  REQUEST = 2
  BIST = 3
  SNK_CAP = 4
  BATTERY_STATUS = 5
  ALERT = 6
  GET_COUNTRY_INFO = 7
  ENTER_USB = 8
  VDM = 15


@enum.unique
class ProleEnum(enum.IntEnum):
  """The Enum for Port Power Role.

  Revision 3.1 Version 1.8 Secontion 6.2.1.1.4 Port Power Role
  """

  SNK = 0
  SRC = 1


@enum.unique
class ReVerEnum(enum.IntEnum):
  """The Enum for Specification Revision.

  Revision 3.1 Version 1.8 Secontion 6.2.1.1.5 Specification Revision
  """

  V1_0 = 0
  V2_0 = 1
  V3_0 = 2


@enum.unique
class DroleEnum(enum.IntEnum):
  """The Enum for Port Data Role.

  Revision 3.1 Version 1.8 Secontion 6.2.1.1.6 Port Data Role
  """

  UFP = 0
  DFP = 1


@enum.unique
class CableEnum(enum.IntEnum):
  """The Enum for Cable Plug.

  Revision 3.1 Version 1.8 Secontion 6.2.1.1.7 Cable Plug
  """

  DFP_UFP = 0
  CABLE_VPD = 1


@enum.unique
class ExtMesgEnum(enum.IntEnum):
  """The Enum for Extended Message Types.

  Revision 3.1 Version 1.8 Table 6-53 Extended Message Types
  """

  EXT_SRC_CAP = 1
  EXT_STATUS = 2
  EXT_GET_BATTERY_CAP = 3
  EXT_BATTERY_CAP = 4
  EXT_GET_MANUF_INFO = 5
  EXT_MANUF_INFO = 6
  EXT_SECURITY_REQUEST = 7
  EXT_SECURITY_RESPONSE = 8
  EXT_FW_UPDATE_REQUEST = 9
  EXT_FW_UPDATE_RESPONSE = 10
  EXT_PPS_STATUS = 11
  EXT_COUNTRY_INFO = 12
  EXT_COUNTRY_CODES = 13


SoP = ct.Enum(ct.BitsInteger(4), SoPEnum)

CtrlMesg = ct.Enum(ct.BitsInteger(5), CtrlMesgEnum)
DataMesg = ct.Enum(ct.BitsInteger(5), DataMesgEnum)
Prole = ct.Enum(ct.BitsInteger(1), ProleEnum)
Cable = ct.Enum(ct.BitsInteger(1), CableEnum)
Drole = ct.Enum(ct.BitsInteger(1), DroleEnum)
SoP = ct.Enum(ct.BitsInteger(4), SoPEnum)
ReVer = ct.Enum(ct.BitsInteger(2), ReVerEnum)
ExtMesg = ct.Enum(ct.BitsInteger(5), ExtMesgEnum)

## PD

# Revision 3.1 Version 1.8 Table 6-1 Message Header
pd_header = util.ByteSwappedBitStruct(
    "extended" / ct.BitsInteger(1),
    "num_data_obj" / ct.BitsInteger(3),
    "msg_id" / ct.BitsInteger(3),
    "power_role"
    / ct.Switch(
        ct.this._._.packet_bin.SOP,
        {
            SoPEnum.SOP.name: Prole,
            SoPEnum.SOP_.name: Cable,
            SoPEnum.SOP__.name: Cable,
        },
        ct.BitsInteger(1),
    ),
    "spec" / ReVer,
    "data_role" / ct.If(ct.this._._.packet_bin.SOP == SoPEnum.SOP.name, Drole),
    "msg_typ"
    / ct.IfThenElse(
        ct.this.num_data_obj,
        ct.IfThenElse(ct.this.extended, ExtMesg, DataMesg),
        CtrlMesg,
    ),
    __size=2,
)

pd_body = ct.Array(
    ct.this.header.num_data_obj,
    ct.Switch(
        ct.this.header.msg_typ,
        {
            DataMesgEnum.SRC_CAP.name: data_mesg.pdo,
            # DataMesgEnum.REQUEST.name: data_mesg.rdo,
            DataMesgEnum.BIST.name: data_mesg.bits,
            DataMesgEnum.VDM.name: data_mesg.vdm,
            # DataMesgEnum.SNK_CAP.name: data_mesg.pdo_sink,
            DataMesgEnum.BATTERY_STATUS.name: data_mesg.bsdo,
            DataMesgEnum.ALERT.name: data_mesg.ado,
            DataMesgEnum.GET_COUNTRY_INFO.name: data_mesg.ccdo,
            DataMesgEnum.ENTER_USB.name: data_mesg.eudo,
        },
    ),
)
pd = ct.Struct("header" / pd_header, "body" / pd_body)

## Twinkie

twinkie_typ = util.ByteSwappedBitStruct(
    "SOP" / SoP,
    "Version" / ct.BitsInteger(4),
    "PD" / ct.BitsInteger(1),
    "Packet_Lost" / ct.BitsInteger(1),
    "CC" / ct.BitsInteger(2),
    ct.Padding(4),
    __size=2,
)
twinkie = ct.Struct(
    "time" / ct.Int32ul,
    "cc1_v" / ct.Int16ul,
    "cc2_v" / ct.Int16ul,
    "cc2_c" / ct.Int16ul,
    "vbus_v" / ct.Int16ul,
    "vbus_c" / ct.Int16ul,
    "packet_bin" / twinkie_typ,
    "data_length" / ct.Int16ul,
    ct.Padding(2),
    "pd" / ct.If(ct.this.data_length, pd),
).compile(pathlib.Path(__file__).parent / "__pycache__" / "compile_twinkie.py")
