"""
DRF serializers for ApexLiftStudio API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    MembershipPlan, Location, Class, Trainer, Booking,
    Profile, Membership, Payment
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and profile."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'},
                                      label='Confirm Password')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Create profile
        Profile.objects.create(user=user)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'avatar', 'date_of_birth']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class MembershipPlanSerializer(serializers.ModelSerializer):
    """Membership plan serializer."""
    features_list = serializers.SerializerMethodField()

    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'slug', 'description', 'price_monthly', 'price_yearly',
                  'features', 'features_list', 'is_active']

    def get_features_list(self, obj):
        return obj.get_features_list()


class LocationSerializer(serializers.ModelSerializer):
    """Location serializer."""

    class Meta:
        model = Location
        fields = ['id', 'name', 'slug', 'address', 'city', 'state', 'postal_code',
                  'latitude', 'longitude', 'phone', 'hours', 'amenities']


class TrainerSerializer(serializers.ModelSerializer):
    """Trainer serializer."""
    specialties_list = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = ['id', 'name', 'slug', 'bio', 'photo', 'specialties', 'specialties_list',
                  'years_experience', 'certifications']

    def get_specialties_list(self, obj):
        return obj.get_specialties_list()


class ClassSerializer(serializers.ModelSerializer):
    """Class serializer."""
    trainer = TrainerSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'title', 'slug', 'description', 'trainer', 'location',
                  'start_time', 'end_time', 'capacity', 'available_spots', 'is_full',
                  'difficulty_level']


class BookingSerializer(serializers.ModelSerializer):
    """Booking serializer."""
    class_instance = ClassSerializer(read_only=True)
    class_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'class_instance', 'class_id', 'status', 'notes', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate_class_id(self, value):
        try:
            class_instance = Class.objects.get(id=value, is_active=True)
            if class_instance.is_full:
                raise serializers.ValidationError("This class is fully booked.")
        except Class.DoesNotExist:
            raise serializers.ValidationError("Invalid class ID.")
        return value

    def create(self, validated_data):
        class_id = validated_data.pop('class_id')
        class_instance = Class.objects.get(id=class_id)
        validated_data['class_instance'] = class_instance
        return super().create(validated_data)


class MembershipSerializer(serializers.ModelSerializer):
    """Membership serializer."""
    plan = MembershipPlanSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'is_active']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer."""

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'status', 'payment_method', 'description', 'created_at']