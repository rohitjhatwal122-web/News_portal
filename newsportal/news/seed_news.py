from django.utils import timezone
from django.contrib.auth.models import User
from .models import NewsTable

def run():
    # Make sure a user exists (you can change the username if needed)
    user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})

    news_data = [
        {
            'heading': 'Breakingg: New Feature Released!',
            'heading_image': 'media/news_images/virat_kohli.jpg',
            'description': 'We are excited to announce a new update with amazing features and performance improvements.',
            'description_2': 'Detailed article continues here with more explanation...',
        },
        {
            'heading': 'Tech World: AI Revolution',
            'heading_image': 'news_images/sample2.jpg',
            'description': 'AI technology is changing the world rapidly — from chatbots to automation tools.',
            'description_2': 'Read full analysis about the latest AI trends and companies leading the change.',
        },
        {
            'heading': 'Sports: Championship Highlights',
            'heading_image': 'news_images/sample3.jpg',
            'description': 'The championship concluded with breathtaking matches and unexpected results.',
            'description_2': 'Exclusive interviews, stats, and behind-the-scenes insights await our readers.',
        },
    ]

    for data in news_data:
        NewsTable.objects.get_or_create(
            heading=data['heading'],
            defaults={
                'heading_image': data['heading_image'],
                'description': data['description'],
                'description_2': data['description_2'],
                'author': user,
                'published_at': timezone.now(),
            }
        )

    print("✅ News seeded successfully!")
