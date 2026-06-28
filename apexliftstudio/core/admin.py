"""
Django admin customization for ApexLiftStudio.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile, MembershipPlan, Membership, Trainer, Location,
    Class, Booking, BlogPost, Testimonial, Payment, ContactMessage
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['created_at']
    raw_id_fields = ['user']


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly', 'price_yearly', 'is_active', 'display_order']
    list_editable = ['is_active', 'display_order']
    search_fields = ['name', 'description']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew']
    list_filter = ['status', 'plan', 'auto_renew', 'start_date']
    search_fields = ['user__username', 'user__email', 'stripe_subscription_id']
    raw_id_fields = ['user']
    date_hierarchy = 'start_date'


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'years_experience', 'is_active', 'created_at']
    list_filter = ['is_active', 'years_experience']
    search_fields = ['name', 'bio', 'specialties']
    prepopulated_fields = {'slug': ('name',)}

    def get_photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return '-'

    get_photo_preview.short_description = 'Photo'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'phone', 'is_active']
    list_filter = ['is_active', 'state', 'city']
    search_fields = ['name', 'address', 'city']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'location', 'start_time', 'capacity', 'available_spots', 'is_active']
    list_filter = ['is_active', 'difficulty_level', 'location', 'trainer', 'start_time']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_time'
    raw_id_fields = ['trainer', 'location']

    def available_spots(self, obj):
        return obj.available_spots

    available_spots.short_description = 'Available Spots'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'class_instance', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'class_instance__location']
    search_fields = ['user__username', 'class_instance__title']
    raw_id_fields = ['user', 'class_instance']
    date_hierarchy = 'created_at'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'published_at', 'views_count']
    list_filter = ['is_published', 'published_at', 'created_at']
    search_fields = ['title', 'body', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'rating', 'is_visible', 'featured', 'created_at']
    list_filter = ['rating', 'is_visible', 'featured', 'created_at']
    search_fields = ['user_name', 'content']
    list_editable = ['is_visible', 'featured']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['user__username', 'stripe_payment_intent_id', 'stripe_charge_id']
    raw_id_fields = ['user', 'membership']
    date_hierarchy = 'created_at'
    readonly_fields = ['stripe_payment_intent_id', 'stripe_charge_id']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'replied', 'created_at']
    list_filter = ['is_read', 'replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read', 'replied']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']