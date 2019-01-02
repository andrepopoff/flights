import json
from bs4 import BeautifulSoup


def get_xml_data(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def get_tickets_type(xml_data):
    if 'ReturnPricedItinerary' in xml_data:
        return 1
    return 0


def get_flight_data(flight_tag):
    return {
        'carrier-id': flight_tag.find('Carrier').get('id'),
        'carrier-name': flight_tag.find('Carrier').text,
        'flight-number': flight_tag.find('FlightNumber').text,
        'source': flight_tag.find('Source').text,
        'destination': flight_tag.find('Destination').text,
        'departure-time': flight_tag.find('DepartureTimeStamp').text,
        'arrival-time': flight_tag.find('ArrivalTimeStamp').text,
        'class': flight_tag.find('Class').text,
        'number-of-stops': flight_tag.find('NumberOfStops').text,
        'fare-basis': flight_tag.find('FareBasis').text.strip(),
        'warning-text': flight_tag.find('WarningText').text.strip(),
        'ticket-type': flight_tag.find('TicketType').text
    }


def from_xml_to_dict(xml_data):
    soup = BeautifulSoup(xml_data, features='xml')
    data = {'response': {'flights': {'onward': [], 'return': []}}}

    data['response']['return-tickets'] = get_tickets_type(xml_data)
    data['response']['request-time'] = soup.find('AirFareSearchResponse').get('RequestTime')
    data['response']['response-time'] = soup.find('AirFareSearchResponse').get('ResponseTime')
    data['response']['request-id'] = soup.find('RequestId').text

    flights_tags = soup.find('PricedItineraries').children
    clean_flights_tags = [tag for tag in flights_tags if tag != '\n']

    for tag in clean_flights_tags:
        onward_flight_tags = tag.find('OnwardPricedItinerary').find_all('Flight')
        [data['response']['flights']['onward'].append(get_flight_data(flight_tag)) for flight_tag in onward_flight_tags]

        if data['response']['return-tickets']:
            return_flight_tags = tag.find('ReturnPricedItinerary').find_all('Flight')
            [data['response']['flights']['return'].append(get_flight_data(flight_tag)) for flight_tag in return_flight_tags]

    print(len(clean_flights_tags))
    print(len(data['response']['flights']['onward']))
    print(len(data['response']['flights']['return']))
    print(data)


def main():
    xml_file_paths = ('xml_files/RS_Via-3.xml', 'xml_files/RS_ViaOW.xml')
    for file in xml_file_paths:
        xml_data = get_xml_data(file)
        data = from_xml_to_dict(xml_data)


if __name__ == '__main__':
    main()