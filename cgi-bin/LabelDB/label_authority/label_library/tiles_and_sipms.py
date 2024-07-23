import itertools as it  # type to start with: engines

from label_authority.registry import register  # in every file
from label_authority.serial_schema import (
    MappingField,
    NumericField,  # H: field types are defined, mapping->pts to something else  and numerical -> just numbers
    SerialSchema,
)

from .types import Subtype

tile_subtypes = (
    [f"{size:02}" for size in range(0, 50, 2)]  # Normal sized tiles
    + [f"F{i}" for i in range(1, 9)]  # Tiles for front section
    + [f"S{i}" for i in range(1, 7)]  # Special tiles
)

desyDict = {str(i): "Wrapped at DESY ({})".format(i) for i in range(10)}

niuDict = dict(
    [
        ("A", "Wrapped at NIU (A)"),
        ("B", "Wrapped at NIU (B)"),
        ("C", "Wrapped at NIU (C)"),
        ("D", "Wrapped at NIU (D)"),
        ("E", "Wrapped at NIU (E)"),
        ("F", "Wrapped at NIU (F)"),
        ("G", "Wrapped at NIU (G)"),
        ("H", "Wrapped at NIU (H)"),
    ]
)

RDict = {**desyDict, **niuDict}

machine_tile_fields = SerialSchema(
    NumericField("PlateNumber", "Plate Number from which the tile was cut", 4),
    MappingField(
        "ReelMagID", "Magazine or Reel Id in which the tile was produced", 1, RDict
    ),
    NumericField("SerialNumber", "Serial number within the magazine/reel", 3),
)

injection_tile_fields = SerialSchema(
    NumericField(
        "InjectionNumber",
        "Injection-molding batch number from which the tile was moldeld",
        4,
    ),
    MappingField(
        "ReelMagID", "Magazine or Reel Id in which the tile was produced", 1, RDict
    ),
    NumericField("SerialNumber", "Serial number within the magazine/reel", 3),
)

sipm_subtypes = ("04", "09")

sipm_fields = SerialSchema(
    NumericField("ReelNumber", "Reel in  which the SiPM was produced", 4),
    NumericField("SerialNumber", "Serial number", 4),
)


def machineTileGetSubtype(major_type, code):
    if code not in tile_subtypes:
        raise KeyError
    if code[0] == "F":
        size = int(code[1])
        nc = 50 + size
        name = f"FH-Tile-{size}"
        long_name = (
            f"{major_type.long_name.strip('Tile')} FH/HD Cast Tile of size {size}"
        )
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

    if major_type.code == "BC" or major_type.code == "TC":
        tile_fields = machine_tile_fields
    else:
        tile_fields = injection_tile_fields

    return Subtype(major_type, name, long_name, code, nc, tile_fields)


def sipmGetSubtype(major_type, code):
    if code not in sipm_subtypes:
        raise KeyError
    if code == "04":
        name = "4mm"
        long_name = major_type.name + "of size 4mm2 "
    else:
        name = "9mm2"
        long_name = major_type.name + "of size 9mm2 "
    nc = code
    return Subtype(major_type, name, long_name, code, nc, sipm_fields)


@register
class BareCast:
    name = "BC-Tile"
    long_name = "Bare Cast Machined Tile"
    code = "BC"
    numeric_code = 20
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return tile_subtypes

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
        return tile_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return machineTileGetSubtype(WrappedCast, code)


@register
class BareInjection:
    name = "BI-Tile"
    long_name = "Bare Injection Molded Tile"
    code = "BI"
    numeric_code = 21
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return tile_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return machineTileGetSubtype(BareInjection, code)


@register
class WrappedInjection:
    name = "TI-Tile"
    long_name = "Wrapped Injection Molded Tile"
    code = "TI"
    numeric_code = 23
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return tile_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return machineTileGetSubtype(WrappedInjection, code)


@register
class SiPM:
    name = "SiPM"
    long_name = "Silicon Photomultiplier"
    code = "SP"
    numeric_code = 24
    num_subtype_chars = 2

    @staticmethod
    def getAllSubtypes():
        return sipm_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return sipmGetSubtype(SiPM, code)
