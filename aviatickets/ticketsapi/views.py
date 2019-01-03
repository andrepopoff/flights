from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from ticketsapi.xml_parser import main


class FlightsView(APIView):
    def get(self, request):
        result = main('ticketsapi/xml_files/RS_Via-3.xml')
        return JsonResponse({'response': result}, status=status.HTTP_200_OK)
