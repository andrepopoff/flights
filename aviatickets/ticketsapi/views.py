from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from os.path import join
# from rest_framework.response import Response

from ticketsapi.flights_handler import get_flights, get_by, get_optimal, get_difference


@api_view(['GET'])
def flights_view(request, url):
    return_flights = request.GET.get('return', '1')

    if return_flights == '0':
        result = get_flights(join('ticketsapi', 'xml_files', 'RS_ViaOW.xml'))
    elif return_flights == '1':
        result = get_flights(join('ticketsapi', 'xml_files', 'RS_Via-3.xml'))
    else:
        return JsonResponse({'error': 'Bad Request (400)'}, status=status.HTTP_400_BAD_REQUEST)

    if url == 'getMostExpensive':
        result = get_by('price', result, max)
    elif url == 'getCheapest':
        result = get_by('price', result, min)
    elif url == 'getLongest':
        result = get_by('duration', result, max)
    elif url == 'getFastest':
        result = get_by('duration', result, min)
    elif url == 'getOptimal':
        result = get_optimal(result)

    return JsonResponse({'response': result}, status=status.HTTP_200_OK)


@api_view(['GET'])
def flights_difference_view(request):
    request1 = get_flights(join('ticketsapi', 'xml_files', 'RS_ViaOW.xml'))
    request2 = get_flights(join('ticketsapi', 'xml_files', 'RS_Via-3.xml'))
    result = get_difference(request1, request2)
    return JsonResponse({'response': result}, status=status.HTTP_200_OK)

