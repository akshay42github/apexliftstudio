"""
DRF API views for ApexLiftStudio.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import HttpResponse
import stripe
import json
from datetime import timedelta

from .models import (
    MembershipPlan, Location, Class, Booking, Membership, Payment
)
from .serializers import (
    UserSerializer, MembershipPlanSerializer, LocationSerializer,
    ClassSerializer, BookingSerializer, ProfileSerializer,
    MembershipSerializer, PaymentSerializer
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class MembershipPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for membership plans."""
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer
    permission_classes = [AllowAny]


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for gym locations."""
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]


class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for fitness classes."""
    serializer_class = ClassSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Class.objects.filter(
            is_active=True,
            start_time__gte=timezone.now()
        ).select_related('trainer', 'location')

        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(start_time__date=date)

        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location_id=location)

        return queryset.order_by('start_time')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def book(self, request, pk=None):
        """Book a class."""
        class_instance = self.get_object()

        # Check if already booked
        existing_booking = Booking.objects.filter(
            user=request.user,
            class_instance=class_instance
        ).first()

        if existing_booking:
            if existing_booking.status == 'confirmed':
                return Response(
                    {'error': 'You have already booked this class.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Reactivate cancelled booking
                existing_booking.status = 'confirmed'
                existing_booking.save()
                serializer = BookingSerializer(existing_booking)
                return Response(serializer.data)

        # Check capacity
        if class_instance.is_full:
            return Response(
                {'error': 'This class is fully booked.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            class_instance=class_instance,
            status='confirmed'
        )

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """User registration API endpoint."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login API endpoint."""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })

    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """Get authenticated user's profile."""
    profile_serializer = ProfileSerializer(request.user.profile)

    # Get active membership
    active_membership = Membership.objects.filter(
        user=request.user,
        status='active'
    ).select_related('plan').first()

    membership_data = None
    if active_membership:
        membership_data = MembershipSerializer(active_membership).data

    return Response({
        'profile': profile_serializer.data,
        'membership': membership_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create Stripe checkout session for membership purchase."""
    plan_id = request.data.get('plan_id')
    billing_cycle = request.data.get('billing_cycle', 'monthly')  # monthly or yearly

    try:
        plan = MembershipPlan.objects.get(id=plan_id, is_active=True)
    except MembershipPlan.DoesNotExist:
        return Response(
            {'error': 'Invalid plan ID'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Determine price
    if billing_cycle == 'yearly':
        price = plan.price_yearly
        price_id = plan.stripe_price_id_yearly
    else:
        price = plan.price_monthly
        price_id = plan.stripe_price_id_monthly

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': int(price * 100),  # Convert to cents
                    'product_data': {
                        'name': f'{plan.name} Membership',
                        'description': f'{billing_cycle.capitalize()} membership for {plan.name}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/dashboard/') + '?checkout=success',
            cancel_url=request.build_absolute_uri('/plans/') + '?checkout=cancelled',
            client_reference_id=request.user.id,
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
                'billing_cycle': billing_cycle,
            }
        )

        return Response({
            'session_id': checkout_session.id,
            'session_url': checkout_session.url
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)

    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failed(payment_intent)

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle successful checkout session."""
    user_id = session['metadata'].get('user_id')
    plan_id = session['metadata'].get('plan_id')
    billing_cycle = session['metadata'].get('billing_cycle', 'monthly')

    if not user_id or not plan_id:
        return

    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        plan = MembershipPlan.objects.get(id=plan_id)

        # Calculate membership dates
        start_date = timezone.now().date()
        if billing_cycle == 'yearly':
            end_date = start_date + timedelta(days=365)
            amount = plan.price_yearly
        else:
            end_date = start_date + timedelta(days=30)
            amount = plan.price_monthly

        # Create or update membership
        membership, created = Membership.objects.update_or_create(
            user=user,
            plan=plan,
            status='active',
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'stripe_subscription_id': session.get('subscription', ''),
            }
        )

        # Create payment record
        Payment.objects.create(
            user=user,
            membership=membership,
            amount=amount,
            currency='inr',
            stripe_payment_intent_id=session.get('payment_intent', ''),
            status='succeeded',
            payment_method='card',
            description=f'{plan.name} - {billing_cycle} membership'
        )

    except Exception as e:
        print(f"Error handling checkout session: {e}")


def handle_payment_intent_succeeded(payment_intent):
    """Handle successful payment intent."""
    # Additional payment processing logic if needed
    pass


def handle_payment_failed(payment_intent):
    """Handle failed payment."""
    # Log or notify about failed payment
    pass