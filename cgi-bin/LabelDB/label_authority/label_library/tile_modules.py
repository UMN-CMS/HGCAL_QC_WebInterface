import itertools as it  #type to start with: engines

from label_authority.registry import register    #in every file
from label_authority.serial_schema import (MappingField, NumericField,  #H: field types are defined, mapping->pts to something else  and numerical -> just numbers 
                                           SerialSchema)

from .types import Subtype

machine_tile_subtypes = (
    [f"{size:02}" for size in range(0, 50, 2)]  # Normal sized tiles
    + [f"F{i}" for i in range(1, 9)]   # Tiles for front section
    + [f"S{i}" for i in range(1, 7)]   # Special tiles
)

desyDict = {str(i): "Wrapped at DESY ({})".format(i) for i in range(10)}

niuDict = dict([
    ("A" , "Wrapped at NIU (A)"),
    ("B" , "Wrapped at NIU (B)"),
    ("C" , "Wrapped at NIU (C)"),
    ("D" , "Wrapped at NIU (D)"),
    ("E" , "Wrapped at NIU (E)"),
    ("F" , "Wrapped at NIU (F)"),
    ("G" , "Wrapped at NIU (G)"),
    ("H" , "Wrapped at NIU (H)")
])

RDict = {**desyDict, **niuDict}

machine_tile_fields = SerialSchema(
    NumericField("PlateNumber", "Plate Number from which the tile was cut", 4), 
    MappingField("ReelMagID", "Magazine or Reel Id in which the tile was produced", 1, RDict),
    NumericField("SerialNumber", "Serial number", 3),
)


def machineTileGetSubtype(major_type, code):
    if code not in machine_tile_subtypes:
        raise KeyError
    if code[0] == "F":
        size = int(code[1])
        nc = 50 + size
        name = f"FH-Tile-{size}"
        long_name = f"{major_type.long_name.strip('Tile')} FH/HD Cast Tile of size {size}"
    elif code[0] == "S":
        size = int(code[1])
        nc = 70 + size
        name = f"Special-Tile-{code}"
        long_name = f"{major_type.long_name.strip('Tile')} Special Tile type {size}"
    else:
        size = int(code)
        nc = size
        name = f"{code}"
        long_name = f"{major_type.long_name} of size {size}"
    return Subtype(major_type, name, long_name, code, nc, machine_tile_fields)


@register
class BareCast:
    name = "BC-Tile"
    long_name = "Bare Cast Machined Tile"
    code = "BC"
    numeric_code = 20
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return machine_tile_subtypes 

    @staticmethod
    def getSubtypeByCode(code):
        return machineTileGetSubtype(BareCast, code)

@register
class WrappedCast:
    name = "TC-Tile"
    long_name = "Wrapped Cast Machined Tile"
    code = "TC"
    numeric_code = 22
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return machine_tile_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return machineTileGetSubtype(WrappedCast, code)
