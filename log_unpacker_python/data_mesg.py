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


Pdo = ct.Enum(ct.BitsInteger(2), PdoEnum)


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
