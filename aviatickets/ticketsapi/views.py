from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from ticketsapi.xml_parser import main


class FlightsView(APIView):
    def get(self, request):
        return_flights = request.GET.get('return', '1')
        if return_flights == '0':
            result = main('ticketsapi/xml_files/RS_ViaOW.xml')
        elif return_flights == '1':
            result = main('ticketsapi/xml_files/RS_Via-3.xml')
        else:
            return JsonResponse({'error': 'Bad Request (400)'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'response': result}, status=status.HTTP_200_OK)
