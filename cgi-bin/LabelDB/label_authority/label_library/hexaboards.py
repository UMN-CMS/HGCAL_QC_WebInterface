import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

hexaT1 = ["F", "T", "B", "L", "R", "5"]
hexaT2 = ["0", "1", "2", "3", "4"]

hexa_list = list(product(hexaT1, hexaT2))
hexa_subtypes = ["".join(hex) for hex in hexa_list]

VersionDict = {
    "0": "No ROCs",
    "2": "Common ground package of HGCROCV3b",
    "4": "Seperated ground package of HGCROCV3b",
    "C": "HGCROCV3c",
}

VendorDict = dict(
    [
        ("P", "Plotech PCB vendor"),
        ("Q", "HiQ PCB vendor"),
        ("M", "Micropack PCB vendor"),
    ]
)

AssemblyDict = dict(
    [
        ("U", "Unassembled board"),
        ("H", "Hybrid SA PCB assembly vendor"),
        ("P", "Plotech PCB assembly vendor"),
    ]
)

PCBDict = {
    "1": "HiQ PCB Vendor",
    "2": "Micropack PCB Vendor",
    "3": "Plotech PCB Vender",
}

BPCBDict = {
    "01": "HiQ PCB Vendor",
    "02": "Micropack PCB Vendor",
    "03": "Plotech PCB Vender",
}

hexa_fields = SerialSchema(
    MappingField(
        "R", "Identifies HGCROC version (pakage type and chip version)", 1, VersionDict
    ),
    MappingField("V", "Identifies PCB vendor", 1, VendorDict),
    MappingField("A", "Identifies PCB assembly vendor", 1, AssemblyDict),
    NumericField("N", "Local serial number", 5),
)

bare_hexa_fields = SerialSchema(
    MappingField("0", "Always 0 to indicate no ROCs", 1, VersionDict),
    MappingField("VendorNumber", "Identifies PCB vendor", 2, BPCBDict),
    NumericField("Number", "Local serial number", 5),
)


def hexaSubtypeByCode(major_type, code):
    long_name = major_type.long_name
    name = major_type.name[0:2]

    if code not in hexa_subtypes:
        raise KeyError

    # First T Value
    if code[0] == "F":
        name = "Full, "
        long_name = long_name + " Full"
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

    if major_type.name[:4] == "Bare":
        fields = bare_hexa_fields
    else:
        fields = hexa_fields
    return Subtype(major_type, name, long_name, code, nc, fields)


@register
class LDHexaboards:
    name = "LD-Hexaboard"
    long_name = "LD Hexaboard"
    code = "XL"
    numeric_code = 18
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return hexa_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hexaSubtypeByCode(LDHexaboards, code)


@register
class BareLDHexaboards:
    name = "Bare-LD-Hexaboard"
    long_name = "Bare LD Hexaboard"
    code = "XB"
    numeric_code = 6
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return hexa_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hexaSubtypeByCode(BareLDHexaboards, code)


@register
class HDHexaboards:
    name = "HD-Hexaboard"
    long_name = "HD Hexaboard"
    code = "XH"
    numeric_code = 7
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return hexa_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hexaSubtypeByCode(HDHexaboards, code)


@register
class BareHDHexaboards:
    name = "Bare-HD-Hexaboard"
    long_name = "Bare HD Hexaboard"
    code = "XG"
    numeric_code = 7
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return hexa_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hexaSubtypeByCode(BareHDHexaboards, code)
