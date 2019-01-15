"""
This file contains all the logic of working with flight data (computing, etc.)
"""

from datetime import datetime
from re import findall

from ticketsapi.handlers.exc_handler import exc_handler
from ticketsapi.handlers.flights_parser import from_xml_to_dict


def get_flights(xml_file_path):
    """
    Receives flight data

    :param xml_file_path: path where the XML file is located
    :return: dictionary with flights data
    """
    return from_xml_to_dict(xml_file_path)


@exc_handler
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


@exc_handler
def calculate_flight_duration(flight_data):
    """
    Calculates the flight duration

    :param flight_data: dictionary that contain flight data
    :return: <class 'datetime.timedelta'>
    """
    departure_time = datetime.strptime(flight_data[0]['departure_time'], '%Y-%m-%dT%H%M')
    arrival_time = datetime.strptime(flight_data[-1]['arrival_time'], '%Y-%m-%dT%H%M')
    return arrival_time - departure_time


@exc_handler
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


@exc_handler
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
    if func not in (max, min):
        raise TypeError('Parameter func must be only min or max builtin func')

    handlers = {'duration': get_durations, 'price': get_total_amounts}
    all_values = handlers[key](flights)
    flights['flights'] = [flights['flights'][idx] for idx, val in enumerate(all_values) if val == func(all_values)]
    return flights


@exc_handler
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


@exc_handler
def check_and_set_params(source1, source2, dict_to_set, set_key):
    """
    Checks the equality of source1 and source2 and adds a key and value to the dictionary

    :param source1: any object
    :param source2: any object
    :param dict_to_set: dictionary to set data
    :param set_key: dictionary key
    """
    if source1 != source2:
        dict_to_set['first'][str(set_key)] = source1
        dict_to_set['second'][str(set_key)] = source2


@exc_handler
def get_service_charges_types(service_charges):
    """
    Returns service charge types

    :param service_charges: list with dictionaries as objects that contain service charge data
    :return: <class 'set'> with service charge types for flight
    """
    return set(data['type'] for data in service_charges)


@exc_handler
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
