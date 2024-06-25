import itertools as it

from label_authority.registry import register  # in every file
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

w_m_subtypes = (["MBD", "WFH", "WBH"])

w_m_fields = SerialSchema(
    NumericField("VersionNumber", "Version Number of the board", 1),
    NumericField("BatchNumber", "Batch number in which the board was produced", 2),
    NumericField("SerialNumber", "Serial number within batch", 4),
)

@register
class WMBoards:
    name = "WM-Boards"
    long_name = "Wingboards and Motherboards"
    code = "WM"
    numeric_code = 28
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return w_m_subtypes

    @staticmethod
    def getSubtypeByCode(sub_code):
        long_name = WMBoards.long_name
        major_type = WMBoards
        if sub_code not in w_m_subtypes:
            raise KeyError
        if sub_code == "MBD":
            nc = "100"
            name = "MB"
            long_name = "Motherboard"
        elif sub_code == "WFH":
            nc = "201"
            name = "FH/HD"
            long_name = "FH/HD Wingboard"
        elif sub_code == "WBH":
            nc = "301"
            name = "BH/LD"
            long_name = "BH/LD Wingboard"

        return Subtype(major_type, name, long_name, sub_code, nc, w_m_fields)




