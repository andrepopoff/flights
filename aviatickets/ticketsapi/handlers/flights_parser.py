"""
This file contains everything related to data parsing.
"""
from lxml import etree
from ticketsapi.handlers.exc_handler import exc_handler


def get_tickets_type(flights_tags):
    """
    Find out the presence of return itineraries

    :param flights_tags: <class 'lxml.etree._ElementTree'> with XML data
    :return: <class 'int'> - returns 1 if there are return itineraries.
    If not, it returns 0
    """
    try:
        return 1 if flights_tags[0].find('ReturnPricedItinerary') is not None else 0
    except TypeError as error:
        print('In func {}: {} {}'.format(get_tickets_type.__name__, error.__class__, error))
        return 0


@exc_handler
def get_flight_data(flight_tag):
    """
    Parsing flight data from xml tags

    :param flight_tag: <class 'lxml.etree._Element'> with flight data
    :return: dictionary with flight data
    """
    return {
        'carrier_id': flight_tag.find('Carrier').attrib['id'],
        'carrier_name': flight_tag.find('Carrier').text,
        'flight_number': flight_tag.find('FlightNumber').text,
        'source': flight_tag.find('Source').text,
        'destination': flight_tag.find('Destination').text,
        'departure_time': flight_tag.find('DepartureTimeStamp').text,
        'arrival_time': flight_tag.find('ArrivalTimeStamp').text,
        'class': flight_tag.find('Class').text,
        'number_of_stops': flight_tag.find('NumberOfStops').text,
        'fare_basis': flight_tag.find('FareBasis').text.strip(),
        'warning_text': flight_tag.find('WarningText').text,
        'ticket_type': flight_tag.find('TicketType').text
    }


@exc_handler
def add_flight_data_to_dict(tag, itinerary_type, data, flight_number, set_key):
    """
    Adds flight data to the dictionary

    :param tag: <class 'lxml.etree._Element'> with flight data
    :param itinerary_type: <class 'str'> - 'OnwardPricedItinerary' or 'ReturnPricedItinerary'
    :param data: dictionary with 'flights' key that contain flight data
    :param flight_number: <class 'int'> - flight order in data['flights'] list
    :param set_key: <class 'str'> - key to set data['flights'][flight_number][set_key]
    """
    flight_tags = tag.find(itinerary_type).find('Flights').findall('Flight')
    [data['flights'][flight_number][set_key].append(get_flight_data(flight_tag)) for flight_tag in flight_tags]


@exc_handler
def add_service_charges(service_charges_tags, data):
    """
    Adds service charges data to the dictionary

    :param service_charges_tags: the list contains objects of class 'lxml.etree._Element'
    :param data: list to add service charges data
    """
    for i, charge in enumerate(service_charges_tags):
        data.append({})
        type_ = data[i]['type'] = charge.attrib['type']
        charge_type = data[i]['charge_type'] = charge.attrib['ChargeType']
        price = data[i]['price'] = charge.text

        if not type_ or not charge_type or not price:
            raise Exception('One of the parameters was not found. Wrong data in service_charges_tags')


@exc_handler
def from_xml_to_dict(xml_file_path):
    """
    From XML data to the dictionary

    :param xml_file_path: string with path to XML file
    :return: dictionary with flights data
    """
    doc = etree.parse(xml_file_path)
    flights_tags = doc.find('PricedItineraries').findall('Flights')
    data = dict()

    flights = data['flights'] = []
    data['return_tickets'] = get_tickets_type(flights_tags)
    data['request_time'] = doc.getroot().attrib['RequestTime']
    data['response_time'] = doc.getroot().attrib['ResponseTime']
    data['request_id'] = doc.find('RequestId').text

    for num, tag in enumerate(flights_tags):
        flights.append({'onward_itinerary': []})
        add_flight_data_to_dict(tag, 'OnwardPricedItinerary', data, num, 'onward_itinerary')

        if data['return_tickets']:
            flights[num]['return_itinerary'] = []
            add_flight_data_to_dict(tag, 'ReturnPricedItinerary', data, num, 'return_itinerary')

        pricing = flights[num]['pricing'] = {'currency': tag.find('Pricing').attrib['currency']}
        pricing['service_charges'] = []

        service_charges = tag.find('Pricing').findall('ServiceCharges')
        add_service_charges(service_charges, pricing['service_charges'])

    return data
