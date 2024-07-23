import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

ic_subtypes = [
    "RL2",
    "RL4",
    "RLC",
    "RH2",
    "RH4",
    "RHC",
    "ECT",
    "ECD",
    "LGT",
    "SCA",
    "RAF",
    "LDO",
    "LPL",
    "BPL",
    "ALD",
]

ic_fields = SerialSchema(NumericField("SerialNumber", "Serial number", 7))


def icSubtypeByCode(major_type, code):
    icDict = dict(
        [
            (
                "RL2",
                "HGCROC-Silicon, LD package, substrate common ground package (SU02) of HGCROCV3b",
            ),
            (
                "RL4",
                "HGCROC-Silicon, LD package, substrate 'best' separated ground package (SU04) of HGCROCV3b",
            ),
            ("RLC", "HGCROC-Silicon, LD package, substrate HGCROCV3c"),
            (
                "RH2",
                "HGCROC-Silicon, HD package, substrate common ground package (SU02) of HGCROCV3b",
            ),
            (
                "RH4",
                "HGCROC-Silicon, HD package, substrate 'best' separated ground package (SU04) of HGCROCV3b",
            ),
            ("RHC", "HGCROC-Silicon, HD package, substrate HGCROCV3c"),
            ("ECT", "ECON-T (Trigger concentrator)"),
            ("ECD", "ECON-D (DAQ concentrator)"),
            ("LGT", "lpGBT (10 Gbps link and control ASIC)"),
            ("SCA", "GBTSCA (Slow control ASIC)"),
            ("RAF", "Rafael (Clock fanout)"),
            ("LDO", "HGC-LDO (1.2V linear regulator)"),
            ("LPL", "LinPOL12V (2.5V linear regulator)"),
            ("BPL", "BPOL12V (switching regulator)"),
            ("ALD", "ALDOv2 (50V linear regulator for SiPMs)"),
        ]
    )

    numICDict = dict(
        [
            ("RL2", "102"),
            ("RL4", "104"),
            ("RLC", "108"),
            ("RH2", "112"),
            ("RH4", "114"),
            ("RHC", "118"),
            ("ECT", "210"),
            ("ECD", "220"),
            ("LGT", "310"),
            ("SCA", "320"),
            ("RAF", "410"),
            ("LDO", "510"),
            ("LPL", "520"),
            ("BPL", "530"),
            ("ALD", "540"),
        ]
    )

    name = ""
    nc = numICDict[code]
    long_name = icDict[code]

    return Subtype(major_type, name, long_name, code, nc, ic_fields)


@register
class ICComp:
    name = "IC(ASICs etc)"
    long_name = "IC Components"
    code = "IC"
    numeric_code = 0
    num_subtype_chars = 3

    @staticmethod
    def getAllSubtypes():
        return ic_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return icSubtypeByCode(ICComp, code)
