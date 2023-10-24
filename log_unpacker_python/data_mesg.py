"""PD Data Message."""

import enum
import pathlib

import construct as ct
import util


@enum.unique
class PdoEnum(enum.IntEnum):
  """The Enum for Power Data Object Types.

  Revision 3.1 Version 1.8 Table 6-7 Power Data Object
  """

  FIXED_SUPPLY = 0
  BATTERY = 1
  VARIABLE_SUPPLY = 2
  APDO = 3


@enum.unique
class ApdoEnum(enum.IntEnum):
  """The Enum for Augmented Power Data Object Types.

  Revision 3.1 Version 1.8 Table 6-8 Augmented Power Data Object
  """

  SPR_PPS = 0
  EPR_AVS = 1


@enum.unique
class BitsModeEnum(enum.IntEnum):
  """The Enum for BIST Mode.

  Revision 3.1 Version 1.8 Table 6-27 BIST Data Object
  """

  CARRIER_MODE = 5
  TEST_DATA = 8
  SHARED_TEST_MODE_ENTRY = 9
  SHARED_TEST_MODE_EXIT = 10


@enum.unique
class VdmCommandTypeEnum(enum.IntEnum):
  """The Enum for VDM Command Type.

  Revision 3.1 Version 1.8 Table 6-29 Structured VDM Header
  """

  REQ = 0
  ACK = 1
  NAK = 2
  BUSY = 3


@enum.unique
class VdmCommandEnum(enum.IntEnum):
  """The Enum for VDM Command.

  Revision 3.1 Version 1.8 Table 6-29 Structured VDM Header
  """

  DISCOVER_IDENTITY = 1
  DISCOVER_SVIDS = 2
  DISCOVER_MODES = 3
  ENTER_MODE = 4
  EXIT_MODE = 5
  ATTENTION = 6
  SVID_16 = 16
  SVID_17 = 17
  SVID_18 = 18
  SVID_19 = 19
  SVID_20 = 20
  SVID_21 = 21
  SVID_22 = 22
  SVID_23 = 23
  SVID_24 = 24
  SVID_25 = 25
  SVID_26 = 26
  SVID_27 = 27
  SVID_28 = 28
  SVID_29 = 29
  SVID_30 = 30
  SVID_31 = 31


@enum.unique
class VdmVersionMajorEnum(enum.IntEnum):
  """The Enum for VDM Version Major.

  Revision 3.1 Version 1.8 Table 6-29 Structured VDM Header
  """

  V2_X = 1


@enum.unique
class VdmVersionMinorEnum(enum.IntEnum):
  """The Enum for VDM Version Major.

  Revision 3.1 Version 1.8 Table 6-29 Structured VDM Header
  """

  V2_0 = 0
  V2_1 = 1


@enum.unique
class BattCharStatEnum(enum.IntEnum):
  """The Enum for Battery Status.

  Revision 3.1 Version 1.8 Table 6-46 Battery Status Data Object (BSDO)
  """

  CHARGING = 1
  DISCHARGING = 2
  IDLE = 3


@enum.unique
class UsbEnum(enum.IntEnum):
  """The Enum for USB Mode.

  Revision 3.1 Version 1.8 Table 6-49 Enter_USB Data Object
  """

  USB_2_0 = 0
  USB_3_2 = 1
  USB_4_0 = 3


@enum.unique
class UsbCableEnum(enum.IntEnum):
  """The Enum for USB Cable Types.

  Revision 3.1 Version 1.8 Table 6-49 Enter_USB Data Object
  """

  ACTIVE_RE_TIMER = 1
  ACTIVE_RE_DRIVER = 2
  OPTICALLY_ISOLATED = 3


@enum.unique
class UsbCableCurrentEnum(enum.IntEnum):
  """The Enum for USB Cable Current Types.

  Revision 3.1 Version 1.8 Table 6-49 Enter_USB Data Object
  """

  VBUS_NOT_SUPPORT = 0
  MAX_3A = 2
  MAX_5A = 3


