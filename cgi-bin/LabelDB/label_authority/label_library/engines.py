import itertools as it

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

engineFields = SerialSchema(NumericField("SerialNumber", "Serial number", 6))


def getLDESub(major_type, code):
    long_name = "Engine"
    name = "Eng"
    nc = code
    if nc == "0QE0":
        nc = int("0400")
        name = "Q " + name + " E"
        long_name = "Qualification Engine East"
    elif nc == "0QW0":
        nc = int("0410")
        name = "Q " + name + " W"
        long_name = "Qualification Engine West"
    else:
        nc = int(code)

    # Check Error
    if code not in LDEngine.getAllSubtypes():
        raise KeyError  # Not sure what this was supposed to be

    # Examine 2nd num
    if code[0] == "0" and code[1] == "0":
        name = name + " V1"
        long_name = long_name + " V1"
    elif code[1] == "1":
        name = name + " V2"
        long_name = long_name + " V2"
    elif code[1] == "2":
        name = name + " V2b"
        long_name = long_name + " V2b"
    elif code[1] == "3":
        name = name + " V3"
        long_name = long_name + " V3"
        if code[2] == "1":
            name = name + " W"
            long_name = "LD " + long_name + " West"
        else:
            long_name = "LD " + long_name + " East"
    elif code[1] == "9":
        name = name + " Dmy"
        long_name = "Mechanical dummy V3 " + long_name + " East"
    elif code[0] == "1":
        long_name = "Production " + long_name
        if code[2] == "1":
            name = name + " W"
            long_name = long_name + " West "
        else:
            name = name + " E"
            long_name = long_name + " East "
        if code[3] == "1":
            long_name = long_name.strip("Production") + " Bare PCB"

    return Subtype(LDEngine, name, long_name, code, nc, engineFields)


@register
class LDEngine:
    name = "LD-Engine"
    long_name = "LD Engine"
    code = "EL"
    numeric_code = 10
    num_subtype_chars = 4

    subtypesList = [
        "0000",
        "0100",
        "0200",
        "0300",
        "0310",
        "0QE0",
        "0QW0",
        "0900",
        "1000",
        "1001",
        "1010",
        "1011",
    ]

    @staticmethod
    def getAllSubtypes():
        return LDEngine.subtypesList

    @staticmethod
    def getSubtypeByCode(code):
        return getLDESub(LDEngine, code)


def getHDESub(major_type, code):
    lon = major_type.long_name
    name = "HDE"

    if code == "03F0":  # GOOD
        nc = "0300"
        name = "HDEF3"
        long_name = "Prototype HD engine V3 (3 IpGBT)"
    if code == "0QF0":  # GOOD
        nc = "0400"
        name = "HDE FQ"
        long_name = "Vendor Qualification Engine Full(6 IpGBT)"
    if code == "0QH0":  # GOOD
        nc = "0410"
        name = "HDE HQ"
        long_name = "Vendor Qualification Engine Half (3 IpGBT)"
    if code[0] == "1":
        nc = code
        long_name = "Production" + lon
    if code[2] == "F":
        nc = "1000"
        name = "HDE F"
        long_name = lon + " Full (6 IpGBT)"
        if code[3] == "B":
            nc = "1001"
            long_name = long_name + " Bare PCB"
    else:
        nc = "1010"
        name = "HDE H"
        long_name = lon + " Half (3 IpGBT)"
        if code[3] == "B":
            nc = "1011"
            long_name = long_name + "Bare PCB"

    if code not in HDEngine.getAllSubtypes():
        raise KeyError

    return Subtype(major_type, name, long_name, code, nc, engineFields)


@register
class HDEngine:
    name = "HD-Engine"
    long_name = "HD Engine"
    code = "EH"
    numeric_code = 11
    num_subtype_chars = 4

    HDsubtypesList = ["03F0", "0QF0", "0QH0", "10F0", "10FB", "10H0", "10HB"]

    @staticmethod
    def getAllSubtypes():
        return HDEngine.HDsubtypesList

    @staticmethod
    def getSubtypeByCode(code):
        return getHDESub(HDEngine, code)
