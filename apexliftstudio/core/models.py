"""
Core models for ApexLiftStudio gym management system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
import json


class Profile(models.Model):
    """Extended user profile with additional fields."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class MembershipPlan(models.Model):
    """Membership plans with pricing and features."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    features = models.JSONField(default=list, help_text="List of features as JSON array")
    is_active = models.BooleanField(default=True)
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'price_monthly']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_features_list(self):
        """Return features as a list."""
        if isinstance(self.features, str):
            return json.loads(self.features)
        return self.features


class Membership(models.Model):
    """User membership with plan and status."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and self.end_date >= timezone.now().date()


class Trainer(models.Model):
    """Gym trainers with bio and specialties."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    bio = models.TextField()
    photo = models.ImageField(upload_to='trainers/', null=True, blank=True)
    specialties = models.CharField(max_length=300, help_text="Comma-separated specialties")
    years_experience = models.IntegerField(default=0)
    certifications = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_specialties_list(self):
        return [s.strip() for s in self.specialties.split(',') if s.strip()]


class Location(models.Model):
    """Gym branch locations."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    hours = models.TextField(help_text="Operating hours, e.g., 'Mon-Fri: 6AM-10PM'")
    amenities = models.TextField(blank=True, help_text="Comma-separated amenities")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Class(models.Model):
    """Fitness classes with schedule."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name='classes')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='classes')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        default='beginner'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{self.start_time.strftime('%Y%m%d%H%M')}"
        super().save(*args, **kwargs)

    @property
    def available_spots(self):
        return self.capacity - self.bookings.filter(status='confirmed').count()

    @property
    def is_full(self):
        return self.available_spots <= 0


class Booking(models.Model):
    """Class bookings by users."""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'class_instance']

    def __str__(self):
        return f"{self.user.username} - {self.class_instance.title} ({self.status})"


class BlogPost(models.Model):
    """Blog posts for gym content."""
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    body = models.TextField(help_text="Supports Markdown")
    excerpt = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Testimonial(models.Model):
    """User testimonials."""
    user_name = models.CharField(max_length=200)
    user_photo = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} - {self.rating} stars"


class Payment(models.Model):
    """Payment records for memberships."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='card')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} ({self.status})"


class ContactMessage(models.Model):
    """Contact form submissions."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"