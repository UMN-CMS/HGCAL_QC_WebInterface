import itertools as it 

from label_authority.registry import register  
from label_authority.serial_schema import (MappingField, NumericField,
                                           SerialSchema)

from .types import Subtype

econ_subtypes = (["1F11", "1F12", "1F21", "1F22", "1F90", "1RT0", "2F00", "2RT0", "2LB0", "25R0", "25L0"])

econ_fields = SerialSchema(
    NumericField("SerialNumber", "Serial number", 6)
)

def econSubtypeByCode(major_type, code):
    if code not in econ_subtypes:
        raise KeyError
    if code[0] == "1":  #PROTOTYPES
        long_name = "Prototype "
        if code[1] == "F":
            name = "CM Full"
            long_name = long_name + "Full, ECON-T"
            if code[2] == "1":
                name = name + ", ECON-T"
                long_name = long_name + " only,"
                if code[3] == "1":
                    name = name + " COB"
                    long_name = long_name + " Chip-on-board"
                else:
                    long_name = long_name + " packaged board"
            elif code[2] == "2":
                long_name = long_name + " ECON-D"
                if code[3] == "1":
                    name = name + ", ECON-D COB"
                    long_name = long_name + " COB"
            else:
                name = "CM dummy"
                long_name = "Full, mechanical dummy"
        else:
            name = "Partial, RT, ECON-T + ECON-D"
            long_name = long_name + "Partial, Semit-Right/Half-Top, ECON-T + ECON-D"
    else:      #PRODUCTION
        pre = "Production"
        n = "Partial "
        if code[2] == "0":
            name = "Full, ECON-D + ECON-T"
            long_name = pre + name
        elif code[2] == "T":
            name = n + "RT"
            long_name = pre + " Partial Semi-Right/Half-Top"
        elif code[2] == "B":
            name = n + "LB"
            long_name = pre + " Partial Semi-Left/Half-Top"
        elif code[2] == "R":
            name = n + "5R"
            long_name = pre + "Five-Right"
        else:
            name = n + "5L"
            long_name = pre + "Five-Left"

    nc = code

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
