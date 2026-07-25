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
                'email': 'admin@apexlift.in',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            Profile.objects.create(user=admin, phone='+91-9000000000')
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))

        # Create test member user
        member, created = User.objects.get_or_create(
            username='rahulsharma',
            defaults={
                'email': 'rahul.sharma@example.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma'
            }
        )
        if created:
            member.set_password('testpass123')
            member.save()
            Profile.objects.create(user=member, phone='+91-9820011122')
            self.stdout.write(self.style.SUCCESS('Created member user: rahulsharma / testpass123'))

        # Create a second test member
        member2, created = User.objects.get_or_create(
            username='priyapatel',
            defaults={
                'email': 'priya.patel@example.com',
                'first_name': 'Priya',
                'last_name': 'Patel'
            }
        )
        if created:
            member2.set_password('testpass123')
            member2.save()
            Profile.objects.create(user=member2, phone='+91-9845566778')
            self.stdout.write(self.style.SUCCESS('Created member user: priyapatel / testpass123'))

        # Create membership plans (INR pricing)
        plans_data = [
            {
                'name': 'Basic',
                'slug': 'basic',
                'description': 'Perfect for getting started with your fitness journey',
                'price_monthly': Decimal('999.00'),
                'price_yearly': Decimal('9999.00'),
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
                'price_monthly': Decimal('1799.00'),
                'price_yearly': Decimal('18999.00'),
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
                'price_monthly': Decimal('2999.00'),
                'price_yearly': Decimal('31999.00'),
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

        # Create trainers (Indian names)
        trainers_data = [
            {
                'name': 'Arjun Mehta',
                'slug': 'arjun-mehta',
                'bio': 'Certified strength coach with 10+ years of experience specializing in powerlifting and sports nutrition.',
                'specialties': 'Strength Training, Nutrition, Weight Loss',
                'years_experience': 10,
                'certifications': 'NASM-CPT, Sports Nutrition Certified',
                'email': 'arjun.mehta@apexlift.in',
                'phone': '+91-9812340001'
            },
            {
                'name': 'Rohan Kapoor',
                'slug': 'rohan-kapoor',
                'bio': 'Former state-level athlete turned fitness coach, passionate about functional training and sports performance.',
                'specialties': 'Functional Training, Sports Performance, HIIT',
                'years_experience': 8,
                'certifications': 'CSCS, TRX Certified',
                'email': 'rohan.kapoor@apexlift.in',
                'phone': '+91-9812340002'
            },
            {
                'name': 'Ananya Iyer',
                'slug': 'ananya-iyer',
                'bio': 'Yoga and Pilates instructor dedicated to mind-body wellness and flexibility training.',
                'specialties': 'Yoga, Pilates, Flexibility, Mindfulness',
                'years_experience': 12,
                'certifications': 'RYT-500, Pilates Mat Certification',
                'email': 'ananya.iyer@apexlift.in',
                'phone': '+91-9812340003'
            },
            {
                'name': 'Vikram Singh',
                'slug': 'vikram-singh',
                'bio': 'Competitive bodybuilder and strength specialist focused on hypertrophy and progressive overload programming.',
                'specialties': 'Bodybuilding, Hypertrophy, Strength Training',
                'years_experience': 9,
                'certifications': 'ACE-CPT, ISSA Bodybuilding Specialist',
                'email': 'vikram.singh@apexlift.in',
                'phone': '+91-9812340004'
            },
            {
                'name': 'Neha Reddy',
                'slug': 'neha-reddy',
                'bio': 'Dance and cardio fitness expert bringing high-energy Zumba and aerobics classes to members of all levels.',
                'specialties': 'Zumba, Cardio, Aerobics, Dance Fitness',
                'years_experience': 6,
                'certifications': 'Zumba Certified Instructor, ACE Group Fitness',
                'email': 'neha.reddy@apexlift.in',
                'phone': '+91-9812340005'
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

        # Create locations (Indian cities)
        locations_data = [
            {
                'name': 'Andheri Branch',
                'slug': 'andheri',
                'address': '12 Link Road, Andheri West',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'postal_code': '400053',
                'latitude': 19.1364,
                'longitude': 72.8296,
                'phone': '022-40011001',
                'email': 'andheri@apexlift.in',
                'hours': 'Mon-Fri: 5AM-11PM, Sat-Sun: 6AM-10PM',
                'amenities': 'Pool, Steam Room, Personal Training, Cafe, Parking'
            },
            {
                'name': 'Koramangala Branch',
                'slug': 'koramangala',
                'address': '45 5th Block, Koramangala',
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'postal_code': '560095',
                'latitude': 12.9352,
                'longitude': 77.6245,
                'phone': '080-50022002',
                'email': 'koramangala@apexlift.in',
                'hours': 'Mon-Fri: 5AM-10PM, Sat-Sun: 7AM-9PM',
                'amenities': 'Yoga Studio, CrossFit Zone, Sauna, Juice Bar, Locker Room'
            },
            {
                'name': 'Banjara Hills Branch',
                'slug': 'banjara-hills',
                'address': '78 Road No. 12, Banjara Hills',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'postal_code': '500034',
                'latitude': 17.4126,
                'longitude': 78.4483,
                'phone': '040-60033003',
                'email': 'banjarahills@apexlift.in',
                'hours': 'Mon-Fri: 5:30AM-10:30PM, Sat-Sun: 7AM-9PM',
                'amenities': 'Swimming Pool, Spa, Kids Zone, Cafe, Free Parking'
            },
            {
                'name': 'Connaught Place Branch',
                'slug': 'connaught-place',
                'address': '9 Outer Circle, Connaught Place',
                'city': 'New Delhi',
                'state': 'Delhi',
                'postal_code': '110001',
                'latitude': 28.6315,
                'longitude': 77.2167,
                'phone': '011-70044004',
                'email': 'cp@apexlift.in',
                'hours': 'Mon-Fri: 5AM-11PM, Sat-Sun: 6AM-10PM',
                'amenities': 'CrossFit Zone, Sauna, Steam Room, Nutrition Bar, Valet Parking'
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
            ('Bodybuilding Basics', 'Learn proper hypertrophy training techniques', 'intermediate', trainers[3]),
            ('Zumba Dance Party', 'High-energy dance cardio workout for all levels', 'beginner', trainers[4]),
            ('Power Lifting Fundamentals', 'Master the big three lifts safely and effectively', 'advanced', trainers[0]),
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
            },
            {
                'title': 'A Beginner\'s Guide to Vegetarian Protein Sources',
                'slug': 'beginners-guide-vegetarian-protein-sources',
                'body': '''# Vegetarian Protein: Building Muscle Without Meat

Many of our members follow a vegetarian lifestyle, and getting enough protein is completely achievable with the right food choices.

## Paneer and Dairy
Paneer, curd, and milk are excellent protein sources easily available across India, offering roughly 18-20g of protein per 100g.

## Lentils and Pulses
Dals like moong, masoor, and chana are protein powerhouses, also rich in fiber and micronutrients.

## Soy Products
Tofu and soy chunks (nutrela) are complete proteins, ideal for those looking to increase intake without dairy.

## Nuts and Seeds
Almonds, peanuts, and chia seeds make great snacks that boost daily protein totals.

## Protein Supplements
Plant-based or whey protein powders can help bridge the gap for those with higher training volume.

Talk to our in-house nutrition coach for a personalized vegetarian meal plan!''',
                'excerpt': 'Discover how to hit your daily protein targets on a vegetarian diet using foods commonly available in India.',
                'tags': 'nutrition, vegetarian, protein, diet',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=8)
            },
            {
                'title': 'How to Stay Motivated During Monsoon Season',
                'slug': 'stay-motivated-monsoon-season',
                'body': '''# Keeping Your Fitness Routine on Track This Monsoon

Rainy season in India often disrupts outdoor activity and daily routines. Here's how to stay consistent.

## Shift to Indoor Training
Use the gym floor for strength training and cardio machines instead of outdoor runs.

## Try Our Group Classes
Zumba, HIIT, and spin classes are great indoor alternatives that keep workouts fun and social.

## Watch Your Immunity
Monsoon season can affect immunity — prioritize sleep, hydration, and vitamin C rich foods.

## Plan Around the Weather
Book morning slots before the rains typically pick up in the afternoon.

## Stay Accountable
Book classes in advance and bring a workout buddy to stay consistent even on gloomy days.

See you at the gym, rain or shine!''',
                'excerpt': 'Practical tips to keep your fitness routine consistent through the Indian monsoon season.',
                'tags': 'motivation, monsoon, fitness routine, indoor workout',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=2)
            }
        ]

        for post_data in blog_posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults={**post_data, 'author': admin}
            )
            if created:
                self.stdout.write(f'Created blog post: {post.title}')

        # Create testimonials (Indian names)
        testimonials_data = [
            {
                'user_name': 'Jessica D\'Souza',
                'content': 'ApexLiftStudio has completely transformed my life! The trainers are knowledgeable, the facilities are top-notch, and the community is incredibly supportive. I\'ve lost 12 kilos and gained so much confidence!',
                'rating': 5,
                'is_visible': True,
                'featured': True
            },
            {
                'user_name': 'Dev Thakur',
                'content': 'Best gym I\'ve ever joined. The variety of classes keeps things interesting, and the personal training sessions have helped me achieve goals I never thought possible.',
                'rating': 5,
                'is_visible': True,
                'featured': True
            },
            {
                'user_name': 'Lisa Chandra',
                'content': 'The Premium membership is worth every rupee. The personal training, massage therapy, and priority booking make my fitness journey seamless and enjoyable.',
                'rating': 5,
                'is_visible': True,
                'featured': True
            },
            {
                'user_name': 'Rajesh Williams',
                'content': 'Clean facilities, modern equipment, and friendly staff. The location is convenient and the hours work perfectly with my schedule. Highly recommend!',
                'rating': 4,
                'is_visible': True,
                'featured': False
            },
            {
                'user_name': 'Simran Kaur',
                'content': 'I joined for the Zumba classes and stayed for the whole community! Neha ma\'am is an amazing instructor and every session feels like a celebration.',
                'rating': 5,
                'is_visible': True,
                'featured': True
            },
            {
                'user_name': 'Aditya Nair',
                'content': 'Great equipment and knowledgeable trainers. Vikram helped me completely restructure my lifting program and I\'ve seen real strength gains in just 3 months.',
                'rating': 5,
                'is_visible': True,
                'featured': False
            },
            {
                'user_name': 'Meera Joshi',
                'content': 'Affordable pricing compared to other gyms in the area, without compromising on quality. The Basic plan is perfect for someone just starting out.',
                'rating': 4,
                'is_visible': True,
                'featured': False
            }
        ]

        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                user_name=testimonial_data['user_name'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(f'Created testimonial from: {testimonial.user_name}')

        # Create memberships for test users
        basic_plan = MembershipPlan.objects.get(slug='basic')
        plus_plan = MembershipPlan.objects.get(slug='plus')

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

        membership2, created = Membership.objects.get_or_create(
            user=member2,
            plan=plus_plan,
            defaults={
                'status': 'active',
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=30),
                'auto_renew': True
            }
        )
        if created:
            self.stdout.write(f'Created membership for {member2.username}')

            Payment.objects.create(
                user=member2,
                membership=membership2,
                amount=plus_plan.price_monthly,
                currency='INR',
                status='succeeded',
                payment_method='card',
                description=f'{plus_plan.name} Monthly Membership'
            )
            self.stdout.write(f'Created payment record for {member2.username}')

        # Create some bookings for the test users
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

        upcoming_classes2 = Class.objects.filter(
            start_time__gte=timezone.now(),
            is_active=True
        )[3:6]

        for cls in upcoming_classes2:
            booking, created = Booking.objects.get_or_create(
                user=member2,
                class_instance=cls,
                defaults={'status': 'confirmed'}
            )
            if created:
                self.stdout.write(f'Created booking for {member2.username}: {cls.title}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data!'))
        self.stdout.write(self.style.SUCCESS('\nDemo Credentials:'))
        self.stdout.write(self.style.SUCCESS('Admin: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Member 1: rahulsharma / testpass123'))
        self.stdout.write(self.style.SUCCESS('Member 2: priyapatel / testpass123'))