Pdo = ct.Enum(ct.BitsInteger(2), PdoEnum)
Apdo = ct.Enum(ct.BitsInteger(2), ApdoEnum)
BitsMode = ct.Enum(ct.BitsInteger(4), BitsModeEnum)
VdmCommandType = ct.Enum(ct.BitsInteger(2), VdmCommandTypeEnum)
VdmCommand = ct.Enum(ct.BitsInteger(5), VdmCommandEnum)
VdmVersionMajor = ct.Enum(ct.BitsInteger(2), VdmVersionMajorEnum)
VdmVersionMinor = ct.Enum(ct.BitsInteger(2), VdmVersionMinorEnum)
BattCharStat = ct.Enum(ct.BitsInteger(2), BattCharStatEnum)
Usb = ct.Enum(ct.BitsInteger(3), UsbEnum)
UsbCable = ct.Enum(ct.BitsInteger(2), UsbCableEnum)
UsbCableCurrent = ct.Enum(ct.BitsInteger(2), UsbCableCurrentEnum)

# Revision 3.1 Version 1.8 Table 6-9 Fixed Supply PDO - Source
fix_supply_pdo_src = ct.Struct(
    "dual_role_power" / ct.Flag,
    "usb_suspend_supported" / ct.Flag,
    "unconstrained_power" / ct.Flag,
    "usb_communications_capable" / ct.Flag,
    "dual_role_data" / ct.Flag,
    "unchunked_extended_messages_supported" / ct.Flag,
    "erp_mode_capable" / ct.Flag,
    ct.Padding(1),
    "peak_current" / ct.BitsInteger(2),
    "voltage_50mv" / ct.BitsInteger(10),
    "max_current_10ma" / ct.BitsInteger(10),
)

# Revision 3.1 Version 1.8 Table 6-11 Variable Supply (non-Battery) PDO - Source
variable_supply_pdo_src = ct.Struct(
    "max_voltage_50mv" / ct.BitsInteger(10),
    "min_voltage_50mv" / ct.BitsInteger(10),
    "max_current_10ma" / ct.BitsInteger(10),
)

# Revision 3.1 Version 1.8 Table 6-12 Battery Supply PDO - Source
battery_supply_pdo_src = ct.Struct(
    "max_voltage_50mv" / ct.BitsInteger(10),
    "min_voltage_50mv" / ct.BitsInteger(10),
    "max_power_250mw" / ct.BitsInteger(10),
)

# Revision 3.1 Version 1.8 Table 6-13 SPR Programmable Power Supply APDO - Source
srp_pps_src = ct.Struct(
    "pps_power_limit" / ct.Flag,
    ct.Padding(2),
    "max_voltage_100mv" / ct.BitsInteger(8),
    ct.Padding(1),
    "min_voltage_100mv" / ct.BitsInteger(8),
    ct.Padding(1),
    "max_current_50ma" / ct.BitsInteger(7),
)

# Revision 3.1 Version 1.8 Table 6-14 EPR Adjustable Voltage Supply APDO – Source
erp_pps_src = ct.Struct(
    "peak_current" / ct.BitsInteger(2),
    "max_voltage_100mv" / ct.BitsInteger(9),
    ct.Padding(1),
    "min_voltage_100mv" / ct.BitsInteger(8),
    "pdp_1w" / ct.BitsInteger(8),
)

# Revision 3.1 Version 1.8 Table 6-8 Augmented Power Data Object
apdo_src = ct.Struct(
    "apdo_typ" / Apdo,
    "spdo_information"
    / ct.Switch(
        ct.this.apdo_typ,
        {
            ApdoEnum.SPR_PPS.name: srp_pps_src,
            ApdoEnum.EPR_AVS.name: erp_pps_src,
        },
    ),
)

# Revision 3.1 Version 1.8 Table 6-7 Power Data Object
pdo = util.ByteSwappedBitStruct(
    "pdo_typ" / Pdo,
    "pdo_information"
    / ct.Switch(
        ct.this.pdo_typ,
        {
            PdoEnum.FIXED_SUPPLY.name: fix_supply_pdo_src,
            PdoEnum.BATTERY.name: battery_supply_pdo_src,
            PdoEnum.VARIABLE_SUPPLY.name: variable_supply_pdo_src,
            PdoEnum.APDO.name: apdo_src,
        },
    ),
    __size=4,
)

# Revision 3.1 Version 1.8 Table 6-16 Fixed Supply PDO - Sink
fix_supply_pdo_sink = ct.Struct(
    "dual_role_power" / ct.Flag,
    "higher_capability" / ct.Flag,
    "unconstrained_power" / ct.Flag,
    "usb_communications_capable" / ct.Flag,
    "dual_role_data" / ct.Flag,
    "fast_role_swap" / ct.BitsInteger(2),
    ct.Padding(3),
    "voltage_50ma" / ct.BitsInteger(10),
    "current_10ma" / ct.BitsInteger(10),
)

