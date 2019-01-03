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
        'carrier_id': flight_tag.find('Carrier').get('id'),
        'carrier_name': flight_tag.find('Carrier').text,
        'flight_number': flight_tag.find('FlightNumber').text,
        'source': flight_tag.find('Source').text,
        'destination': flight_tag.find('Destination').text,
        'departure_time': flight_tag.find('DepartureTimeStamp').text,
        'arrival_time': flight_tag.find('ArrivalTimeStamp').text,
        'class': flight_tag.find('Class').text,
        'number_of_stops': flight_tag.find('NumberOfStops').text,
        'fare_basis': flight_tag.find('FareBasis').text.strip(),
        'warning_text': flight_tag.find('WarningText').text.strip(),
        'ticket_type': flight_tag.find('TicketType').text
    }


def add_flight_data_to_dict(soup_obj, itinerary_type, data, flight_number, key):
    flight_tags = soup_obj.find(itinerary_type).find_all('Flight')
    [data['flights'][flight_number][key].append(get_flight_data(flight_tag)) for flight_tag in flight_tags]


def add_service_charges(service_charges_tags, data):
    for i, charge in enumerate(service_charges_tags):
        data.append({})
        data[i]['type'] = charge.get('type')
        data[i]['charge_type'] = charge.get('ChargeType')
        data[i]['price'] = charge.text


def from_xml_to_dict(xml_data):
    soup = BeautifulSoup(xml_data, features='xml')
    data = dict()
    flights = data['flights'] = []
    data['return_tickets'] = get_tickets_type(xml_data)
    data['request_time'] = soup.find('AirFareSearchResponse').get('RequestTime')
    data['response_time'] = soup.find('AirFareSearchResponse').get('ResponseTime')
    data['request_id'] = soup.find('RequestId').text

    flights_tags = soup.find('PricedItineraries').children
    clean_flights_tags = [tag for tag in flights_tags if tag != '\n']

    for num, tag in enumerate(clean_flights_tags):
        flights.append({'onward_itinerary': []})
        add_flight_data_to_dict(tag, 'OnwardPricedItinerary', data, num, 'onward_itinerary')

        if data['return_tickets']:
            flights[num]['return_itinerary'] = []
            add_flight_data_to_dict(tag, 'ReturnPricedItinerary', data, num, 'return_itinerary')

        pricing = flights[num]['pricing'] = {'currency': tag.find('Pricing').get('currency')}
        pricing['service_charges'] = []

        service_charges = tag.find('Pricing').find_all('ServiceCharges')
        add_service_charges(service_charges, pricing['service_charges'])

    return data


def get_flights(xml_file_path):
    xml_data = get_xml_data(xml_file_path)
    return from_xml_to_dict(xml_data)


if __name__ == '__main__':
    xml_file_paths = ('xml_files/RS_Via-3.xml', 'xml_files/RS_ViaOW.xml')
    for file in xml_file_paths:
        print(get_flights(file))
