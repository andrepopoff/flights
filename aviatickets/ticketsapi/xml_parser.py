import json
from bs4 import BeautifulSoup


def get_xml_data(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def main():
    xml_file_paths = ('xml_files/RS_Via-3.xml', 'xml_files/RS_ViaOW.xml')
    for file in xml_file_paths:
        xml_data = get_xml_data(file)
        print(xml_data)


if __name__ == '__main__':
    main()