from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
import requests

class CalculateDistanceViewTests(TestCase):

    def setUp(self):
        self.client = Client()

    def mock_geocode_response(self, address, formatted_address, latitude, longitude):
        return {
            'results': [{
                'formatted_address': formatted_address,
                'geometry': {
                    'location': {
                        'lat': latitude,
                        'lng': longitude
                    }
                }
            }],
            'status': 'OK'
        }

    def mock_requests_get(self, url, *args, **kwargs):
        if 'Nonexistent' in url:
            return self.MockResponse({'results': [], 'status': 'ZERO_RESULTS'}, status_code=200)
        if 'start_address' in url:
            return self.MockResponse(self.mock_geocode_response(
                'start_address', 'Start Address Formatted', 34.052235, -118.243683))
        elif 'destination_address' in url:
            return self.MockResponse(self.mock_geocode_response(
                'destination_address', 'Destination Address Formatted', 36.778259, -119.417931))
        return self.MockResponse({'results': [], 'status': 'ZERO_RESULTS'}, status_code=200)

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code != 200:
                raise requests.RequestException(f"Mock error: {self.status_code}")

    def test_calculate_distance_view_get(self):
        response = self.client.get(reverse('calculate_distance'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('requests.get')
    def test_calculate_distance_view_post_success(self, mock_get):
        mock_get.side_effect = self.mock_requests_get

        data = {
            'start_address': 'start_address',
            'destination_address': 'destination_address'
        }
        response = self.client.post(reverse('calculate_distance'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('distance', response.json())
        self.assertGreater(response.json()['distance'], 0)

    @patch('requests.get')
    def test_calculate_distance_view_post_no_results(self, mock_get):
        mock_get.side_effect = self.mock_requests_get

        data = {
            'start_address': 'Nonexistent Start Address',
            'destination_address': 'Nonexistent Destination Address'
        }
        response = self.client.post(reverse('calculate_distance'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'No results found for start address')
