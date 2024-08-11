from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Location
from django.contrib.postgres.search import TrigramSimilarity
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

            start_location = Location.objects.annotate(
                similarity=TrigramSimilarity('formatted_address', start_address)
            ).filter(
                similarity__gt=0.3
            ).order_by('-similarity').first()


            if not start_location:
                start_location = self.fetch_and_save_location(start_address, google_api_key)
                if not start_location:
                    return Response({'error': 'No results found for start address'}, status=status.HTTP_404_NOT_FOUND)
            

            destination_location = Location.objects.annotate(
                similarity=TrigramSimilarity('formatted_address', destination_address)
            ).filter(
                similarity__gt=0.3
            ).order_by('-similarity').first()


            if not destination_location:
                destination_location = self.fetch_and_save_location(destination_address, google_api_key)
                if not destination_location:
                    return Response({'error': 'No results found for destination address'}, status=status.HTTP_404_NOT_FOUND)


            # Calculate the distance
            distance = self.calculate_distance(
                start_location.latitude, start_location.longitude,
                destination_location.latitude, destination_location.longitude
            )

            return Response({'distance': distance}, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def fetch_and_save_location(self, address, google_api_key):
        """Fetch location from Google API and save it to the database."""
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data['results']:
            return None

        location_data = data['results'][0]
        location = Location.objects.create(
            address=address,
            latitude=location_data['geometry']['location']['lat'],
            longitude=location_data['geometry']['location']['lng'],
            formatted_address=location_data['formatted_address']
        )
        return location

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Radius of the Earth in km
        
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
