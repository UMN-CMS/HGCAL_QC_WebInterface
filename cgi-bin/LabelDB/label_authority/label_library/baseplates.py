import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

frontType = ["F0", "TL", "BL", "LL", "RL", "5L"]
base_subtypes = (
    [item + "W" for item in frontType]
    + [item + "C" for item in frontType]
    + ["BHW", "LHW", "THC", "RHW"]
)

VendorDict = {"A": "vendor A", "B": "vendor B", "C": "vendor C"}

base_fields = SerialSchema(
    MappingField("VendorNumber", "Identifies vendor", 1, VendorDict),
    NumericField("BatchNumber", "Batch number", 1),
    NumericField("Number", "Local serial number", 5),
)


def baseSubtypeByCode(major_type, code):
    if code not in base_subtypes:
        return KeyError
    cutDict = {
        "F": "Full",
        "T": "Top",
        "B": "Bottom",
        "L": "Left",
        "R": "Right",
        "5": "Five",
    }
    densDict = {"L": "LD, ", "H": "HD, ", "0": ""}
    matDict = {"W": "WCu", "P": "PCB", "C": "Carbon fiber"}

    numCutDict = {"F": "0", "T": "1", "B": "2", "L": "3", "R": "4", "5": "5"}
    numDensDict = {"H": "2", "L": "1", "0": "0"}
    numMatDict = {"W": "1", "P": "2", "C": "3"}

    name = f"{cutDict[code[0]]}, {densDict[code[1]]}{matDict[code[2]]}"
    long_name = f"{densDict[code[1]]} {cutDict[code[0]]} baseplate of {matDict[code[2]]} material"
    nc = numCutDict[code[0]] + numDensDict[code[1]] + numMatDict[code[2]]

    return Subtype(major_type, name, long_name, code, nc, base_fields)


@register
class Baseplate:
    name = "Baseplate"
    long_name = "Baseplate"
    code = "BA"
    numeric_code = 1
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return base_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return baseSubtypeByCode(Baseplate, code)
