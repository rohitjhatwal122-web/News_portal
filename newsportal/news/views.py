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


def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Password and Confirm password do not match!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        username = email.split('@')[0]  # generate username from email

        # ✅ Saving to User model
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.save()

        messages.success(request, "Registration successful!")
        return redirect('register')

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



@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')




def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')



def user_table(request):
    plans = SubscriptionPlans.objects.all()
    return render(request, 'plans.html', {'plans': plans})

def home(request):
    news_list = NewsTable.objects.filter(is_deleted=False)
    return render(request, 'home.html', {'news_list': news_list})




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




@login_required
def create_news(request):
    # Check if the user's subscription is approved
    subscription = SubscriptionTable.objects.filter(user=request.user, is_approved=True, status='active').last()

    if not subscription:
        messages.error(request, "Your subscription is not approved yet. Please wait for admin approval.")
        return redirect('subscription_status')  # redirect to a page showing their current subscription

    if request.method == 'POST':
        heading = request.POST.get('heading')
        description = request.POST.get('description')
        heading_image = request.FILES.get('heading_image')

        NewsTable.objects.create(
            heading=heading,
            description=description,
            heading_image=heading_image,
            author=request.user,
            published_at=timezone.now(),
        )

        messages.success(request, "✅ News uploaded successfully!")
        return redirect('dashboard')

    return render(request, 'create_news.html')




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

    # normal upload logic here
    if request.method == 'POST':
        heading = request.POST.get('heading')
        heading_image = request.FILES.get('heading_image')
        description = request.POST.get('description')
        description_2 = request.POST.get('description_2')
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
            author=request.user
        )

        messages.success(request, "✅ News submitted successfully!")
        return redirect('home')

    return render(request, 'create_news.html', {'user_has_active_plan': user_has_active_plan})





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
    return render(request, 'news_detail.html', {'news': news})





@login_required(login_url='login')
def home(request):
    news_list = NewsTable.objects.filter(is_deleted=False).order_by('-published_at')

    user_has_active_plan = SubscriptionTable.objects.filter(
        user=request.user,
        payment_status='paid',
        status='active'
    ).exists()

    return render(request, 'home.html', {
        'news_list': news_list,
        'user_has_active_plan': user_has_active_plan
    })