# Revision 3.1 Version 1.8 Table 6-17 Variable Supply (non-Battery) PDO - Sink
variable_supply_pdo_sink = ct.Struct(
    "max_voltage_50mv" / ct.BitsInteger(10),
    "min_voltage_50mv" / ct.BitsInteger(10),
    "current_10ma" / ct.BitsInteger(10),
)

# Revision 3.1 Version 1.8 Table 6-18 Battery Supply PDO - Sink
battery_supply_pdo_sink = ct.Struct(
    "max_voltage_50mv" / ct.BitsInteger(10),
    "min_voltage_50mv" / ct.BitsInteger(10),
    "power_250mw" / ct.BitsInteger(10),
)

# Revision 3.1 Version 1.8 Table 6-19 Programmable Power Supply APDO - Sink
srp_pps_sink = ct.Struct(
    ct.Padding(3),
    "max_voltage_100mv" / ct.BitsInteger(8),
    ct.Padding(1),
    "min_voltage_100mv" / ct.BitsInteger(8),
    ct.Padding(1),
    "max_current_50ma" / ct.BitsInteger(7),
)

# Revision 3.1 Version 1.8 Table 6-20 EPR Adjustable Voltage Supply APDO - Sink
erp_pps_sink = ct.Struct(
    ct.Padding(2),
    "max_voltage_100mv" / ct.BitsInteger(9),
    ct.Padding(1),
    "min_voltage_100mv" / ct.BitsInteger(8),
    "pdp_1w" / ct.BitsInteger(8),
)

apdo_sink = ct.Struct(
    "apdo_typ" / Apdo,
    "spdo_information"
    / ct.Switch(
        ct.this.apdo_typ,
        {
            ApdoEnum.SPR_PPS.name: srp_pps_sink,
            ApdoEnum.EPR_AVS.name: erp_pps_sink,
        },
    ),
)

pdo_sink = util.ByteSwappedBitStruct(
    "pdo_typ" / Pdo,
    "pdo_information"
    / ct.Switch(
        ct.this.pdo_typ,
        {
            PdoEnum.FIXED_SUPPLY.name: fix_supply_pdo_sink,
            PdoEnum.BATTERY.name: battery_supply_pdo_sink,
            PdoEnum.VARIABLE_SUPPLY.name: variable_supply_pdo_sink,
            PdoEnum.APDO.name: apdo_sink,
        },
    ),
    __size=4,
)

## RDO
rdo = util.ByteSwappedBitStruct(
    "pos" / ct.Peek(ct.BitsInteger(4)), "data" / ct.Bytes(32), __size=4
)

# Revision 3.1 Version 1.8 Table 6-21 Fixed and Variable Request Data Object
# Revision 3.1 Version 1.8 Table 6-22 Fixed and Variable Request Data Object with GiveBack Support
fix_variable_rdo = ct.Struct(
    "pos" / ct.BitsInteger(4),
    "give_back_flag" / ct.Flag,
    "capability_mismatch" / ct.Flag,
    "usb_communications_capable" / ct.Flag,
    "no_usb_suspend" / ct.Flag,
    "unchunked_extended_messages_supported" / ct.Flag,
    "erp_mode_capable" / ct.Flag,
    ct.Padding(2),
    "current_10ma" / ct.BitsInteger(10),
    "current_limit_10ma" / ct.BitsInteger(10),
).compile(pathlib.Path(__file__).parent / "__pycache__" / "fix_variable_rdo.py")

# Revision 3.1 Version 1.8 Table 6-23 Battery Request Data Object
# Revision 3.1 Version 1.8 Table 6-24 Battery Request Data Object with GiveBack Support
battery_rdo = ct.Struct(
    "pos" / ct.BitsInteger(4),
    "give_back_flag" / ct.Flag,
    "Capability_Mismatch" / ct.Flag,
    "usb_communications_capable" / ct.Flag,
    "no_usb_suspend" / ct.Flag,
    "unchunked_extended_messages_supported" / ct.Flag,
    "erp_mode_capable" / ct.Flag,
    ct.Padding(2),
    "power_250mw" / ct.BitsInteger(10),
    "power_limit_250mw" / ct.BitsInteger(10),
).compile(pathlib.Path(__file__).parent / "__pycache__" / "battery_rdo.py")

