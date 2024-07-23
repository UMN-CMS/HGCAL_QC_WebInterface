import itertools as it  # type to start with: engines

from label_authority.registry import register  # in every file
from label_authority.serial_schema import (
    MappingField,
    NumericField,  # H: field types are defined, mapping->pts to something else  and numerical -> just numbers
    SerialSchema,
)

from .types import Subtype

dc_subtype = ["TST1"]

zipper_subtypes = [
    "AR00",
    "BR00",
    "CR00",
    "BS00",
    "AL00",
]  # NOTE: THIS IS WRONG, SHOULD BE AL0

tester_subtypes = [
    "0001",
    "0002",
    "0011",
    "0012",
    "0021",
    "0031",
    "0032",
    "0033",
    "0034",
    "0400",
    "0410",
    "0420",
    "0430",
]

dc_zip_fields = SerialSchema(NumericField("SerialNumber", "Serial number", 6))


def dcGetSubtype(major_type, code):
    if code not in dc_subtype:
        raise KeyError
    name = "Test DC/DC"
    nc = "9001"
    long_name = name + " Board"
    return Subtype(major_type, name, long_name, code, nc, dc_zip_fields)


def zipperGetSubtype(major_type, code):
    name = major_type.name
    if code not in zipper_subtypes:
        raise KeyError
    if code == "AR00":
        long_name = "Semi/Half Zipper, straight ('regular'), no IpGBT"
    elif code == "BR00":
        long_name = "Five Right Zipper, no IpGBT"
    elif code == "CR00":
        long_name = "Five Left Zipper, no IpGBT"
    elif code == "BS00":
        long_name = "Five Right Zipper, snake, no IpGBT"
    elif code == "AL00":
        long_name = "Semi/Half Zipper with IpGBT"
    nc = code
    return Subtype(major_type, name, long_name, code, nc, dc_zip_fields)


def testerGetSubtype(major_type, code):
    if code not in tester_subtypes:
        raise KeyError
    if code[1] == "4":
        name = "Eng"
        long_name = "Engine Tester "
        if code[2] == "0":
            name = name + "T"
            long_name = long_name + "rev D"
        elif code[2] == "3":
            name = name + "HI"
            long_name = long_name + "HD Interposer rev A"
        else:
            dir = "West"
            if code[2] == "1":
                dir = "East"
            name = name + "LI" + dir[0]
            long_name = long_name + dir + " rev C"
    else:
        if code[2] == "3":
            name = "Wag"
            long_name = "Wagon "
            if code[3] == "1":
                long_name = long_name + "Tester"
                name = name + "T"
            elif code[3] == "2":
                long_name = long_name + "Wheel"
                name = name + "Whl"
            else:
                dir = "West"
                if code[3] == "3":
                    dir = "East"
                name = name + "AD" + dir[0]
                long_name = long_name + "Adapter " + dir
        elif code[2] == "2":
            name = "ZCU"
            long_name = "ZCU102"
        elif code[2] == "1":
            long_name = "Hexacontroller"
            name = "HXCTR" + code[3]
            if code[3] == "1":
                long_name = long_name + code[3] + " (Kria-based)"
        else:
            name = "TBT"
            long_name = "Tileboard Tester"
            if code[3] == "2":
                name = name + code[3]
                long_name = long_name + " V2"
    nc = code
    return Subtype(major_type, name, long_name, code, nc, dc_zip_fields)


@register
class DCDCBoard:
    name = "DC/DC Board"
    long_name = "DC/DC Board"
    code = "DC"
    numeric_code = 16
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return dc_subtype

    @staticmethod
    def getSubtypeByCode(code):
        return dcGetSubtype(DCDCBoard, code)


@register
class ZipperBoard:
    name = "Zipper Board"
    long_name = "Zipper Board"
    code = "ZP"
    numeric_code = 17
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return zipper_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return zipperGetSubtype(ZipperBoard, code)


@register
class Testers:
    name = "Testers"
    long_name = "Testers"
    code = "TS"
    numeric_code = 90
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return tester_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return testerGetSubtype(Testers, code)
