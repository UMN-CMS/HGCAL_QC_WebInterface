class Barcode:
    def __init__(self, major_type, subtype, field_values):
        self.major_type = major_type
        self.subtype = subtype
        self.field_values = field_values
        self.barcode = None

    @staticmethod
    def fromParts(major_type, subtype, field_values):
        pass

    @staticmethod
    def fromString(barcode):
        pass

    def parts(self):
        pass
