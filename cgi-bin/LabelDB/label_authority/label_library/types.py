from abc import ABC, abstractmethod
from typing import Any, Optional

from label_authority.serial_schema import SerialSchema


class Subtype:
    """Subtype of a major type.

    :param major_type: Major type for this subtype
    :type major_type: Any
    :param name: Short name describing the subtype, without reference to major type.
    :type name: str
    :param long_name: Long name describing the subtype, without reference to major type.
    :type long_name: str
    :param code: Alphanumeric code for this subtype, as would appear in the barcode.
    :type code: str
    :param numeric_code: Integer code for this subtype
    :type numeric_code: int
    :param serial_schema: 
    :type serial_schema: :py:class:`label_authority.serial_schema.SerialSchema`
    :param complete_long_name: If provided, use this name as the complete long name (including major type)
    :type complete_long_name: Optional[str]
    :param complete_short_name: If provided, use this name as the complete short name (including major type)
    :type complete_short_name: Optional[str]


    """

    def __init__(
        self,
        major_type: Any,
        name: str,
        long_name: str,
        code: str,
        numeric_code: int,
        serial_schema: SerialSchema,
        complete_long_name: Optional[str] = None,
        complete_short_name: Optional[str] = None,
    ):

        self.major_type = major_type
        self.name = name
        self.long_name = long_name
        self.code = code
        self.numeric_code = numeric_code
        self.serial_schema = serial_schema
        self._complete_long_name = complete_long_name
        self._complete_short_name = complete_short_name


        

    def __str__(self) -> str:
        return f"Subtype({self.name}, {self.code})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def complete_long_name(self) -> str:
        if self._complete_long_name:
            return self._complete_long_name
        else:
            return f"{self.major_type.long_name} - {self.long_name}"

    @property
    def complete_short_name(self) -> str:
        if self._complete_short_name:
            return self._complete_short_name
        else:
            return f"{self.major_type.name} - {self.name}"
