import json
from bs4 import BeautifulSoup


def get_xml_data(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def from_xml_to_dict(xml_data):
    pass


def main():
    xml_file_paths = ('xml_files/RS_Via-3.xml', 'xml_files/RS_ViaOW.xml')
    for file in xml_file_paths:
        xml_data = get_xml_data(file)
        data = from_xml_to_dict(xml_data)


if __name__ == '__main__':
    main()