import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

hexaT1 = ["F", "T", "B", "L", "R", "5"]
hexaT2 = ["0", "1", "2", "3", "4"]
hexaT3 = ["U", "2", "4", "C"]

hexa_list = list(product(hexaT1, hexaT2, hexaT3))
hexa_subtypes = ["".join(hex) for hex in hexa_list]

VendorDict = dict(
    [
        ("P", "Plotech PCB vendor"),
        ("Q", "HiQ PCB vendor"),
        ("M", "Micropack PCB vendor"),
        # ("1", "Plotech PCB,vendor"),
        # ("2", "HiQ PCB vendor"),
        # ("3", "Micropack PB vendor")
    ]
)

AssemblyDict = dict(
    [
        ("U", "Unassembled board"),
        ("H", "Hybrid SA PCB assembly vendor"),
        ("P", "Plotech PCB assembly vendor"),
        # ("0", "Unassembled board"),
        # ("1", "Hybrid SA PCB assembly vendor"),
        # ("2", "Plotech PCB assembly vendor")
    ]
)

hexa_fields = SerialSchema(
    MappingField("PCBVendor", "Identifies PCB vendor", 1, VendorDict),
    MappingField("AssemblyVendor", "Identifies PCB assembly vendor", 1, AssemblyDict),
    NumericField("SerialNumber", "Serial number within batch", 5),
)


def hexaSubtypeByCode(major_type, code):
    long_name = major_type.long_name
    name = major_type.name[0:2]

    if code not in hexa_subtypes:
        raise KeyError

    # First T Value
    if code[0] == "F":
        name = "Full, "
        long_name = "Full " + long_name
        nc = "0"
    elif code[0] == "T":
        name = "Top, "
        long_name = long_name + " Top"
        nc = "1"
    elif code[0] == "B":
        name = "Bottom, "
        long_name = long_name + " Bottom"
        nc = "2"
    elif code[0] == "L":
        name = "Left, "
        long_name = long_name + " Left"
        nc = "3"
    elif code[0] == "R":
        name = "Right, "
        long_name = long_name + " Right"
        nc = "4"
    else:
        name = "Five, "
        long_name = long_name + " Five"
        nc = "5"

    # Second T Value
    nc = nc + code[1]
    if code[1] == "4":
        name = name + "Preproduction/production, "
        long_name = long_name + " Preproduction/production"
    else:
        name = name + "Prototype, "
        long_name = long_name + " prototype"

    # Third T Value
    if code[2] == "U":
        name = name + "Used"
        nc = nc + "0"
        long_name = long_name + " (used)"
    if code[2] == "2":
        name = name + "SU02 packaged"
        nc = nc + code[2]
        long_name = long_name + " with S02-packaged HGCROCV3b ASICs"
    if code[2] == "4":
        name = name + "SU04 packaged"
        nc = nc + code[2]
        long_name = long_name + " with S04-packaged HGCROCV3b ASICs"
    if code[2] == "C":
        name = name + "Sperated ground packaged"
        nc = nc + "8"
        long_name = long_name + " with HGCROCV3b ASICs"

    return Subtype(major_type, name, long_name, code, nc, hexa_fields)


@register
class LDHexaboards:
    name = "LD-Hexaboard"
    long_name = "LD Hexaboard"
    code = "XL"
    numeric_code = 6
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return hexa_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hexaSubtypeByCode(LDHexaboards, code)


@register
class HDHexaboards:
    name = "HD-Hexaboard"
    long_name = "HD Hexaboard"
    code = "XH"
    numeric_code = 7
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return hexa_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hexaSubtypeByCode(HDHexaboards, code)
