from django.test import TestCase, Client
from django.urls import reverse


class HealthCheckTest(TestCase):
    """Test the health check endpoint"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check(self):
        """Test health check endpoint returns 200"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
