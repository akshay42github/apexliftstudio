"""
Management command to seed demo data for ApexLiftStudio.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from core.models import (
    Profile, MembershipPlan, Membership, Trainer, Location,
    Class, Booking, BlogPost, Testimonial, Payment
)


class Command(BaseCommand):
    help = 'Seeds database with demo data for ApexLiftStudio'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')

        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@apexlift.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            Profile.objects.create(user=admin, phone='555-0000')
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin / admin123'))

        # Create test member user
        member, created = User.objects.get_or_create(
            username='johndoe',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created:
            member.set_password('testpass123')
            member.save()
            Profile.objects.create(user=member, phone='555-1111')
            self.stdout.write(self.style.SUCCESS(f'Created member user: johndoe / testpass123'))

        # Create membership plans
        plans_data = [
            {
                'name': 'Basic',
                'slug': 'basic',
                'description': 'Perfect for getting started with your fitness journey',
                'price_monthly': Decimal('29.99'),
                'price_yearly': Decimal('299.99'),
                'features': [
                    'Access to gym equipment',
                    'Locker rental',
                    'Free fitness assessment',
                    'Mobile app access'
                ],
                'display_order': 1
            },
            {
                'name': 'Plus',
                'slug': 'plus',
                'description': 'Enhanced experience with group classes included',
                'price_monthly': Decimal('49.99'),
                'price_yearly': Decimal('499.99'),
                'features': [
                    'All Basic features',
                    'Unlimited group classes',
                    'Sauna and steam room access',
                    'Guest privileges (2x/month)',
                    'Nutritional guidance'
                ],
                'display_order': 2
            },
            {
                'name': 'Premium',
                'slug': 'premium',
                'description': 'Ultimate fitness experience with personal training',
                'price_monthly': Decimal('89.99'),
                'price_yearly': Decimal('899.99'),
                'features': [
                    'All Plus features',
                    '4 personal training sessions/month',
                    'Priority class booking',
                    'Unlimited guest privileges',
                    'Massage therapy (1x/month)',
                    'Private locker',
                    'Towel service'
                ],
                'display_order': 3
            }
        ]

        for plan_data in plans_data:
            plan, created = MembershipPlan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created plan: {plan.name}')

        # Create trainers
        trainers_data = [
            {
                'name': 'Sarah Johnson',
                'slug': 'sarah-johnson',
                'bio': 'Certified personal trainer with 10+ years of experience specializing in strength training and nutrition.',
                'specialties': 'Strength Training, Nutrition, Weight Loss',
                'years_experience': 10,
                'certifications': 'NASM-CPT, Precision Nutrition Level 1',
                'email': 'sarah@apexlift.com',
                'phone': '555-2001'
            },
            {
                'name': 'Mike Chen',
                'slug': 'mike-chen',
                'bio': 'Former collegiate athlete turned fitness coach, passionate about functional training and sports performance.',
                'specialties': 'Functional Training, Sports Performance, HIIT',
                'years_experience': 8,
                'certifications': 'CSCS, TRX Certified',
                'email': 'mike@apexlift.com',
                'phone': '555-2002'
            },
            {
                'name': 'Emily Rodriguez',
                'slug': 'emily-rodriguez',
                'bio': 'Yoga and Pilates instructor dedicated to mind-body wellness and flexibility training.',
                'specialties': 'Yoga, Pilates, Flexibility, Mindfulness',
                'years_experience': 12,
                'certifications': 'RYT-500, Pilates Mat Certification',
                'email': 'emily@apexlift.com',
                'phone': '555-2003'
            }
        ]

        trainers = []
        for trainer_data in trainers_data:
            trainer, created = Trainer.objects.get_or_create(
                slug=trainer_data['slug'],
                defaults=trainer_data
            )
            trainers.append(trainer)
            if created:
                self.stdout.write(f'Created trainer: {trainer.name}')

        # Create locations
        locations_data = [
            {
                'name': 'Downtown Branch',
                'slug': 'downtown',
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'phone': '555-1001',
                'email': 'downtown@apexlift.com',
                'hours': 'Mon-Fri: 5AM-11PM, Sat-Sun: 7AM-9PM',
                'amenities': 'Pool, Sauna, Steam Room, Cafe, Childcare'
            },
            {
                'name': 'Westside Branch',
                'slug': 'westside',
                'address': '456 West Avenue',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10025',
                'latitude': 40.7829,
                'longitude': -73.9654,
                'phone': '555-1002',
                'email': 'westside@apexlift.com',
                'hours': 'Mon-Fri: 6AM-10PM, Sat-Sun: 8AM-8PM',
                'amenities': 'Sauna, Basketball Court, Yoga Studio'
            }
        ]

        locations = []
        for location_data in locations_data:
            location, created = Location.objects.get_or_create(
                slug=location_data['slug'],
                defaults=location_data
            )
            locations.append(location)
            if created:
                self.stdout.write(f'Created location: {location.name}')

        # Create classes
        class_types = [
            ('Morning Yoga', 'Start your day with energizing yoga flows', 'beginner', trainers[2]),
            ('HIIT Bootcamp', 'High-intensity interval training for maximum results', 'advanced', trainers[1]),
            ('Strength & Conditioning', 'Build muscle and increase strength', 'intermediate', trainers[0]),
            ('Evening Pilates', 'Core-focused Pilates for flexibility', 'beginner', trainers[2]),
            ('Spin Class', 'Energetic cycling workout with great music', 'intermediate', trainers[1]),
        ]

        classes_created = 0
        for i in range(7):  # Create classes for next 7 days
            date = timezone.now() + timedelta(days=i)
            for class_name, desc, level, trainer in class_types:
                hour = random.choice([6, 9, 12, 17, 19])
                start = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                end = start + timedelta(hours=1)
                location = random.choice(locations)

                class_slug = f"{class_name.lower().replace(' ', '-')}-{start.strftime('%Y%m%d%H%M')}"

                cls, created = Class.objects.get_or_create(
                    slug=class_slug,
                    defaults={
                        'title': class_name,
                        'description': desc,
                        'trainer': trainer,
                        'location': location,
                        'start_time': start,
                        'end_time': end,
                        'capacity': random.randint(15, 25),
                        'difficulty_level': level,
                        'is_active': True
                    }
                )
                if created:
                    classes_created += 1

            self.stdout.write(f'Created {classes_created} classes')

            # Create blog posts
            blog_posts_data = [
                {
                    'title': '10 Essential Tips for Building Muscle Mass',
                    'slug': '10-essential-tips-building-muscle-mass',
                    'body': '''# Building Muscle Mass: A Comprehensive Guide

                Building muscle mass requires a combination of proper training, nutrition, and recovery. Here are 10 essential tips to help you achieve your muscle-building goals:

                ## 1. Progressive Overload
                Continuously challenge your muscles by gradually increasing weight, reps, or intensity.

                ## 2. Protein Intake
                Aim for 1.6-2.2g of protein per kg of bodyweight daily to support muscle growth.

                ## 3. Compound Exercises
                Focus on multi-joint exercises like squats, deadlifts, and bench press.

                ## 4. Adequate Rest
                Muscles grow during recovery. Ensure 7-9 hours of quality sleep per night.

                ## 5. Consistent Training
                Maintain a regular workout schedule, training each muscle group 2-3 times per week.

                ## 6. Caloric Surplus
                Consume slightly more calories than you burn to fuel muscle growth.

                ## 7. Proper Form
                Quality over quantity - perfect your technique to maximize gains and prevent injury.

                ## 8. Hydration
                Stay well-hydrated to optimize muscle function and recovery.

                ## 9. Track Progress
                Keep a workout log to monitor improvements in strength and size.

                ## 10. Patience
                Building muscle takes time. Stay consistent and trust the process.

                Remember, everyone's body responds differently. Listen to your body and adjust your approach as needed.''',
                    'excerpt': 'Discover the fundamental principles of muscle building with these 10 proven tips from our expert trainers.',
                    'tags': 'muscle building, strength training, fitness tips, workout',
                    'is_published': True,
                    'published_at': timezone.now() - timedelta(days=5)
                },
                {
                    'title': 'The Benefits of Morning Workouts',
                    'slug': 'benefits-morning-workouts',
                    'body': '''# Why Morning Workouts Transform Your Day

                Starting your day with exercise can have profound effects on your physical and mental well-being.

                ## Enhanced Metabolism
                Morning exercise kickstarts your metabolism, helping you burn more calories throughout the day.

                ## Improved Mental Clarity
                Exercise releases endorphins and increases blood flow to the brain, enhancing focus and productivity.

                ## Better Sleep
                Regular morning workouts help regulate your circadian rhythm, leading to improved sleep quality.

                ## Consistency
                Morning workouts are less likely to be skipped due to unexpected daily obligations.

                ## Increased Energy
                Contrary to popular belief, morning exercise boosts energy levels for the entire day.

                Join us for our morning classes and experience the difference!''',
                    'excerpt': 'Learn how morning workouts can boost your metabolism, mental clarity, and overall well-being.',
                    'tags': 'morning workout, fitness routine, healthy habits',
                    'is_published': True,
                    'published_at': timezone.now() - timedelta(days=12)
                },
                {
                    'title': 'Nutrition Guide for Optimal Fitness Performance',
                    'slug': 'nutrition-guide-optimal-fitness',
                    'body': '''# Fueling Your Fitness Journey

                Proper nutrition is the foundation of any successful fitness program. Here's your comprehensive guide.

                ## Macronutrients Balance
                - **Protein**: 25-35% of total calories
                - **Carbohydrates**: 40-50% of total calories
                - **Fats**: 20-30% of total calories

                ## Pre-Workout Nutrition
                Eat a balanced meal 2-3 hours before training, combining complex carbs and lean protein.

                ## Post-Workout Recovery
                Consume protein and carbs within 30-60 minutes after exercise to optimize recovery.

                ## Hydration Strategy
                Drink water consistently throughout the day. Aim for at least 3 liters daily.

                ## Meal Timing
                Eat every 3-4 hours to maintain stable energy levels and support muscle recovery.

                ## Whole Foods First
                Prioritize whole, unprocessed foods over supplements when possible.

                Consult with our nutrition experts to create a personalized meal plan!''',
                    'excerpt': 'Master the fundamentals of sports nutrition to maximize your workout results and recovery.',
                    'tags': 'nutrition, diet, fitness, healthy eating',
                    'is_published': True,
                    'published_at': timezone.now() - timedelta(days=20)
                }
            ]

            for post_data in blog_posts_data:
                post, created = BlogPost.objects.get_or_create(
                    slug=post_data['slug'],
                    defaults={**post_data, 'author': admin}
                )
                if created:
                    self.stdout.write(f'Created blog post: {post.title}')

            # Create testimonials
            testimonials_data = [
                {
                    'user_name': 'Jessica Martinez',
                    'content': 'ApexLiftStudio has completely transformed my life! The trainers are knowledgeable, the facilities are top-notch, and the community is incredibly supportive. I\'ve lost 30 pounds and gained so much confidence!',
                    'rating': 5,
                    'is_visible': True,
                    'featured': True
                },
                {
                    'user_name': 'David Thompson',
                    'content': 'Best gym I\'ve ever joined. The variety of classes keeps things interesting, and the personal training sessions have helped me achieve goals I never thought possible.',
                    'rating': 5,
                    'is_visible': True,
                    'featured': True
                },
                {
                    'user_name': 'Lisa Chang',
                    'content': 'The Premium membership is worth every penny. The personal training, massage therapy, and priority booking make my fitness journey seamless and enjoyable.',
                    'rating': 5,
                    'is_visible': True,
                    'featured': True
                },
                {
                    'user_name': 'Robert Williams',
                    'content': 'Clean facilities, modern equipment, and friendly staff. The location is convenient and the hours work perfectly with my schedule. Highly recommend!',
                    'rating': 4,
                    'is_visible': True,
                    'featured': False
                }
            ]

            for testimonial_data in testimonials_data:
                testimonial = Testimonial.objects.create(**testimonial_data)
                if created:
                    self.stdout.write(f'Created testimonial from: {testimonial.user_name}')

            # Create a membership for the test user
            basic_plan = MembershipPlan.objects.get(slug='basic')
            membership, created = Membership.objects.get_or_create(
                user=member,
                plan=basic_plan,
                defaults={
                    'status': 'active',
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timedelta(days=30),
                    'auto_renew': True
                }
            )
            if created:
                self.stdout.write(f'Created membership for {member.username}')

                # Create a payment record
                Payment.objects.create(
                    user=member,
                    membership=membership,
                    amount=basic_plan.price_monthly,
                    currency='INR',
                    status='succeeded',
                    payment_method='card',
                    description=f'{basic_plan.name} Monthly Membership'
                )
                self.stdout.write(f'Created payment record for {member.username}')

            # Create some bookings for the test user
            upcoming_classes = Class.objects.filter(
                start_time__gte=timezone.now(),
                is_active=True
            )[:3]

            for cls in upcoming_classes:
                booking, created = Booking.objects.get_or_create(
                    user=member,
                    class_instance=cls,
                    defaults={'status': 'confirmed'}
                )
                if created:
                    self.stdout.write(f'Created booking for {member.username}: {cls.title}')

            self.stdout.write(self.style.SUCCESS('Successfully seeded demo data!'))
            self.stdout.write(self.style.SUCCESS('\nDemo Credentials:'))
            self.stdout.write(self.style.SUCCESS('Admin: admin / admin123'))
            self.stdout.write(self.style.SUCCESS('Member: johndoe / testpass123'))