from bs4 import BeautifulSoup
from datetime import datetime


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


def get_total_amounts(flights):
    total_amounts = []
    for flight in flights['flights']:
        amount = 0
        for charge in flight['pricing']['service_charges']:
            if charge['charge_type'] == 'TotalAmount':
                amount += float(charge['price'])
        total_amounts.append(amount)

    return total_amounts


def get_by(key, flights, func):
    handlers = {'duration': get_durations, 'price': get_total_amounts}
    all_values = handlers[key](flights)
    flights['flights'] = [flights['flights'][idx] for idx, val in enumerate(all_values) if val == func(all_values)]
    return flights


def get_durations(flights):
    durations = []
    for flight in flights['flights']:
        duration = calculate_flight_duration(flight, 'onward_itinerary')
        if flights['return_tickets']:
            return_duration = calculate_flight_duration(flight, 'return_itinerary')
            duration = duration + return_duration
        durations.append(duration)

    return durations


def calculate_flight_duration(flight, key):
    departure_time = datetime.strptime(flight[key][0]['departure_time'], '%Y-%m-%dT%H%M')
    arrival_time = datetime.strptime(flight[key][-1]['arrival_time'], '%Y-%m-%dT%H%M')
    return arrival_time - departure_time


def get_optimal(flights):
    durations = get_durations(flights)
    average_time = sum([duration.total_seconds() for duration in durations]) / len(durations)
    flights['flights'] = [flight for idx, flight in enumerate(flights['flights']) if durations[idx].total_seconds() <= average_time]
    return get_by('price', flights, min)


def check_and_set_params(response1, response2, dict_to_set, set_key):
    if response1 != response2:
        dict_to_set['first'][set_key] = response1
        dict_to_set['second'][set_key] = response2


def get_service_charges_types(service_charges):
    return set(data['type'] for data in service_charges)


def get_difference(response1, response2):
    difference = {'first': {}, 'second': {}}
    flights1 = response1['flights'][0]['onward_itinerary']
    flights2 = response2['flights'][0]['onward_itinerary']
    check_and_set_params(response1['return_tickets'], response2['return_tickets'], difference, 'return_itinerary')
    check_and_set_params(flights1[0]['source'], flights2[0]['source'], difference, 'source')
    check_and_set_params(flights1[-1]['destination'], flights2[-1]['destination'], difference, 'destination')
    check_and_set_params(flights1[0]['departure_time'], flights2[0]['departure_time'], difference, 'departure_date')

    pricing1 = response1['flights'][0]['pricing']
    pricing2 = response2['flights'][0]['pricing']
    check_and_set_params(pricing1['currency'], pricing2['currency'], difference, 'currency')

    type1 = sorted(list(get_service_charges_types(pricing1['service_charges'])))
    type2 = sorted(list(get_service_charges_types(pricing2['service_charges'])))
    check_and_set_params(type1, type2, difference, 'type')

    return difference


if __name__ == '__main__':
    xml_file_paths = ('xml_files/RS_Via-3.xml', 'xml_files/RS_ViaOW.xml')
    all_flights = []
    for file in xml_file_paths:
        flights = get_flights(file)
        all_flights.append(flights)
        # print(get_at_extreme_prices(flights, min))
        # print(get_by_duration(flights, min))
        # print(get_optimal(flights))

    print(get_difference(all_flights[0], all_flights[1]))
