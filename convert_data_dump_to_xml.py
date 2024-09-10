import os
import json
import argparse
import xmltodict


def parse_args():
    parser = argparse.ArgumentParser(description="Convert JSON file to XML.")
    parser.add_argument('-i', '--input_json',
                        help="Path to the input JSON file.")
    parser.add_argument('-o', '--output_xml',
                        help="Path to the output XML file.")
    return parser.parse_args()


def read_json_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input JSON file '{file_path}' not found.")

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def wrap_repeating_fields(json_data):
    array_fields = ['external_ids', 'links', 'locations',
                    'names', 'relationships', 'types', 'domains']
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, list):
                if key == 'all':
                    # Special case for 'all': repeat <all> tag for each value without nesting
                    json_data[key] = [item for item in value]
                elif key in array_fields:
                    # Handle other regular array fields
                    json_data[key] = {
                        key[:-1]: [wrap_repeating_fields(item) for item in value]}
            elif isinstance(value, dict):
                json_data[key] = wrap_repeating_fields(value)
    elif isinstance(json_data, list):
        json_data = [wrap_repeating_fields(item) for item in json_data]
    return json_data


def convert_data_dump_to_xml(json_data):
    json_data = wrap_repeating_fields(json_data)

    # Ensure there's a root element
    if isinstance(json_data, list):
        json_data = {"records": {"record": json_data}}
    elif isinstance(json_data, dict):
        json_data = {"record": json_data}
    xml_data = xmltodict.unparse(json_data, pretty=True, full_document=False)
    # Add XML declaration
    xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_data

    return xml_data


def write_xml_file(xml_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(xml_data)


def main():
    args = parse_args()
    json_data = read_json_file(args.input_json)
    xml_data = convert_json_to_xml(json_data)
    write_xml_file(xml_data, args.output_xml)
    print(f"Successfully converted JSON to XML. Output saved to: {args.output_xml}")


if __name__ == "__main__":
    main()
