"""PD Data Message."""

import enum

import construct as ct
import util


class PdoEnum(enum.IntEnum):
  """The Enum for Power Data Object Types.

  Revision 3.1 Version 1.8 Table 6-7 Power Data Object
  """

  FIXED_SUPPLY = 0
  BATTERY = 1
  VARIABLE_SUPPLY = 2
  APDO = 3


class BitsModeEnum(enum.IntEnum):
  """The Enum for BIST Mode.

  Revision 3.1 Version 1.8 Table 6-27 BIST Data Object
  """

  CARRIER_MODE = 5
  TEST_DATA = 8
  SHARED_TEST_MODE_ENTRY = 9
  SHARED_TEST_MODE_EXIT = 10


class BattCharStatEnum(enum.IntEnum):
  """The Enum for Battery Status.

  Revision 3.1 Version 1.8 Table 6-46 Battery Status Data Object (BSDO)
  """

  CHARGING = 1
  DISCHARGING = 2
  IDLE = 3


Pdo = ct.Enum(ct.BitsInteger(2), PdoEnum)
BitsMode = ct.Enum(ct.BitsInteger(4), BitsModeEnum)
BattCharStat = ct.Enum(ct.BitsInteger(2), BattCharStatEnum)

# Revision 3.1 Version 1.8 Table 6-9 Fixed Supply PDO - Source
fix_supply_pdo_src = ct.Struct(
    "dual_role_power" / ct.BitsInteger(1),
    "usb_suspend_supported" / ct.BitsInteger(1),
    "unconstrained_power" / ct.BitsInteger(1),
    "usb_communications_capable" / ct.BitsInteger(1),
    "dual_role_data" / ct.BitsInteger(1),
    "unchunked_extended_messages_supported" / ct.BitsInteger(1),
    "erp_mode_capable" / ct.BitsInteger(1),
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
    "pps_power_limit" / ct.BitsInteger(1),
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
    "apdo_typ" / ct.BitsInteger(2),
    "spdo_information"
    / ct.Switch(
        ct.this.apdo_typ,
        {
            0b00: srp_pps_src,
            0b01: erp_pps_src,
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

# Revision 3.1 Version 1.8 Table 6-27 BIST Data Object
bits = util.ByteSwappedBitStruct("mode" / BitsMode, ct.Padding(28), __size=4)

# Revision 3.1 Version 1.8 Table 6-46 Battery Status Data Object (BSDO)
bsdo = util.ByteSwappedBitStruct(
    "battery_present_capacity" / ct.BitsInteger(16),
    "battery_info"
    / ct.Struct(
        ct.Padding(4),
        "battery_charging_status" / BattCharStat,
        "battery_is_present" / ct.BitsInteger(1),
        "invalid_battery_reference" / ct.BitsInteger(1),
    ),
    __size=8,
)

# Revision 3.1 Version 1.8 Table 6-47 Alert Data Object
ado = util.ByteSwappedBitStruct(
    "ext" / ct.BitsInteger(1),
    "ovp_event" / ct.BitsInteger(1),
    "source_input_change" / ct.BitsInteger(1),
    "operating_condition_change" / ct.BitsInteger(1),
    "otp_event" / ct.BitsInteger(1),
    "ocp_event" / ct.BitsInteger(1),
    "battery_status_change_event" / ct.BitsInteger(1),
    ct.Padding(1),
    "fixed_batteries" / ct.BitsInteger(4),
    "hot_swappable_batteries" / ct.BitsInteger(4),
    ct.Padding(12),
    "ext_event" / ct.BitsInteger(4),
    __size=4,
)
