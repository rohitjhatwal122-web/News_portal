from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


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


# def user_table(request):
#     users = User.objects.all()
#     return render(request, 'table.html', {'users': users})


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


# def news_detail(request):
#     return render(request,"news_detail.html")



