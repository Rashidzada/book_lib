from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile,Book
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    return render(request,'index.html')


def contact(request):
    return render(request,'contact.html')


def about(request):
    return render(request,'about.html')



def book(request):
    return render(request,'book.html')

@login_required(login_url='login_view')
def forum(request):
    return render(request,'forum.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            
            # Check user's role
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                user_profile = None

            if user_profile is not None:
                if user_profile.role == 'teacher':
                    return redirect('teacher_dashboard')  # Redirect to teacher dashboard
                else:
                    return redirect('student_dashboard')  # Redirect to student dashboard
            else:
                messages.error(request, "User profile not found.")
        else:
            error_message = 'Invalid email or password'
            return render(request, 'login_view.html', {'error_message': error_message})

    return render(request, 'login_view.html')





def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = email  # Use email as username
        first_name = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST['role']

        # Check if email or username already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Email or username already exists.")
            return render(request, 'signup.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Create a new user
        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, is_staff=True)

        # Create a user profile
        profile = UserProfile(user=user, role=role)
        profile.save()

        messages.success(request, "Account created successfully. You can now log in.")
        return redirect('login_view')

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login_view')
def teacher_dashboard(request):
    return render(request,'teacher_dashboard.html')

@login_required(login_url='login_view')
def student_dashboard(request):
    return render(request,'student_dashboard.html')


@login_required(login_url='login_view')
def profile(request):
    context = None
    try:
        context ={
       
        'user_profile': UserProfile.objects.get(user=request.user)
    }
    except Exception as e:
        print(e)
        messages.error(request, "User profile not found.")
    return render(request,'profile.html',context=context)





from django.shortcuts import render, redirect
from .models import UserProfile

def upload_profile(request):
    user = request.user
    
    if request.method == 'POST':
       
        # Retrieve data from the HTML form
        bio = request.POST.get('bio')
        picture = request.FILES.get('picture')
        phone = request.POST.get('phone')

        # Create a new UserProfile instance
        profile = UserProfile(user=request.user, bio=bio, picture=picture, phone=phone,role = request.user.userprofile.role)
        profile.save()

        return redirect('profile')  # Redirect to profile detail page
    else:
        return render(request, 'upload_profile.html',{'user':user})



@login_required(login_url='login_view')
def dashboard(request):
    if UserProfile.objects.filter(role = 'teacher'):
        return teacher_dashboard(request=request)
    elif UserProfile.objects.filter(role = 'student'):
        return student_dashboard(request=request)
    
    return redirect('index')




from django.shortcuts import render, redirect
from .models import UserProfile  # Assuming UserProfile is your model

def edit_profile(request):
    user = request.user
    profile = user.userprofile  # Assuming userprofile is a OneToOneField in your User model

    if request.method == 'POST':
        # Retrieve data from the HTML form
        bio = request.POST.get('bio')
        picture = request.FILES.get('picture')
        phone = request.POST.get('phone')

        # Update the existing profile instance
        profile.bio = bio
        profile.role = str(user)
        if picture:
            profile.picture = picture
        profile.phone = phone
        profile.save()

        return redirect('profile')  # Redirect to profile detail page
    else:
        return render(request, 'edit_profile.html', {'profile': profile})




from django.db import IntegrityError

def upload_book(request):
    user_profile = request.user.userprofile 
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        genre = request.POST.get('genre')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')
        soft_copy = request.FILES.get('soft_copy')
        youtube_link = request.POST.get('youtube_link')

        try:
            # Basic form validation (consider additional checks for file types and sizes)
            if not title or not author or not isbn or not cover_image or not soft_copy:
                raise ValueError('Please fill in all required fields and upload both cover image and soft copy.')

            book = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                genre=genre,
                description=description,
                cover_image=cover_image,
                soft_copy=soft_copy,
                youtube_link=youtube_link,
                published_by=user_profile
            )

            # Handle successful upload logic (e.g., confirmation message)
            messages.success(request, 'Book uploaded successfully!')
            return redirect('available_books')

        except IntegrityError:
            messages.error(request, 'This ISBN already exists. Please provide a unique ISBN.')
            return render(request, 'upload_book.html')

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'upload_book.html')

    else:
        return render(request, 'upload_book.html')




@login_required(login_url='login_view')
def available_books(request):
    user_profile = request.user.userprofile  # Assuming user profile is linked to User
    published_books = Book.objects.filter(published_by=user_profile)
    return render(request, 'available_books.html', {'published_books': published_books})


@login_required(login_url='login_view')
def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'book_details.html', {'book': book})


from django.shortcuts import get_object_or_404, redirect, render
from .models import Book

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.genre = request.POST.get('genre')
        book.description = request.POST.get('description')
        book.youtube_link = request.POST.get('youtube_link')

        if 'cover_image' in request.FILES:
            book.cover_image = request.FILES['cover_image']

        if 'soft_copy' in request.FILES:
            book.soft_copy = request.FILES['soft_copy']

        book.save()
        return redirect('book_details', book_id=book.id)

    return render(request, 'edit_book.html', {'book': book})


from django.shortcuts import get_object_or_404, redirect
from .models import Book

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('available_books')
