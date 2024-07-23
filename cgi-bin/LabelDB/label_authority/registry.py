from .exceptions import InvalidBarcode, InvalidSchema

major_type_registry = {}


def checkValidClass(cls):
    needs_attrs = ["name", "long_name", "code", "numeric_code", "num_subtype_chars"]
    needs_methods = ["getSubtypeByCode", "getAllSubtypes"]
    if not callable(cls):
        raise InvalidSchema(f"Argument to register must be a callable.")

    to_test = cls()

    for attr in needs_attrs:
        if not hasattr(to_test, attr):
            raise InvalidSchema(
                f'Class {to_test.__class__.__name__} does not have required member "{attr}"'
            )
    for method in needs_methods:
        if not hasattr(to_test, method) or not callable(getattr(to_test, method)):
            raise InvalidSchema(
                f'Class {to_test.__class__.__name__} does not have required callable method "{method}"'
            )


def register(cls):
    """Registry"""
    checkValidClass(cls)

    def __str__(self):
        return f"MajorType({self.name}, {self.code})"

    def __repr__(self):
        return str(self)

    if cls.__str__ is object.__str__:
        cls.__str__ = __str__
    if cls.__repr__ is object.__repr__:
        cls.__repr__ = __repr__

    to_add = cls()
    major_type_registry[to_add.code] = to_add
    return cls


def getMajorType(code):
    """Get a an object satisfying the major type specification.

    :param code: Major type code defining the desired major type
    :type code: str
    """

    major_type = major_type_registry[code]
    return major_type


def getAllMajorTypes():
    """Get a dictionary containing all major types known to the library."""
    return major_type_registry
