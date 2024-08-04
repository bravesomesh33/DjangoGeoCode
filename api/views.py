from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Location
import requests
import math

class CalculateDistanceView(APIView):

    def post(self, request):
        start_address = request.data.get('start_address')
        destination_address = request.data.get('destination_address')

        if not start_address or not destination_address:
            return Response({'error': 'Both start and destination addresses are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            google_api_key = settings.GOOGLE_API_KEY

            # Get the geocode data for start_address
            start_location = Location.objects.filter(address=start_address).first()

            if not start_location:
                start_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={start_address}&key={google_api_key}'
                start_response = requests.get(start_url)
                start_response.raise_for_status()
                start_data = start_response.json()

                if not start_data['results']:
                    return Response({'error': 'No results found for start address'}, status=status.HTTP_404_NOT_FOUND)

                start_location_data = start_data['results'][0]
                start_latitude = start_location_data['geometry']['location']['lat']
                start_longitude = start_location_data['geometry']['location']['lng']
                start_location = Location.objects.create(
                    address=start_address,
                    latitude=start_latitude,
                    longitude=start_longitude,
                    formatted_address=start_location_data['formatted_address']
                )
            else:
                start_latitude = start_location.latitude
                start_longitude = start_location.longitude

            # Get the geocode data for destination_address
            destination_location = Location.objects.filter(address=destination_address).first()
            if not destination_location:
                destination_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={destination_address}&key={google_api_key}'
                destination_response = requests.get(destination_url)
                destination_response.raise_for_status()
                destination_data = destination_response.json()

                if not destination_data['results']:
                    return Response({'error': 'No results found for destination address'}, status=status.HTTP_404_NOT_FOUND)

                destination_location_data = destination_data['results'][0]
                destination_latitude = destination_location_data['geometry']['location']['lat']
                destination_longitude = destination_location_data['geometry']['location']['lng']
                destination_location = Location.objects.create(
                    address=destination_address,
                    latitude=destination_latitude,
                    longitude=destination_longitude,
                    formatted_address=destination_location_data['formatted_address']
                )
            else:
                destination_latitude = destination_location.latitude
                destination_longitude = destination_location.longitude

            # Calculate the distance
            distance = self.calculate_distance(start_latitude, start_longitude, destination_latitude, destination_longitude)

            return Response({'distance': distance}, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Radius of the Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
