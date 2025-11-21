from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import *
from .models import SubscriptionTable, NewsTable
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import SubscriptionPlans, SubscriptionTable
from .models import NewsTable, SubscriptionTable
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from .models import NewsTable,  SubscriptionTable
from django.core.paginator import Paginator
from django.db.models import Q


# ================================register view=====================================

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.mail import EmailMessage
from django.conf import settings

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if password != confirm_password:
            messages.error(request, "Password and Confirm password do not match!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        username = email.split('@')[0]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if role and role.lower() in dict(UserProfile.ROLE_CHOICES):
            profile.role = role.lower()
        profile.save()

        # ✅ HTML email bhejna
        try:
            html_email = EmailMessage(
                subject='Welcome to Our Site! 🎉',
                body=f'<h2>Hello {first_name},</h2><p>Thanks for registering on our website!</p>',
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            html_email.content_subtype = 'html'  # HTML content type
            html_email.send()
        except Exception as e:
            print(f"Email could not be sent: {e}")

        messages.success(request, "Registration successful! Please check your email.")
        return redirect('login')

    return render(request, 'register.html')



# ===============================================login view=====================================

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        username = email.split("@")[0]   # same logic we used in register

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")  # redirect to home page or dashboard
        else:
            messages.error(request, "Invalid email or password!")

    return render(request, "login.html")




# ===============================logout view=====================================


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

# ================================user_table view=====================================

def user_table(request):
    plans = SubscriptionPlans.objects.all()
    return render(request, 'plans.html', {'plans': plans})

# ================================home view=====================================

def home(request):
    news_list = NewsTable.objects.filter(is_deleted=False)
    
    # Agar user login hai, to uska role nikalo
    role = None
    if request.user.is_authenticated:
        try:
            role = request.user.userprofile.role
        except:
            role = "User"  # default role

    return render(request, 'home.html', {
        'news_list': news_list,
        'role': role
    })



# ================================user_table view=====================================

def user_table(request):
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()
     
    if not user_has_active_plan:
        plans = SubscriptionPlans.objects.filter(is_active=True)
        return render(request, 'plans.html', {'plans': plans})
    
    else:
        return redirect("create_news") 
    


# ==================================subscription_plans view=====================================


@login_required(login_url='login')
def subscription_plans(request):
    plans = SubscriptionPlans.objects.filter(is_active=True)
    return render(request, 'plans.html', {'plans': plans})

# ================================plan_pay view===================================


@login_required(login_url='login')
def plan_pay(request, slug):
    plan = get_object_or_404(SubscriptionPlans, slug=slug, is_active=True)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        SubscriptionTable.objects.create(
            user=request.user,
            plan=plan,
            enrolled_at=timezone.now(),
            expired_at=timezone.now() + timezone.timedelta(days=plan.days),
            amount_paid=plan.discount_price or plan.price,
            payment_method=payment_method,
            status='pending',
            payment_status='pending'
        )

        messages.success(request, "✅ Payment request submitted successfully! Waiting for admin approval.")
        return redirect('thank_you')

    return render(request, 'plan_pay.html', {'plan': plan})



# ==============================================thank_you view===================================

@login_required(login_url='login')
def thank_you(request):
    messages.info(request, "Your plan enrollment request has been sent to admin.")
    return render(request, 'thank_you.html')





# ==============================================subscription_status view===================================


@login_required
def subscription_status(request):
    subscription = SubscriptionTable.objects.filter(user=request.user).last()
    return render(request, 'subscription_status.html', {'subscription': subscription})



# ==================================create_news view=========================================


@login_required(login_url='login')
def create_news(request):
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    if not user_has_active_plan:
        messages.warning(request, "You cannot upload news until your payment is approved by admin.")
        return redirect('plans')  # or wherever your plans page is
    category_choices = [choice[0] for choice in NewsTable._meta.get_field('category').choices]

    # normal upload logic here
    if request.method == 'POST':
        heading = request.POST.get('heading')
        heading_image = request.FILES.get('heading_image')
        description = request.POST.get('description')
        description_2 = request.POST.get('description_2')
        category = request.POST.get('category')
        published_at = request.POST.get('published_at')

        # ✅ Validate all required fields
        if not all([heading, heading_image, description, published_at]):
            messages.error(request, "Please fill all required fields before submitting.")
            return redirect('create_news')

        # ✅ Save to database
        NewsTable.objects.create(
            heading=heading,
            heading_image=heading_image,
            description=description,
            description_2=description_2,
            published_at=published_at,
            category=category,
            author=request.user
        )

        messages.success(request, "✅ News submitted successfully!")
        return redirect('home')

    return render(request, 'create_news.html', {'user_has_active_plan': user_has_active_plan, 'category_choices': category_choices})


# =============================================home view=========================================
@login_required(login_url='login')
def home(request):
    # 🔹 Step 1: Get search query and category from URL
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    # 🔹 Step 2: Start with all news
    news_list = NewsTable.objects.filter(is_deleted=False)

    # 🔹 Step 3: Filter by category (if selected)
    if selected_category:
        news_list = news_list.filter(category__iexact=selected_category)

    # 🔹 Step 4: Filter by search query (if any)
    if query:
        news_list = news_list.filter(
            Q(heading__icontains=query) |
            Q(description__icontains=query) |
            Q(description_2__icontains=query) |
            Q(category__icontains=query)
        )

    # 🔹 Step 5: Order by latest published
    news_list = news_list.order_by('-published_at')

    # 🔹 Step 6: Hero section news
    hero_news = NewsTable.objects.filter(
        is_featured=True, is_deleted=False
    ).order_by('-published_at')[:3]

    # 🔹 Step 7: Check if user has active plan
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    # 🔹 Step 8: Pagination
    paginator = Paginator(news_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🔹 Step 9: Get categories from model choices
    categories = [c[0] for c in NewsTable._meta.get_field('category').choices]

    # 🔹 Step 10: Render
    return render(request, 'home.html', {
        'hero_news': hero_news,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'user_has_active_plan': user_has_active_plan,
    })

# =============================gmail test view=============================


def send_test_email(request):
    subject = "Test Django"
    message = "abcdeefghertyuifghjkjklmnopqrstuvwxyz ."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["rohitjhatwal230@gmail.com"]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse("✅ Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"❌ Error: {e}")





# ========================================news_detail=========================================

@login_required(login_url='login')
def news_detail(request, news_id):
    # ✅ Check if user has active paid plan
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    if not user_has_active_plan:
        messages.warning(request, "Please activate a plan to read the full article.")
        return redirect('user_table')

    # ✅ Get the current news
    news = get_object_or_404(NewsTable, id=news_id, is_deleted=False)

    # ✅ Get related news from same category (excluding current one)
    related_news = NewsTable.objects.filter(
        is_deleted=False,
        category=news.category
    ).exclude(id=news.id).order_by('-published_at')

    # ✅ Pagination: 6 related news per page
    paginator = Paginator(related_news, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news_detail.html', {
        'news': news,
        'page_obj': page_obj,
        'user_has_active_plan': user_has_active_plan
    })



# ==================================search news view=========================================
from django.shortcuts import render
from django.http import JsonResponse
from .models import NewsTable
from rapidfuzz import fuzz

def search_news(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        all_news = NewsTable.objects.filter(is_deleted=False)
        matched_news = []

        for n in all_news:
            # Har field ke liye similarity check
            score = max(
                fuzz.partial_ratio(query.lower(), n.heading.lower()),
                fuzz.partial_ratio(query.lower(), n.description.lower()),
                fuzz.partial_ratio(query.lower(), n.description_2.lower())
            )
            # Agar match 70% ya usse zyada hai to include karo
            if score >= 50:
                matched_news.append((n, score))

        # Sort by best match first
        matched_news.sort(key=lambda x: x[1], reverse=True)
        results = [n for n, score in matched_news[:20]]

        # 🔹 AJAX request ke liye (live search)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = [{'id': n.id, 'heading': n.heading} for n in results]
            return JsonResponse({'results': data})

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })



# ==================================NewsVideo========================
from django.shortcuts import render, get_object_or_404
from .models import NewsVideo, NewsTable

# 🏠 Home page view — show featured and all videos
def news_video(request):
    videos = NewsVideo.objects.order_by('-uploaded_at')
    featured_video = videos.first() if videos.exists() else None

    return render(request, 'home.html', {
        'featured_video': featured_video,
        'videos': videos,  # send all videos too
    })


# 🎞️ Gallery page view — show all videos in grid
def video_gallery(request):
    videos = NewsVideo.objects.order_by('-uploaded_at')
    return render(request, 'gallery.html', {
        'videos': videos
    })


# 🎬 Video detail page — play video + show related
def video_detail(request, video_id):
    video = get_object_or_404(NewsVideo, id=video_id)

    # Related Videos
    related_videos = NewsVideo.objects.filter(
        category=video.category
    ).exclude(id=video.id)[:6]

    # Related News Articles from NewsTable 
    related_news = NewsTable.objects.filter(
        category=video.category,
        is_deleted=False
    ).order_by('-published_at')[:6]

    return render(request, "video_detail.html", {
        "video": video,
        "related_videos": related_videos,
        "related_news": related_news,
    })




def video_list(request):
    videos = NewsVideo.objects.filter(is_featured=False).order_by('-uploaded_at')
    return render(request, 'video_list.html', {'videos': videos})



# ===================================forgot_password view=========================================

import random
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if not User.objects.filter(email=email).exists():
            messages.error(request, "Email not found!")
            return redirect('forgot_password')

        # Generate 6 digit OTP
        otp = random.randint(100000, 999999)

        # Session me save karna
        request.session['reset_email'] = email
        request.session['reset_otp'] = str(otp)

        # Send OTP
        html_body = f"""
        <h3>Your OTP Code</h3>
        <p>Your password reset OTP is: <strong>{otp}</strong></p>
        """

        email_message = EmailMessage(
            "Password Reset OTP",
            html_body,
            settings.EMAIL_HOST_USER,
            [email],
        )
        email_message.content_subtype = 'html'
        email_message.send()

        messages.success(request, "OTP sent to your email!")
        return redirect('verify_otp')

    return render(request, 'forgot_password.html')


# ===================================verify_otp view=========================================

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('reset_otp')

        if entered_otp == saved_otp:
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP!")
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')


# ===================================reset_password view=========================================


from django.contrib.auth.hashers import make_password

def reset_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('reset_password')

        email = request.session.get('reset_email')
        user = User.objects.get(email=email)
        user.password = make_password(password)
        user.save()

        # Clear session
        request.session.pop('reset_email', None)
        request.session.pop('reset_otp', None)

        messages.success(request, "Password reset successful! Please login.")
        return redirect('login')

    return render(request, 'reset_password.html')



from .models import NewsVideo


@login_required(login_url='login')
def upload_video(request):

    # ✅ Check if user has an active and paid subscription
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    if not user_has_active_plan:
        messages.warning(request, "You cannot upload videos until your payment is approved by admin.")
        return redirect('plans')

    # Get category choices
    category_choices = [choice[0] for choice in NewsVideo._meta.get_field('category').choices]

    # -------------------------
    # ✅ When form submitted
    # -------------------------
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        is_featured = 'is_featured' in request.POST

        # -------------------------
        # ✅ Validate required fields
        # -------------------------
        if not all([title, description, video_file]):
            messages.error(request, "Please fill all required fields before submitting.")
            return redirect('upload_video')

        # -------------------------
        # ✅ Save video to database
        # -------------------------
        NewsVideo.objects.create(
            title=title,
            description=description,
            category=category,
            video_file=video_file,
            thumbnail=thumbnail,
            is_featured=is_featured,
            author=request.user
        )

        messages.success(request, "🎉 Video uploaded successfully!")
        return redirect('video_list')

    # -------------------------
    # Page Load
    # -------------------------
    return render(request, "News_video.html", {
        "user_has_active_plan": user_has_active_plan,
        "category_choices": category_choices
    })