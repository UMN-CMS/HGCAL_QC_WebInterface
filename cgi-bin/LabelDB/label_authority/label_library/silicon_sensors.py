import itertools as it
from itertools import product

from label_authority.registry import register
from label_authority.serial_schema import MappingField, NumericField, SerialSchema

from .types import Subtype

thickness = ["1", "2", "3"]
cut = ["F", "T", "B", "L", "R", "M", "S"]
sensor = ["XX", "TP", "BT", "TL", "TR", "BL", "BR"]

silicon_subtypes = ["".join(sil) for sil in list(product(thickness, cut, sensor))]

sensDict = {
    "1": "300 um",
    "2": "200 um",
    "3": "120 um",
    "4": "300 um",
    "5": "200 um",
    "6": "120 um",
}

silicon_fields = SerialSchema(
    # MappingField("SensorThickness", "Sensor thickness", 1, sensDict),
    NumericField("BatchNumber", "Batch or lot number", 6),
)


def siSubtypeByCode(major_type, code):
    if code not in silicon_subtypes:
        raise KeyError

    thickDict = {"1": "120 um", "2": "200 um", "3": "300 um"}
    cutDict = {
        "F": "Full",
        "T": "Top",
        "B": "Bottom",
        "L": "Left",
        "R": "Right",
        "5": "Five",
        "M": "Half-moon or test structure",
        "S": "Whole sensor",
    }
    sensorDict = {
        "XX": "whole or active sensor",
        "TP": "top half-moon",
        "BT": "bottom half-moon",
        "TL": "top-left half-moon",
        "TR": "top-right half-moon",
        "BL": "bottom-left half-moon",
        "BR": "bottom-right half-moon",
    }

    numCutDict = {
        "F": "0",
        "T": "1",
        "B": "2",
        "L": "3",
        "R": "4",
        "5": "5",
        "M": "8",
        "S": "9",
    }
    numSensorDict = {
        "XX": "00",
        "TP": "11",
        "BT": "66",
        "TL": "22",
        "TR": "33",
        "BL": "44",
        "BR": "55",
    }

    name = ""
    long_name = (
        f"{thickDict[code[0]]} {major_type.long_name[:2]} {sensorDict[code[2:]]}"
    )
    nc = code[0] + numCutDict[code[1]] + numSensorDict[code[2:]]

    return Subtype(major_type, name, long_name, code, nc, silicon_fields)


@register
class SiliconLDModule:
    name = "LD-Sensor"
    long_name = "LD Silicon Sensor"
    code = "SL"
    numeric_code = 2
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return silicon_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return siSubtypeByCode(SiliconLDModule, code)


@register
class SiliconHDModule:
    name = "HD-Sensor"
    long_name = "HD Silicon Sensor"
    code = "SH"
    numeric_code = 3
    num_subtype_chars = 4

    @staticmethod
    def getAllSubtypes():
        return silicon_subtypes

    @staticmethod
    def getSubtypeByCode(code):
        return siSubtypeByCode(SiliconHDModule, code)
