from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from .registry import getMajorType


@dataclass
class BarcodeSpec:
    """
    Represents the values of a given barcode.
    This class is returned through calls to :py:func:`.decode` and is passed as the sole argument to
    :py:func:`.encode`.

    :param major_type_code: Major type code
    :type major_type_code: str
    :param subtype_code: Major type code
    :type subtype_code: str
    :param field_values: Mapping of field name to value.
    :type field_values: Dict[str,Any]
    """

    major_type_code: str
    subtype_code: str
    field_values: Dict[str, Any]


def decode(barcode: str) -> BarcodeSpec:
    """Decode a barcode.
    

    :param barcode: Barcode to decode
    :type barcode: str
    :return: The decoded values of the barcode
    :rtype: :py:class:`.BarcodeSpec`
    """

    if len(barcode) != 15:
        raise ValueError(f'Barcode "{barcode}" has length {len(barcode)} != 15.')
    if not barcode.isalnum():
        raise ValueError(f'Barcode "{barcode}" contains non alphanumeric characters.')
    if barcode[:3] != "320":
        raise ValueError(f'Barcode "{barcode}" starts with {barcode[:3]} != "320"')

    barcode = barcode[3:]

    major_type_code = barcode[:2]
    major_type = getMajorType(major_type_code)

    subtype_length = major_type.num_subtype_chars
    subtype_code = barcode[2 : 2 + subtype_length]
    subtype = major_type.getSubtypeByCode(subtype_code) #somethings wrong here too

    serial = barcode[2 + subtype_length :]
    serial_schema = subtype.serial_schema

    return BarcodeSpec(major_type_code, subtype_code, serial_schema.decode(serial))


def encode(barcode_spec: BarcodeSpec) -> str:
    """Decode a barcode.
    

    :param barcode_spec: Values to encode
    :type barcode_spec: :py:class:`.BarcodeSpec`
    :return: Encoded barcode
    :rtype: str
    """

    parts = ["320"]

    major_type_code = barcode_spec.major_type_code
    subtype_code = barcode_spec.subtype_code
    field_values = barcode_spec.field_values

    parts.append(major_type_code)
    parts.append(subtype_code)

    mt = getMajorType(major_type_code)
    st = mt.getSubtypeByCode(subtype_code)
    serial_schema = st.serial_schema

    serial = serial_schema.encode(field_values)

    parts.append(serial)

    return "".join(parts)
