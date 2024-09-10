# ROR Data Dump to XML Converter

Converts ROR data dump from JSON to XML format with special handling for certain data structures.

## Installation

```
pip install -r requirements.txt
```

## Usage

To convert JSON to XML:
```
python convert_data_dump_to_xml.py -i input.json -o output.xml
```

To run tests on the conversion:
```
python test_conversion.py -i input.json -o output.xml
```

## Conversion Logic: Assumptions and Special Cases

1. Repeating fields ('external_ids', 'links', 'locations', 'names', 'relationships', 'types', 'domains') are wrapped in singular-named parent elements.
2. 'all' field: Repeats <all> tag for each value without nesting.
3. Root element: JSON lists wrapped in {"records": {"record": [...]}}; dictionaries in {"record": {...}}.
4. Recursively processes nested structures.
5. Uses UTF-8 encoding for input/output.
6. Outputs pretty-printed XML.
7. No XML namespace handling.

## Test Logic

The test script (`test_conversion.py`) performs the following validations:

1. XML Well-formedness: Ensures the output XML is well-formed and can be parsed.
2. Structure Validation: Checks if the root element is 'records' and each record contains required fields.
3. Content Comparison: Randomly samples records from the JSON input and compares them with corresponding XML records.
4. Field-by-Field Comparison: Recursively compares all fields in JSON and XML, including special handling for lists and the 'all' field.

To run tests:
```
python test_conversion.py -i input.json -o output.xml
```

The test script will output the results of the validation and comparison processes.


## Notes

- The test script samples a subset of records for detailed comparison. Adjust the `num_samples` parameter in `sample_and_compare()` function for more extensive testing.
- While the converter doesn't handle XML namespaces, the output XML should be sufficient for most use cases of ROR data.
