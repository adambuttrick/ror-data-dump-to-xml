import os
import json
import argparse
import random
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from convert_data_dump_to_xml import read_json_file, convert_data_dump_to_xml, write_xml_file


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test JSON to XML conversion.")
    parser.add_argument('-i', '--input_json',
                        help="Path to the input JSON file.")
    parser.add_argument('-o', '--output_xml',
                        help="Path to the output XML file.")
    return parser.parse_args()


def load_xml_file(xml_path):
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Output XML file '{xml_path}' not found.")
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return root
    except ParseError as e:
        print(f"XML parsing error: {e}")
        return None


def validate_xml_structure(root):
    if root.tag != 'records':
        print("Error: Root element should be 'records'")
        return False
    for record in root.findall('record'):
        if not validate_record_structure(record):
            return False
    return True


def validate_record_structure(record):
    required_fields = ['admin', 'id', 'locations', 'names', 'status', 'types']
    for field in required_fields:
        if record.find(field) is None:
            print(f"Error: Required field '{field}' is missing in a record")
            return False
    return True


def compare_fields(json_value, xml_element, path=""):
    path_description = f" at path: {path}"

    if json_value is None and (xml_element is None or xml_element.text in [None, '', 'None']):
        return True

    if isinstance(json_value, dict):
        for key, value in json_value.items():
            child_element = xml_element.find(key)
            if child_element is None:
                print(f"Missing key '{key}' in XML{path_description}")
                return False
            if not compare_fields(value, child_element, f"{path}/{key}"):
                return False

    elif isinstance(json_value, list):
        if path.endswith('all'):
            xml_value = xml_element.text if xml_element is not None else None
            if xml_value is None:
                print(f"Missing <all> element in XML{path_description}")
                return False
            if len(json_value) != 1 or str(json_value[0]) != xml_value:
                print(f"Mismatch for 'all'{path_description} - Expected: {json_value}, Found: {xml_value}")
                return False
        else:
            xml_children = list(xml_element) if xml_element is not None else []
            if len(json_value) != len(xml_children):
                print(f"List length mismatch{path_description} - Expected: {len(json_value)}, Found: {len(xml_children)}")
                return False
            for index, item in enumerate(json_value):
                if not compare_fields(item, xml_children[index], f"{path}/{index}"):
                    return False

    else:
        if xml_element is None or xml_element.text != str(json_value):
            xml_text = xml_element.text if xml_element is not None else "None"
            print(f"Mismatch{path_description} - Expected: {json_value}, Found: {xml_text}")
            return False

    return True


def compare_json_xml_record(json_record, xml_record):
    for key, value in json_record.items():
        xml_element = xml_record.find(key)
        if xml_element is None and value is not None:
            print(f"Missing key '{key}' in XML.")
            return False
        if not compare_fields(value, xml_element, key):
            print(f"Mismatch in field: {key}")
            return False
    return True


def sample_random_json_record(json_data):
    return random.choice(json_data)


def find_corresponding_xml_record(json_sample, xml_records):
    json_id = json_sample.get("id")
    for record in xml_records:
        xml_id = record.find('id').text
        if xml_id == json_id:
            return record
    return None


def sample_and_compare(input_json, output_xml, num_samples=10):
    json_data = read_json_file(input_json)
    xml_root = load_xml_file(output_xml)

    if xml_root is None:
        print("XML validation failed: Could not parse XML file")
        return

    if not validate_xml_structure(xml_root):
        print("XML validation failed: Invalid XML structure")
        return

    xml_records = xml_root.findall('.//record')
    for _ in range(num_samples):
        json_sample = sample_random_json_record(json_data)
        xml_record = find_corresponding_xml_record(json_sample, xml_records)
        if xml_record is None:
            print(f"No matching XML record found for ID: {json_sample.get('id')}")
            continue
        if compare_json_xml_record(json_sample, xml_record):
            print(f"Record {json_sample.get('id')} matched successfully!")
        else:
            print(f"Record {json_sample.get('id')} did not match!")


def main():
    args = parse_args()
    sample_and_compare(args.input_json, args.output_xml)


if __name__ == "__main__":
    main()
