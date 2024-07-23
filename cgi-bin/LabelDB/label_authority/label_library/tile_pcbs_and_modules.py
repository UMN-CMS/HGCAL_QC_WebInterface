import itertools as it  # type to start with: engines
from itertools import product

from label_authority.registry import register  # in every file
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

shape_row_class = [
    "A5",
    "A6",
    "B1",
    "B2",
    "C5",
    "D8",
    "E8",
    "G8",
    "G7",
    "G5",
    "G3",
    "J1",
    "J2",
    "K2",
    "K0",
    "K8",
    "K5",
]
geometry = ["F", "R", "L"]
material = ["C", "M"]
pcb_list = list(product(shape_row_class, geometry))

tile_pcb_subtypes = ["".join(pcb) for pcb in pcb_list]

module_list = list(product(tile_pcb_subtypes, material))

tile_module_subtypes = ["".join(mod) for mod in module_list]

versDict = {
    "2": "common ground package of HGCROCV3b ASIC",
    "4": "seperated-ground HGCROCV3b ASIC",
    "C": "HGCROCV3c ASIC",
}

manuDict = {"A": "manufacturer A", "B": "manufacturer B", "C": "manufacturer C"}

tile_pcb_fields = SerialSchema(
    MappingField("VersionNumber", "HGCROC version or board generation", 1, versDict),
    MappingField(
        "ManufacturerNumber", "Board manufaturer, currently unspecified", 1, manuDict
    ),
    NumericField("0", "Digit reserved as zero", 1),
    NumericField("SerialNumber", "Serial number", 4),
)

tile_module_fields = SerialSchema(
    MappingField("VersionNumber", "HGCROC version or board generation", 1, versDict),
    MappingField(
        "ManufacturerNumber", "Board manufaturer, currently unspecified", 1, manuDict
    ),
    NumericField("SerialNumber", "Serial number", 4),
)


def tileSubtypeByCode(major_type, code):
    if code not in tile_pcb_subtypes and code not in tile_module_subtypes:
        return KeyError
    numDict = {
        "0": "ten",
        "1": "eleven",
        "2": "twelve",
        "3": "three",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
    }
    shapeDict = {
        "A": "1",
        "B": "2",
        "C": "3",
        "D": "4",
        "E": "5",
        "G": "6",
        "J": "7",
        "K": "8",
    }
    geoDict = {"F": "0", "L": "1", "R": "2"}

    if len(code) == 3:
        code = code + "n"
    rowNum = numDict[code[1]]
    nc = shapeDict[code[0]] + code[1] + geoDict[code[2]]
    if code[3] == "C":
        nc = nc + "1"
        mat = "cast"
    elif code[3] == "M":
        nc = nc + "2"
        mat = "molded"
    else:
        code = code[:3]
        mat = ""

    if major_type.name == "Tile-Module":
        tile_fields = tile_module_fields
    else:
        tile_fields = tile_pcb_fields

    name = " "
    long_name = f"{major_type.long_name} with shape {code[0]} and {rowNum} rows of {mat} tiles, 9mm\ :sup:`2` SiPMs"

    return Subtype(major_type, name, long_name, code, nc, tile_fields)


@register
class TilePCB:
    name = "Tile-PCB"
    long_name = "Tile PCB"
    code = "TB"
    numeric_code = 26
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return tile_pcb_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return tileSubtypeByCode(TilePCB, code)


@register
class BareTilePCB:
    name = "Bare-Tile-PCB"
    long_name = "Tile PCB without any components"
    code = "TP"
    numeric_code = 25
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return tile_pcb_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return tileSubtypeByCode(BareTilePCB, code)


@register
class TileModule:
    name = "Tile-Module"
    long_name = "Tile Module"
    code = "TM"
    numeric_code = 25
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return tile_module_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return tileSubtypeByCode(TileModule, code)
