"""
This file contains all the logic of working with flight data (parsing, computing, etc.)
"""

from bs4 import BeautifulSoup
from datetime import datetime
from re import findall


def get_xml_data(xml_file_path):
    """
    Reads xml file

    :param xml_file_path: <class 'str'> - XML file path
    :return: <class 'str'> - XML file data
    """
    try:
        with open(xml_file_path, 'r') as file:
            return file.read()
    except (FileNotFoundError, OSError, TypeError) as error:
        print('In func {}: {} {}'.format(get_xml_data.__name__, error.__class__, error))


def get_tickets_type(xml_data):
    """
    Find out the presence of return itineraries

    :param xml_data: string with XML data
    :return: <class 'int'> - returns 1 if there are return itineraries.
    If not, it returns 0
    """
    try:
        return 1 if 'ReturnPricedItinerary' in xml_data else 0
    except TypeError as error:
        print('In func {}: {} {}'.format(get_tickets_type.__name__, error.__class__, error))
        return 0


def get_flight_data(flight_tag):
    """
    Parsing flight data from xml tags

    :param flight_tag: <class 'bs4.element.Tag'>
    :return: dictionary with flight data
    """
    try:
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
    except AttributeError as error:
        print('In func {}: {} {}'.format(get_flight_data.__name__, error.__class__, error))


def add_flight_data_to_dict(soup_obj, itinerary_type, data, flight_number, set_key):
    """
    Adds flight data to the dictionary

    :param soup_obj: <class 'bs4.element.Tag'>
    :param itinerary_type: <class 'str'> - 'OnwardPricedItinerary' or 'ReturnPricedItinerary'
    :param data: dictionary with 'flights' key that contain flight data
    :param flight_number: <class 'int'> - flight order in data['flights'] list
    :param set_key: <class 'str'> - key to set data['flights'][flight_number][set_key]
    """
    flight_tags = soup_obj.find(itinerary_type).find_all('Flight')
    [data['flights'][flight_number][set_key].append(get_flight_data(flight_tag)) for flight_tag in flight_tags]


def add_service_charges(service_charges_tags, data):
    """
    Adds service charges data to the dictionary

    :param service_charges_tags: <class 'bs4.element.ResultSet'>
    :param data: list to add service charges data
    """
    for i, charge in enumerate(service_charges_tags):
        data.append({})
        data[i]['type'] = charge.get('type')
        data[i]['charge_type'] = charge.get('ChargeType')
        data[i]['price'] = charge.text


def from_xml_to_dict(xml_data):
    """
    From XML data to the dictionary

    :param xml_data: string with XML data
    :return: dictionary with flights data
    """
    try:
        soup = BeautifulSoup(xml_data, features='xml')
    except TypeError:
        return

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
    """
    Receives flight data

    :param xml_file_path: path where the XML file is located
    :return: dictionary with flights data
    """
    xml_data = get_xml_data(xml_file_path)
    return from_xml_to_dict(xml_data)


def get_total_amounts(flights):
    """
    Calculates the total amount of each flight

    :param flights: dictionary with 'flights' key that contain flight data
    :return: total amounts list that contain total amounts for all flights
    """
    total_amounts = []
    for flight in flights['flights']:
        amount = 0
        for charge in flight['pricing']['service_charges']:
            if charge['charge_type'] == 'TotalAmount':
                amount += float(charge['price'])
        total_amounts.append(amount)

    return total_amounts


def calculate_flight_duration(flight_data):
    """
    Calculates the flight duration

    :param flight_data: dictionary that contain flight data
    :return: <class 'datetime.timedelta'>
    """
    departure_time = datetime.strptime(flight_data[0]['departure_time'], '%Y-%m-%dT%H%M')
    arrival_time = datetime.strptime(flight_data[-1]['arrival_time'], '%Y-%m-%dT%H%M')
    return arrival_time - departure_time


def get_durations(flights):
    """
    Calculates the duration of each flight

    :param flights: dictionary with 'flights' key that contain flight data
    :return: durations list that contain durations for all flights
    """
    durations = []
    for flight in flights['flights']:
        duration = calculate_flight_duration(flight['onward_itinerary'])
        if flights['return_tickets']:
            return_duration = calculate_flight_duration(flight['return_itinerary'])
            duration = duration + return_duration
        durations.append(duration)

    return durations


