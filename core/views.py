"""
Template views for ApexLiftStudio.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import (
    MembershipPlan, Trainer, Location, Class, BlogPost,
    Testimonial, Membership, Booking, Payment
)
from .forms import UserRegistrationForm, UserLoginForm, ContactForm


def home(request):
    """Homepage with hero and highlights."""
    plans = MembershipPlan.objects.filter(is_active=True)[:3]
    testimonials = Testimonial.objects.filter(is_visible=True, featured=True)[:4]
    upcoming_classes = Class.objects.filter(
        is_active=True,
        start_time__gte=timezone.now()
    ).select_related('trainer', 'location')[:6]

    context = {
        'plans': plans,
        'testimonials': testimonials,
        'upcoming_classes': upcoming_classes,
    }
    return render(request, 'home.html', context)


def plans_view(request):
    """Membership plans page."""
    plans = MembershipPlan.objects.filter(is_active=True).order_by('display_order', 'price_monthly')
    context = {'plans': plans}
    return render(request, 'plans.html', context)


def about_view(request):
    """About page with mission and trainers."""
    trainers = Trainer.objects.filter(is_active=True)
    context = {'trainers': trainers}
    return render(request, 'about.html', context)


def locations_view(request):
    """Locations page with Google Maps."""
    locations = Location.objects.filter(is_active=True)
    context = {'locations': locations}
    return render(request, 'locations.html', context)


def classes_view(request):
    """Class schedule page."""
    classes = Class.objects.filter(
        is_active=True,
        start_time__gte=timezone.now()
    ).select_related('trainer', 'location').order_by('start_time')

    # Filter by location if provided
    location_id = request.GET.get('location')
    if location_id:
        classes = classes.filter(location_id=location_id)

    # Filter by date if provided
    date = request.GET.get('date')
    if date:
        classes = classes.filter(start_time__date=date)

    locations = Location.objects.filter(is_active=True)
    context = {
        'classes': classes,
        'locations': locations,
    }
    return render(request, 'classes.html', context)


def blog_list(request):
    """Blog list page."""
    posts = BlogPost.objects.filter(is_published=True).select_related('author').order_by('-published_at')

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(body__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    context = {'posts': posts, 'search_query': search_query}
    return render(request, 'blog_list.html', context)


def blog_detail(request, slug):
    """Individual blog post page."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])

    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id).order_by('-published_at')[:3]

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog_detail.html', context)


def contact_view(request):
    """Contact form page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            if request.user.is_authenticated:
                contact_message.user = request.user
            contact_message.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = ContactForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'contact.html', context)


def register_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'auth/register.html', context)


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = UserLoginForm()

    context = {'form': form}
    return render(request, 'auth/login.html', context)


def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    """User dashboard."""
    # Get active membership
    active_membership = Membership.objects.filter(
        user=request.user,
        status='active'
    ).select_related('plan').first()

    # Get upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        status='confirmed',
        class_instance__start_time__gte=timezone.now()
    ).select_related('class_instance', 'class_instance__trainer', 'class_instance__location').order_by('class_instance__start_time')[:5]

    # Get payment history
    payments = Payment.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    context = {
        'active_membership': active_membership,
        'upcoming_bookings': upcoming_bookings,
        'payments': payments,
    }
    return render(request, 'dashboard.html', context)