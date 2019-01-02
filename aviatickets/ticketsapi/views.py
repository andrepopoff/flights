from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ticketsapi.xml_parser import main


class FlightsView(APIView):
    def get(self, request):
        result = main('ticketsapi/xml_files/RS_Via-3.xml')
        response = Response(result, status=status.HTTP_200_OK)
        return response
