from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from ticketsapi.flights_handler import get_flights, get_by, get_optimal, get_difference


class FlightsView(APIView):
    def get(self, request, url):
        return_flights = request.GET.get('return', '1')

        if return_flights == '0':
            result = get_flights('ticketsapi/xml_files/RS_ViaOW.xml')
        elif return_flights == '1':
            result = get_flights('ticketsapi/xml_files/RS_Via-3.xml')
        else:
            return JsonResponse({'error': 'Bad Request (400)'}, status=status.HTTP_400_BAD_REQUEST)

        if url == 'getAll':
            pass
        elif url == 'getMostExpensive':
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


class DifferenceView(APIView):
    def get(self, request):
        response1 = get_flights('ticketsapi/xml_files/RS_ViaOW.xml')
        response2 = get_flights('ticketsapi/xml_files/RS_Via-3.xml')
        result = get_difference(response1, response2)
        return JsonResponse({'response': result}, status=status.HTTP_200_OK)
