from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from ticketsapi.flights_handler import get_flights, get_at_extreme_prices


class FlightsView(APIView):
    def get(self, request):
        return_flights = request.GET.get('return', '1')
        flight_type = request.GET.get('type', 'all')

        if return_flights == '0':
            result = get_flights('ticketsapi/xml_files/RS_ViaOW.xml')
        elif return_flights == '1':
            result = get_flights('ticketsapi/xml_files/RS_Via-3.xml')
        else:
            return JsonResponse({'error': 'Bad Request (400)'}, status=status.HTTP_400_BAD_REQUEST)

        if flight_type == 'all':
            pass
        elif flight_type == 'expensive':
            result = get_at_extreme_prices(result, max)
        elif flight_type == 'cheap':
            result = get_at_extreme_prices(result, min)
        else:
            return JsonResponse({'error': 'Bad Request (400)'}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'response': result}, status=status.HTTP_200_OK)