# Revision 3.1 Version 1.8 Table 6-25 PPS Request Data Object
pps_rdo = ct.Struct(
    "pos" / ct.BitsInteger(4),
    ct.Padding(1),
    "Capability_Mismatch" / ct.Flag,
    "usb_communications_capable" / ct.Flag,
    "no_usb_suspend" / ct.Flag,
    "unchunked_extended_messages_supported" / ct.Flag,
    "erp_mode_capable" / ct.Flag,
    ct.Padding(1),
    "voltage_20mv" / ct.BitsInteger(12),
    ct.Padding(2),
    "current_50ma" / ct.BitsInteger(7),
).compile(pathlib.Path(__file__).parent / "__pycache__" / "pps_rdo.py")

# Revision 3.1 Version 1.8 Table 6-26 AVS Request Data Object
avs_rdo = ct.Struct(
    "pos" / ct.BitsInteger(4),
    ct.Padding(1),
    "Capability_Mismatch" / ct.Flag,
    "usb_communications_capable" / ct.Flag,
    "no_usb_suspend" / ct.Flag,
    "unchunked_extended_messages_supported" / ct.Flag,
    "erp_mode_capable" / ct.Flag,
    ct.Padding(1),
    "voltage_25mv" / ct.BitsInteger(12),
    ct.Padding(2),
    "current_50ma" / ct.BitsInteger(7),
).compile(pathlib.Path(__file__).parent / "__pycache__" / "avs_rdo.py")

# Revision 3.1 Version 1.8 Table 6-27 BIST Data Object
bits = util.ByteSwappedBitStruct("mode" / BitsMode, ct.Padding(28), __size=4)

# Revision 3.1 Version 1.8 Table 6-28 Unstructured VDM Header
# Revision 3.1 Version 1.8 Table 6-29 Structured VDM Header
vdm = util.ByteSwappedBitStruct(
    "vid" / ct.BitsInteger(16),
    "vdm_typ" / ct.Flag,
    "body"
    / ct.IfThenElse(
        ct.this.vdm_typ,
        ct.Struct(
            "major_version" / VdmVersionMajor,
            "minor_version" / VdmVersionMinor,
            "obj_position" / ct.BitsInteger(3),
            "command_typ" / VdmCommandType,
            ct.Padding(1),
            "command" / VdmCommand,
        ),
        ct.BitsInteger(15),
    ),
    __size=4,
)

# Revision 3.1 Version 1.8 Table 6-46 Battery Status Data Object (BSDO)
bsdo = util.ByteSwappedBitStruct(
    "battery_present_capacity" / ct.BitsInteger(16),
    "battery_info"
    / ct.Struct(
        ct.Padding(4),
        "battery_charging_status" / BattCharStat,
        "battery_is_present" / ct.Flag,
        "invalid_battery_reference" / ct.Flag,
    ),
    __size=8,
)

# Revision 3.1 Version 1.8 Table 6-47 Alert Data Object
ado = util.ByteSwappedBitStruct(
    "ext" / ct.Flag,
    "ovp_event" / ct.Flag,
    "source_input_change" / ct.Flag,
    "operating_condition_change" / ct.Flag,
    "otp_event" / ct.Flag,
    "ocp_event" / ct.Flag,
    "battery_status_change_event" / ct.Flag,
    ct.Padding(1),
    "fixed_batteries" / ct.BitsInteger(4),
    "hot_swappable_batteries" / ct.BitsInteger(4),
    ct.Padding(12),
    "ext_event" / ct.BitsInteger(4),
    __size=4,
)

# Revision 3.1 Version 1.8 Table 6-48 Country Code Data Object
ccdo = util.ByteSwappedBitStruct(
    "first" / ct.BitsInteger(8),
    "second" / ct.BitsInteger(8),
    ct.Padding(16),
    __size=4,
)

# Revision 3.1 Version 1.8 Table 6-49 Enter_USB Data Object
eudo = util.ByteSwappedBitStruct(
    ct.Padding(1),
    "usb_communications_capable" / Usb,
    ct.Padding(1),
    "u4drd" / ct.Flag,
    "u3drd" / ct.Flag,
    ct.Padding(1),
    "speed" / ct.BitsInteger(3),
    "cable_typ" / UsbCable,
    "cable_current" / UsbCableCurrent,
    "pcie" / ct.Flag,
    "dp" / ct.Flag,
    "tbt" / ct.Flag,
    "hoy" / ct.Flag,
    ct.Padding(12),
    __size=4,
)
