"""
Unit tests for ApexLiftStudio.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from datetime import timedelta
from decimal import Decimal

from .models import (
    MembershipPlan, Membership, Trainer, Location, Class, Booking, Payment
)


class MembershipPlanModelTest(TestCase):
    """Test MembershipPlan model."""

    def setUp(self):
        self.plan = MembershipPlan.objects.create(
            name='Basic Plan',
            slug='basic-plan',
            description='Basic membership',
            price_monthly=Decimal('29.99'),
            price_yearly=Decimal('299.99'),
            features=['Access to gym', 'Locker'],
            is_active=True
        )

    def test_plan_creation(self):
        """Test plan is created correctly."""
        self.assertEqual(self.plan.name, 'Basic Plan')
        self.assertEqual(self.plan.price_monthly, Decimal('29.99'))
        self.assertTrue(self.plan.is_active)

    def test_plan_string_representation(self):
        """Test plan string representation."""
        self.assertEqual(str(self.plan), 'Basic Plan')

    def test_slug_auto_generation(self):
        """Test slug is auto-generated."""
        plan = MembershipPlan.objects.create(
            name='Premium Plan',
            description='Premium membership',
            price_monthly=Decimal('59.99'),
            price_yearly=Decimal('599.99'),
        )
        self.assertEqual(plan.slug, 'premium-plan')


class MembershipModelTest(TestCase):
    """Test Membership model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.plan = MembershipPlan.objects.create(
            name='Test Plan',
            slug='test-plan',
            description='Test',
            price_monthly=Decimal('39.99'),
            price_yearly=Decimal('399.99'),
        )
        self.membership = Membership.objects.create(
            user=self.user,
            plan=self.plan,
            status='active',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )

    def test_membership_creation(self):
        """Test membership is created correctly."""
        self.assertEqual(self.membership.user, self.user)
        self.assertEqual(self.membership.plan, self.plan)
        self.assertEqual(self.membership.status, 'active')

    def test_membership_is_active(self):
        """Test is_active property."""
        self.assertTrue(self.membership.is_active)

        # Test expired membership
        self.membership.end_date = timezone.now().date() - timedelta(days=1)
        self.membership.save()
        self.assertFalse(self.membership.is_active)


class ViewTests(TestCase):
    """Test template views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_home_view(self):
        """Test home page loads."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_plans_view(self):
        """Test plans page loads."""
        response = self.client.get(reverse('plans'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans.html')

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class APITests(APITestCase):
    """Test API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.plan = MembershipPlan.objects.create(
            name='API Test Plan',
            slug='api-test-plan',
            description='Test plan',
            price_monthly=Decimal('49.99'),
            price_yearly=Decimal('499.99'),
            is_active=True
        )

    def test_plans_list_api(self):
        """Test plans API endpoint."""
        response = self.client.get('/api/plans/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_signup_api(self):
        """Test user registration API."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post('/api/signup/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

    def test_login_api(self):
        """Test login API endpoint."""
        data = {
            'username': 'apiuser',
            'password': 'apipass123'
        }
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_authenticated_api_access(self):
        """Test authenticated API access."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['profile']['username'], 'apiuser')


class ClassBookingTest(TestCase):
    """Test class booking functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='bookinguser',
            password='bookpass123'
        )
        self.trainer = Trainer.objects.create(
            name='John Trainer',
            slug='john-trainer',
            bio='Experienced trainer',
            specialties='Yoga, Pilates'
        )
        self.location = Location.objects.create(
            name='Main Branch',
            slug='main-branch',
            address='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            latitude=40.7128,
            longitude=-74.0060,
            phone='555-1234',
            hours='6AM-10PM'
        )
        self.class_instance = Class.objects.create(
            title='Morning Yoga',
            slug='morning-yoga-test',
            description='Relaxing yoga class',
            trainer=self.trainer,
            location=self.location,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            capacity=10
        )

    def test_class_booking(self):
        """Test booking a class."""
        booking = Booking.objects.create(
            user=self.user,
            class_instance=self.class_instance,
            status='confirmed'
        )
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(self.class_instance.available_spots, 9)

    def test_class_full_capacity(self):
        """Test class at full capacity."""
        # Book all spots
        for i in range(10):
            user = User.objects.create_user(username=f'user{i}', password='pass')
            Booking.objects.create(
                user=user,
                class_instance=self.class_instance,
                status='confirmed'
            )

        self.assertTrue(self.class_instance.is_full)
        self.assertEqual(self.class_instance.available_spots, 0)