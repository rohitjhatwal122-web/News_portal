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

        messages.success(request, "Registration successful!")
        return redirect('login')

    return render(request, 'register.html')



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







def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')



def user_table(request):
    plans = SubscriptionPlans.objects.all()
    return render(request, 'plans.html', {'plans': plans})

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
        return redirect("create_news")  # Corrected the redirect statement








@login_required(login_url='login')
def subscription_plans(request):
    plans = SubscriptionPlans.objects.filter(is_active=True)
    return render(request, 'plans.html', {'plans': plans})


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


@login_required(login_url='login')
def thank_you(request):
    messages.info(request, "Your plan enrollment request has been sent to admin.")
    return render(request, 'thank_you.html')




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import NewsTable,  SubscriptionTable

# @login_required
# def create_news(request):
#     # Check if the user's subscription is approved
#     subscription = SubscriptionTable.objects.filter(user=request.user, is_approved=True, status='active').last()

#     if not subscription:
#         messages.error(request, "Your subscription is not approved yet. Please wait for admin approval.")
#         return redirect('subscription_status')  # redirect to a page showing their current subscription

#     # Fetch categories to pass to template
    

#     if request.method == 'POST':
#         heading = request.POST.get('heading')
#         description = request.POST.get('description')
#         description_2 = request.POST.get('description_2')
#         heading_image = request.FILES.get('heading_image')
#         published_at = request.POST.get('published_at')
#         category_id = request.POST.get('category')

        

#         NewsTable.objects.create(
#             heading=heading,
#             description=description,
#             description_2=description_2,
#             heading_image=heading_image,
#             author=request.user,
#             published_at=published_at,
            
#         )

#         messages.success(request, "✅ News uploaded successfully!")
#         return redirect('dashboard')

#     return render(request, 'create_news.html', {
        
#     })




@login_required
def subscription_status(request):
    subscription = SubscriptionTable.objects.filter(user=request.user).last()
    return render(request, 'subscription_status.html', {'subscription': subscription})


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





@login_required(login_url='login')
def home(request):
    news_list = NewsTable.objects.filter(is_deleted=False).order_by('-published_at')
    hero_news = NewsTable.objects.filter(is_featured=True, is_deleted=False).order_by('-published_at')[:3]
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    return render(request, 'home.html', {
        'news_list': news_list,
        'hero_news': hero_news,
        'user_has_active_plan': user_has_active_plan
    })

# =============================gmail test view=============================


def send_test_email(request):
    subject = "Test Email from Django"
    message = "abcdeefghijklmnopqrstuvwxyz ."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["rohitjhatwal230@gmail.com"]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse("✅ Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"❌ Error: {e}")









# from django.core.paginator import Paginator
# def category_news_list(request, cat_id):
#     # get the category or 404
#     category = get_object_or_404(NewsCategory, id=cat_id)

#     # filter news: not deleted, same category, published_at <= now
#     news_qs = NewsTable.objects.filter(
#         is_deleted=False,
#         category=category,
#         published_at__lte=timezone.now()
#     ).order_by('-published_at')

#     # paginator (12 per page as you used earlier)
#     paginator = Paginator(news_qs, 12)
#     page = request.GET.get('page')
#     news_list = paginator.get_page(page)

#     return render(request, 'news/category_list.html', {
#         'category': category,
#         'news_list': news_list,
#     })


# Optional: if you add a slug field to categories, use this view:
# def category_news_by_slug(request, slug):
#     category = get_object_or_404(NewsCategory, slug=slug)  # requires slug field
#     news_qs = NewsTable.objects.filter(is_deleted=False, category=category, published_at__lte=timezone.now()).order_by('-published_at')
#     paginator = Paginator(news_qs, 12)
#     news_list = paginator.get_page(request.GET.get('page'))
#     return render(request, 'newss/category_list.html', {'category': category, 'news_list': news_list})




@login_required(login_url='login')
def news_detail(request, news_id):
    # If user does not have an active paid subscription, redirect to plans page
    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    if not user_has_active_plan:
        messages.warning(request, "Please activate a plan to read the full article.")
        return redirect('user_table')   # this name is your plans page (in urls.py you used name='user_table')

    # user has active plan → show the full news
    news = get_object_or_404(NewsTable, id=news_id, is_deleted=False)
    allnews = NewsTable.objects.filter(is_deleted=False).order_by('-published_at')
    return render(request, 'news_detail.html', {'news': news, 'allnews': allnews})