def get_by(key, flights, func):
    """
    Returns the most expensive/cheapest, longest/fastest flights

    :param key: <class 'str'> - 'duration' or 'price'
    If you need to find the longest/fastest itineraries, then choose 'duration'.
    If you need to find the most expensive/cheapest itineraries, then choose 'price'
    :param flights: dictionary with 'flights' key that contain flight data
    :param func: <class 'builtin_function_or_method'> - only min or max builtin functions
    If you need to find the fastest or cheapest itineraries --> min
    If you need to find the longest or most expensive --> max
    :return: dictionary with flights data
    """
    handlers = {'duration': get_durations, 'price': get_total_amounts}
    all_values = handlers[key](flights)
    flights['flights'] = [flights['flights'][idx] for idx, val in enumerate(all_values) if val == func(all_values)]
    return flights


def get_optimal(flights):
    """
    Finds the best flight option.
    First, the function finds all flights
    whose duration is less than the average duration of all flights on this itinerary.
    From this list, return flights with the lowest price.

    :param flights: dictionary with 'flights' key that contain flight data
    :return: dictionary with optimal flights
    """
    durations = get_durations(flights)
    average_time = sum([duration.total_seconds() for duration in durations]) / len(durations)
    flights['flights'] = [
        flight for idx, flight in enumerate(flights['flights']) if durations[idx].total_seconds() <= average_time
    ]
    return get_by('price', flights, min)


def check_and_set_params(source1, source2, dict_to_set, set_key):
    """
    Checks the equality of source1 and source2 and adds a key and value to the dictionary

    :param source1: any object
    :param source2: any object
    :param dict_to_set: dictionary to set data
    :param set_key: dictionary key
    """
    if source1 != source2:
        dict_to_set['first'][set_key] = source1
        dict_to_set['second'][set_key] = source2


def get_service_charges_types(service_charges):
    """
    Returns service charge types

    :param service_charges: list with dictionaries as objects that contain service charge data
    :return: <class 'set'> with service charge types for flight
    """
    return set(data['type'] for data in service_charges)


def get_difference(flights_data1, flights_data2):
    """
    Returns the difference between two flight data dictionaries.

    Checks only the most important data:
    - availability of the return itinerary
    - whether the departure dates match
    - checks whether the departure and arrival airports match
    - whether the types of passengers match

    :param flights_data1: dictionary with 'flights' key that contain flight data from the first file
    :param flights_data2: dictionary with 'flights' key that contain flight data from the second file
    :return: A dictionary that displays the difference between two flight dictionaries
    """
    difference = {'first': {}, 'second': {}}

    flights1 = flights_data1['flights'][0]['onward_itinerary']
    flights2 = flights_data2['flights'][0]['onward_itinerary']
    check_and_set_params(flights_data1['return_tickets'], flights_data2['return_tickets'], difference, 'return_itinerary')
    check_and_set_params(flights1[0]['source'], flights2[0]['source'], difference, 'source')
    check_and_set_params(flights1[-1]['destination'], flights2[-1]['destination'], difference, 'destination')

    departure_data1 = findall(r'(.+)T', flights1[0]['departure_time'])[0]
    departure_data2 = findall(r'(.+)T', flights2[0]['departure_time'])[0]
    check_and_set_params(departure_data1, departure_data2, difference, 'departure_date')

    pricing1 = flights_data1['flights'][0]['pricing']
    pricing2 = flights_data2['flights'][0]['pricing']
    check_and_set_params(pricing1['currency'], pricing2['currency'], difference, 'currency')

    type1 = sorted(list(get_service_charges_types(pricing1['service_charges'])))
    type2 = sorted(list(get_service_charges_types(pricing2['service_charges'])))
    check_and_set_params(type1, type2, difference, 'type')

    return difference


if __name__ == '__main__':
    soup = BeautifulSoup('', 'lxml')
    soup2 = BeautifulSoup('', features='xml')
    print(get_flight_data(soup))
    print(type(soup))
    print(type(soup2))
