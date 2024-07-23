import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

shape = ["F", "T", "B", "L", "R", "5"]
thickness = ["1", "2", "3"]
btype = ["W", "P", "C"]
version = ["X", "2", "4", "C"]

ld_subtypes = ["".join(hex) for hex in list(product(shape, thickness[1:], btype))]

hd_subtypes = ["".join(hex) for hex in list(product(shape[:5], thickness[:2], btype))]

locatDict = {
    "SB": "assembled at USCB",
    "CM": "assembled at CMU",
    "IH": "assembled at IHEP",
    "NT": "assembled at NTU",
    "TI": "assembled at TIFR",
    "TT": "assembled at TTU",
}
versDict = {
    "X": "Preseries",
    "2": "common ground package of HGCROCV3b ASIC",
    "4": "seperated-ground HGCROCV3b ASIC",
    "C": "HGCROCV3c",
}

si_fields = SerialSchema(
    MappingField("R", "Version of ROC", 1, versDict),
    MappingField("L", "Location of the Module Assembly Center (MAC)", 2, locatDict),
    NumericField("N", "Local serial number", 4),
)


def siSubtypeByCode(major_type, code):
    if code not in ld_subtypes and code not in hd_subtypes:
        raise KeyError

    shapeDict = {
        "F": "Full",
        "T": "Top",
        "B": "Bottom",
        "L": "Left",
        "R": "Right",
        "5": "Five",
    }
    thickDict = {
        "1": "120 :math:`\mu`\m",
        "2": "200 :math:`\mu`\m",
        "3": "300 :math:`\mu`\m",
    }
    btypeDict = {"W": "CuW", "P": "PCB", "C": "Carbon Fiber"}

    numShapeDict = {"F": "0", "T": "1", "B": "2", "L": "3", "R": "4", "5": "5"}
    numBtypeDict = {"W": "1", "P": "2", "C": "3"}

    name = ""
    long_name = f"{major_type.long_name[:2]} {shapeDict[code[0]]}, {thickDict[code[1]]}, {btypeDict[code[2]]} baseplate"

    nc = numShapeDict[code[0]] + code[1] + numBtypeDict[code[2]]

    return Subtype(major_type, name, long_name, code, nc, si_fields)


@register
class HDSiModule:
    name = "HD-Si-Module"
    long_name = "HD Si Module"
    code = "MH"
    numeric_code = 9
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return hd_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return siSubtypeByCode(HDSiModule, code)


@register
class LDSiModule:
    name = "LD-Si-Module"
    long_name = "LD Si Module"
    code = "ML"
    numeric_code = 8
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return ld_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return siSubtypeByCode(LDSiModule, code)


@register
class LDPModule:
    name = "LD-Protomodule"
    long_name = "LD Protomodule"
    code = "PL"
    numeric_code = 4
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return ld_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return siSubtypeByCode(LDPModule, code)


@register
class HDPModule:
    name = "HD-Protomodule"
    long_name = "HD Protomodule"
    code = "PH"
    numeric_code = 5
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return hd_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return siSubtypeByCode(HDPModule, code)
