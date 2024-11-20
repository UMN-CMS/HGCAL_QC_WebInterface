import sys
sys.path.append("../../hgcal-label-info/label-authority")

import label_authority as la
decoded = la.decode("320WW10A1BA0001")
schema = la.getMajorType(decoded.major_type_code).getSubtypeByCode(decoded.subtype_code).serial_schema
print(schema.encode(decoded.field_values))
