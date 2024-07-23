import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

dig1 = ["1", "2", "3"]
dig23 = ["F0", "SR", "HT", "SL", "HB", "5R", "5L"]
dig4 = ["B", "D", "T"]

econ_list = list(product(dig1, dig23, dig4))

econ_subtypes = ["".join(hex) for hex in econ_list]

econ_fields = SerialSchema(NumericField("SerialNumber", "Serial number", 6))


def econSubtypeByCode(major_type, code):
    if code not in econ_subtypes:
        raise KeyError

    modDict = {"1": "Prototype", "2": "Prototype", "3": "(pre)Prodeuction"}
    CMDict = {
        "F0": "Full",
        "SR": "Semi-Right",
        "HT": "Half-Top",
        "SL": " Semi-Left",
        "HB": "Half Bottom",
        "5R": "Five Right",
        "5L": "Five Left",
    }
    boardDict = {"B": "Bare board", "D": "ECON-D only", "T": "ECON-D and ECON-T"}

    numBoardDict = {"B": "0", "D": "1", "T": "2"}
    nameBoardDict = {"B": "Bare", "D": "D", "T": "D+T"}

    if code[1] == "F":
        name = "CM"
        front = ""
    else:
        name = "PCM"
        front = "Partial"
    name = f"{name} {CMDict[code[1:3]]} {nameBoardDict[code[3]]}"
    long_name = f"{modDict[code[0]]} {front} {CMDict[code[1:3]]} {boardDict[code[3]]}"

    nc = code[:3] + numBoardDict[code[3]]

    return Subtype(major_type, name, long_name, code, nc, econ_fields)


@register
class EconMezz:
    name = "ECON-Mezzanine"
    long_name = "Concentrator Mezzanine"
    code = "CM"
    numeric_code = 15
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return econ_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return econSubtypeByCode(EconMezz, code)
