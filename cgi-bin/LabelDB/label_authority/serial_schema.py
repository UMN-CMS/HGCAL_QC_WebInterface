import itertools as it
from collections.abc import Sequence
from abc import abstractmethod, ABC
from typing import Any, Dict, Generic, TypeVar, Union

from .exceptions import InvalidSchema

T = TypeVar("T")



class Field(ABC,Generic[T]):
    """A field describes the meaning of a part of the the non-type portion of the barcode.
    Fields translate describe how codes, the alpha-numeric values appearing the barcode, should be interpretted as values.

    :param name: The name of the field
    :type name: str
    :param description: A description of the field
    :type description: str
    :param width: The size of the field, in characters. An N width field always occupies exactly N characters in the barcode.
    :type width: int

    """

    qualitative = False

    def __init__(self, name: str, description: str, width: int):
        self.name = name
        self.description = description
        self.width = width

    
    @abstractmethod
    def _isValidValue(self, value: T) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _isValidCode(self, code: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _valueToCode(self, value: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def _codeToValue(self, code: str) -> T:
        raise NotImplementedError

    def isValidValue(self, value: T) -> bool:
        """ Check if a provided value

        :param value: Value to check.
        :type value: T
        :return: True if the value is valid, False otherwise
        :rtype: bool
        """
        return self._isValidValue(value)

    def isValidCode(self, code: str) -> bool:
        """ Check if a provided code is valid.

        :param code: Code to check.
        :type code: str
        :return: True if the code is valid, False otherwise
        :rtype: bool
        """

        if not isinstance(code,str):
            return False

        if len(code) != self.width:
            return False
            
        return self._isValidCode(code)

    def getValueOptions(self):
        """Get a sequence of possible values for this field.

        :return: A list of possible values for the field.
        :rtype: Sequence[T]
        """
        raise NotImplementedError

    def valueToCode(self, value: T) -> str:
        """
        :param value: Value to encode
        :type value: T
        :return: The encoded value, always a :py:attr:`Field.width` length string.
        :rtype: str
        """
        if not self.isValidValue(value):
            raise ValueError(
                f'Value "{value}" is not a valid value for field '
                f'"{self.name}" of class {self.__class__.__name__}'
            )
        #ret = "{1:0{0}}".format(self.width, self._valueToCode(value))
        ret = self._valueToCode(value)

        if len(ret) > self.width:
            raise ValueError()
        return ret

    def codeToValue(self, code: str) -> T:
        """
        :param value: Value to encode
        :type value: T
        :return: The encoded value, always a :py:attr:`Field.width` length string.
        :rtype: str
        """
        if not self.isValidCode(code):
            raise ValueError(
                f'Code "{code}" is not a valid code for field '
                f'"{self.name}" of type {self.__class__.__name__}'
            )
        ret = self._codeToValue(code)
        return ret

    def __str__(self) -> str:
        return f"Field({self.name}, width = {self.width})"

    def __repr__(self) -> str:
        return str(self)


class MappingField(Field[Any]):
    qualitative = True

    def __init__(
        self, name: str, description: str, width: int, mapping: Dict[str, Any]
    ):
        """Mapping is a mapping from code->value

        :param name: The name of the field
        :type name: str
        :param description: A description of the field
        :type description: str
        :param width: The size of the field, in characters. An N width field always occupies exactly N characters in the barcode.
        :type width: int
        :param mapping: Describes the meaning of code values
        :type mapping: Dict[str,Any]
        """

        super().__init__(name, description, width)
        self.mapping = mapping
        self.inv_mapping = {v: k for k, v in self.mapping.items()}
        for k, v in self.mapping.items():
            if len(str(k)) > self.width:
                raise InvalidSchema(
                    f"Invalid schema for field {self.name}:\n"
                    f"Key {k} has value {v} with length {len(str(k))} > width {self.width} "
                )
            if not (isinstance(k, str) and isinstance(v, str)):
                raise InvalidSchema(
                    "Mapping fields must map from strings to strings."
                    f"Invalid pair ({k},{v})"
                )

    def getValueOptions(self):
        return list(self.inv_mapping)

    def _valueToCode(self, value):
        return self.inv_mapping[value]

    def _codeToValue(self, code):
        return self.mapping[code]

    def _isValidCode(self, code):
        return code in self.mapping

    def _isValidValue(self, value):
        return value in self.inv_mapping


class NumericField(Field[int]):
    qualitative = False

    def __init__(self, name: str, description: str, width: int):
        super().__init__(name, description, width)

    def getValueOptions(self):
        return range(0, 10 ** (self.width))

    def _valueToCode(self, value):
        ret = "{1:0{0}}".format(self.width, int(value))
        return ret

    def _codeToValue(self, code):
        return int(code)

    def _isValidCode(self, code):
        try:
            int(code)
        except ValueError as e:
            return False
        return int(code) in range(0, 10 ** (self.width))

    def _isValidValue(self, value):
        if not isinstance(value,int):
            return False
        return value in range(0, 10 ** (self.width))


class SerialSchema:
    """A schema describing the fields that make up the serial part of the barcode.
    The schema is a series of :py:class:`Field`, which each describe how to interpret a certain portion of the serial code.

    :param parts: The fields making up this schema.
    :type parts: :py:class:`Field`
    """

    def __init__(self, *parts: Field):
        self.parts = list(parts)

    @property
    def serial_length(self) -> int:
        """Total size of this schema, being the sum of the all the field widths.
        """
        return sum(p.width for p in self.parts)

    def encode(self, mapping: Dict[str, Any]) -> str:
        """Translate a dictionary of field values in to a encoded string.

        :param mapping: Mapping of the form :py:attr:`Field.name` -> value, describing the value that each field should take.
        :type mapping: Dict[str,Any]
        :return: Encoded serial code
        """
        code_parts = [p.valueToCode(mapping[p.name]) for p in self.parts]
        code = "".join(code_parts)
        return code

    def decode(self, barcode: str) -> Dict[str, Any]:
        """Determine the values of all the fields in an encoded serial number.

        :param barcode: Encoded serial string
        :type barcode: str
        :return: Mapping of the form :py:attr:`Field.name` -> value, describing the value of each field
        :rtype: Dict[str,Any]
        """
        if len(barcode) != self.serial_length:
            raise ValueError(
                f'Barcode "{barcode}" does not have correct length {self.serial_length}'
            )
        i = iter(barcode)
        decoded = {
            p.name: p.codeToValue("".join(it.islice(i, None, p.width)))
            for p in self.parts
        }
        return decoded

    def getPossibleValues(self) -> Dict[str, Sequence]:
        return {p.name: p.getValueOptions() for p in self.parts}

    def __str__(self) -> str:
        return str(self.parts)
