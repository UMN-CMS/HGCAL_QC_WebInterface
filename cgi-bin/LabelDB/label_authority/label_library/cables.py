import itertools as it

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

cable_subtypes = ["TXA", "TXB", "TXC", "TXD", "FFH", "FBH", "PFH", "PBH"]

cable_fields = SerialSchema(
    NumericField("VersionNumber", "Version Number of the cable", 1),
    NumericField("BatchNumber", "Batch number in which the cable  was produced", 2),
    NumericField("SerialNumber", "Serial number within batch", 4),
)


def getSubtypesByCode(major_type, code):
    if code not in cable_subtypes:
        raise KeyError
    if code[2] != "H":
        name = "Twin-Ax " + code[2]
        long_name = (
            "Twin-Ax Cable between " + code[2] + "-shape tilemodules and wingboard"
        )
        nc = 100 + (ord(code[2]) - 64)
    if code[0] == "F":
        nc = 220
        insert = " E or G "
        if code[1] == "F":
            nc = nc - 10
            insert = " J or K "
        name = "Flex cable" + insert
        long_name = "Flex cable between" + insert + "tilemodules and wingboard"
    elif code[0] == "P":
        nc = 320
        if code[1] == "F":
            nc = nc - 10
        name = "Power adapter " + code[1:]
        long_name = "Power adapter board/cable for use with " + code[1:] + " windboard"

    return Subtype(major_type, name, long_name, code, nc, cable_fields)


@register
class Cables:
    name = "Scintillator Cables"
    long_name = "Scintillator Cables"
    code = "SC"
    numeric_code = 29
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return cable_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return getSubtypesByCode(Cables, code)
