import itertools as it
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from .exceptions import FieldError, InvalidSchema

T = TypeVar("T")


class FieldValue(Generic[T]):
    """Simple container representing the value of a field.
    Contains only two members :py:attr:`FieldValue.value` and  :py:attr:`FieldValue.code` which represent either the value or the code for the specific field.

    When used for encoding, the user may provide only the value or the code.
    If both the value and the code are provided, the user is responsible for ensuring they are consistent for the given schema, or an exception will be raised.

    When returned from a decoding function, both the value and the field are populated.


    Note that this class can be constructed from either another :py:class`FieldValue` or from the code and value itself.


    :param value: Value of the field
    :type value: Any
    :param code: Code of the field
    :type code: str
    """

    def __make(self, value, code):
        self.value = value
        self.code = code

    def __init__(self, value=None, code=None):
        if value is None and code is None:
            raise ValueError("Both value and code cannot be none")
        if isinstance(value, FieldValue):
            self.__make(value.value, value.code)
        else:
            self.__make(value, code)

    def __eq__(self, other):
        fv = FieldValue(other)
        return ((self.value == fv.value) or (fv.value is None)) and (
            (self.code == fv.code) or (fv.code is None)
        )

    def __str__(self):
        x = ", ".join(str(y) for y in [self.value, self.code] if y is not None)
        return f"FieldValue({x})"

    def __repr__(self):
        return str(self)


class Field(ABC, Generic[T]):
    """A field describes the meaning of a part of the the non-type portion of the barcode.
    Fields translate describe how codes, the alpha-numeric values appearing the barcode, should be interpretted as values.

    :param name: The name of the field
    :type name: str
    :param description: A description of the field
    :type description: str
    :param width: The size of the field, in characters. An N width field always occupies exactly N characters in the barcode.
    :type width: int

    """

    def __init__(self, name: str, description: str, width: int):
        self.name = name
        self.description = description
        self.width = width

    @abstractmethod
    def _valueToCode(self, value: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def _codeToValue(self, code: str) -> T:
        raise NotImplementedError

    def getValueOptions(self):
        """Get a sequence of possible values for this field.

        :return: A list of possible values for the field.
        :rtype: Sequence[T]
        """
        raise NotImplementedError

    def valueToCode(self, value: Union[FieldValue[T], T]) -> str:
        """
        :param value: Value to encode
        :type value: T
        :return: The encoded value, always a :py:attr:`Field.width` length string.
        :rtype: str
        """
        fv: FieldValue = FieldValue(value)
        raw_value = fv.value
        ret = self._valueToCode(raw_value)

        if fv.code is not None and fv.value is not None:
            if fv.code != ret:
                raise FieldError()

        assert len(ret) == self.width
        return ret

    def codeToValue(self, code: str) -> FieldValue[T]:
        """
        :param value: Value to encode
        :type value: T
        :return: The encoded value, always a :py:attr:`Field.width` length string.
        :rtype: str
        """
        if not isinstance(code, str):
            raise TypeError(f'Code "{code}" is not a string')
        if len(code) != self.width:
            raise FieldError(
                f'Code "{code}" is not a valid code for field '
                f'"{self.name}" of type {self.__class__.__name__}'
            )

        ret = self._codeToValue(code)

        return FieldValue(ret, code)

    def __str__(self) -> str:
        return f"Field({self.name}, width = {self.width})"

    def __repr__(self) -> str:
        return str(self)


U = TypeVar("U")


class MappingField(Generic[U], Field[U]):
    def __init__(self, name: str, description: str, width: int, mapping: Dict[str, U]):
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
        return [FieldValue(value, code) for code, value in self.mapping.items()]

    def _valueToCode(self, value):
        try:
            return self.inv_mapping[value]
        except KeyError:
            raise FieldError()

    def _codeToValue(self, code):
        try:
            return self.mapping[code]
        except KeyError:
            raise FieldError()


class NumericField(Field[int]):
    class Range:
        def __init__(self, field):
            self.field = field

        def __len__(self):
            return 10**self.field.width

        def __getitem__(self, i):
            if i < 0 or i > len(self):
                raise KeyError()
            return FieldValue(i, self.field._valueToCode(i))

        def toString(self):
            return f"0-{len(self) - 1}"

    def __init__(self, name: str, description: str, width: int):
        super().__init__(name, description, width)

    def getValueOptions(self):
        return NumericField.Range(self)

    def _valueToCode(self, value):
        if not isinstance(value, int):
            raise FieldError(f"Value is not an int")
        if value not in range(0, 10 ** (self.width)):
            raise FieldError("Value is not in range")
        ret = "{1:0{0}}".format(self.width, int(value))
        return ret

    def _codeToValue(self, code):
        try:
            x = int(code)
        except ValueError as e:
            raise FieldError(f"Field cannot be converted to an integer")

        if x not in range(0, 10 ** (self.width)):
            raise FieldError("Code is not in range")
        return x


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
        """Total size of this schema, being the sum of the all the field widths."""
        return sum(p.width for p in self.parts)

    def encode(self, mapping: Dict[str, Union[FieldValue, Any]]) -> str:
        """Translate a dictionary of field values in to a encoded string.


        :param mapping: Mapping of the form :py:attr:`Field.name` -> value, describing the value that each field should take. The value may be either a proper `.FieldValue` or any other type. If the value is not `.FieldValue`, it is converted internally.
        :type mapping: Dict[str,Any]
        :return: Encoded serial code
        """
        code_parts = [
            p.valueToCode(FieldValue(mapping[p.name]).value) for p in self.parts
        ]
        code = "".join(code_parts)
        return code

    def decode(self, barcode: str) -> Dict[str, FieldValue]:
        """Determine the values of all the fields in an encoded serial number.

        :param barcode: Encoded serial string
        :type barcode: str
        :return: Mapping of the form :py:attr:`Field.name` -> :py:class:`FieldValue`, describing the value of each field
        :rtype: Dict[str,FieldValue]
        """
        if len(barcode) != self.serial_length:
            raise FieldError(
                f'Barcode "{barcode}" does not have correct length {self.serial_length}'
            )
        bi = iter(barcode)
        decoded: Dict[str, FieldValue] = {}
        for i, p in enumerate(self.parts):
            icode = it.islice(bi, None, p.width)
            code = "".join(icode)
            decoded[p.name] = FieldValue(p.codeToValue(code), code)
        return decoded

    def getPossibleValues(self) -> Dict[str, Sequence]:
        return {p.name: p.getValueOptions() for p in self.parts}


    def getPart(self, name):
        return next(x for x in self.parts if x.name == name)

    def __str__(self) -> str:
        return str(self.parts)
