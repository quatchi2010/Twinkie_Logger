"""The data package for the twinkie and top layer of the Power Delivery."""

import enum
import pathlib

import construct as ct
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


SoP = ct.Enum(ct.BitsInteger(4), SoPEnum)


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
    # "pd" / ct.If(ct.this.data_length, pd),
).compile(pathlib.Path(__file__).parent / "__pycache__" / "compile_twinkie.py")
