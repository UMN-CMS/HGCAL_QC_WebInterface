import itertools as it

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

ld_ws = ["10A1", "20A1", "30A1", "30A3", "10Z1"]
lde_wagon_subtypes = ld_ws + (["20B1"])
ldw_wagon_subtypes = ld_ws + (["30A2", "11A1"])

hd_sub_base = ["A1", "AB", "B1", "BB", "CB", "C1", "D1", "DB"]
front_sub = ["30", "31", "21", "20"]
hd_subtypes = ["30A0", "30C0"]
for i in range(4):
    if len(hd_sub_base) == 6:
        hd_sub_base = hd_sub_base[: len(hd_sub_base) - 1]
    insert = [front_sub[i] + item for item in hd_sub_base]

    if len(hd_sub_base) == 5:
        hd_sub_base = hd_sub_base[: len(hd_sub_base) - 1]
    else:
        hd_sub_base = hd_sub_base[: len(hd_sub_base) - 2]
    hd_subtypes.extend(insert)

wagon_fields = SerialSchema(NumericField("SerialNumber", "Serial number of wagon", 6))


def ld_wagonSubtypeByCode(major_type, code):
    name = major_type.name[9:]
    long_name = major_type.name

    name = name + " " + code[0] + code[2]
    if code[2] == "Z":
        name = major_type.name[9:] + " 1 Debug"
        long_name = name + " wagon"
    if code[3] == "1":
        long_name = name + ", Straight shape"
    elif code[3] == "2":
        name = "Lefty Python"
        long_name = long_name + ", Python shape"
    else:
        name = major_type.name[9:] + " T"
        long_name = long_name + ", T shape"
    if code[1] == "1":
        name = "West F+P A"
        long_name = name + " with " + code[0] + " full module, 1 partial module,"
    else:
        long_name = long_name + " with " + code[0] + " full module, 0 partial modules,"
    if code == "10A1" or code == "20B1":
        long_name = long_name + " and 2 incoming crossover links (Inc. Xs)"
    else:
        long_name = long_name + " and 0 incoming crossover links (Inc. Xs)"

    nc = code

    if code not in lde_wagon_subtypes and code not in ldw_wagon_subtypes:
        raise KeyError

    return Subtype(major_type, name, long_name, code, nc, wagon_fields)


@register
class LDWagonWest:
    name = "LD-Wagon-West"
    long_name = "LD Wagon West"
    code = "WW"
    numeric_code = 13
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return ldw_wagon_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return ld_wagonSubtypeByCode(LDWagonWest, code)


@register
class LDWagonEast:
    name = "LD-Wagon-East"
    long_name = "LD Wagon East"
    code = "WE"
    numeric_code = 12
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return lde_wagon_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return ld_wagonSubtypeByCode(LDWagonEast, code)


def hd_wagonSubtypeByCode(major_type, code):
    if code not in hd_subtypes:
        raise KeyError
    name = "HD Wagon"
    long_name = "HD Wagon"

    if code[3] == "1":  # PRODUCTION
        long_name = "Production " + long_name
        if code[2] == "C" or code[2] == "D":
            long_name = long_name + " with a shape of Triangle 3, HDEF, link topology"
            if code[2] == "C":
                long_name = long_name + " 1"
            else:
                long_name = long_name + " 2"
        elif code == "31B1":
            long_name = long_name + ", J-shaped 3 + Top, HDEF"
        else:
            long_name = long_name + " with a shape of Straight " + code[0]
            if code[1] == "1" and code[0] == "2":
                long_name = long_name + " + Bottom"
            if code == "31A1":
                long_name = long_name + " + Semi"
            elif code == "30A1" or code == "21A1":
                long_name = long_name + ", HDEF"
            else:
                long_name = long_name + ", HDEH"
    elif code[3] == "B":  # PRODUCTION BARE PCB
        long_name = "Production Bare PCB " + long_name
        if code[0] == "3":
            long_name = long_name + " with a shape of Straight " + code[0]
            if code[1] == "0":
                if code[2] == "A":
                    long_name = long_name + " for Full HD Engine"
                elif code[2] == "B":
                    long_name = long_name + " for Half HD Engine"
                elif code[2] == "C":
                    long_name = "HD Wagon with a shape of Triangle 3, link topology 1"
                else:
                    long_name = "HD Wagon with a shape of Triangle 3, link topology 2"
            else:
                if code[2] == "A":
                    long_name = long_name + " + Semi Left"
                elif code[2] == "B":
                    long_name = long_name + " + Semi Right"
                elif code[2] == "C":
                    long_name = "Hd Wagon with a J-Shaped 3 + Top"
        else:
            long_name = long_name + " with a shape  of Straight " + code[0]
            if code[1] == "1":
                long_name = long_name + " + Bottom"
                if code[2] == "B":
                    long_name = long_name + " for Half"
    else:  # PROTOTYPES
        long_name = "Prototype " + long_name

    nc = code

    return Subtype(major_type, name, long_name, code, nc, wagon_fields)


@register
class HDWagon:
    name = "HD-Wagon"
    long_name = "HD Wagon"
    code = "WH"
    numeric_code = 14
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return hd_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return hd_wagonSubtypeByCode(HDWagon, code)
