import json
from bs4 import BeautifulSoup


def get_xml_data(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def get_tickets_type(xml_data):
    if 'ReturnPricedItinerary' in xml_data:
        return 1
    return 0


def from_xml_to_dict(xml_data):
    soup = BeautifulSoup(xml_data, features='xml')
    data = {'response': {'flights': {'onward': [], 'return': []}}}
    data['response']['return-tickets'] = get_tickets_type(xml_data)
    data['response']['request-time'] = soup.find('AirFareSearchResponse').get('RequestTime')
    data['response']['response-time'] = soup.find('AirFareSearchResponse').get('ResponseTime')
    data['response']['request-id'] = soup.find('RequestId').text
    flights_tags = soup.find('PricedItineraries').children
    clean_flights_tags = [tag for tag in flights_tags if tag != '\n']
    print(len(clean_flights_tags))
    print(data)


def main():
    xml_file_paths = ('xml_files/RS_Via-3.xml', 'xml_files/RS_ViaOW.xml')
    for file in xml_file_paths:
        xml_data = get_xml_data(file)
        data = from_xml_to_dict(xml_data)


if __name__ == '__main__':
    main()