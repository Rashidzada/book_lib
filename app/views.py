
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required


def index(request):
    context = {
        'books':Book.objects.all().order_by('-id')
    }
    return render(request,'index.html',context)


def contact(request):
    return render(request,'contact.html')


def about(request):
    return render(request,'about.html')


def book(request):
    context = {
        'books':Book.objects.all().order_by('-id')
    }
    return render(request,'book.html',context)

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
                    return redirect('dashboard')  # Redirect to teacher dashboard
                else:
                    return redirect('dashboard')  # Redirect to student dashboard
            else:
                messages.error(request, "User profile not found.")
        else:
            error_message = 'Invalid email or password'
            return render(request, 'login_view.html', {'error_message': error_message})

    return render(request, 'login_view.html')


def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST['role']

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Create a new user
        user = User.objects.create_user(username=email, email=email, password=password, is_staff=True,first_name = username)

        # Create a user profile with the role
        profile = UserProfile(user=user, role=role)
        profile.save()

        messages.success(request, "Account created successfully. You can now log in.")
        return redirect('login_view')

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('index')

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

def upload_profile(request):
    user = request.user
    
    if request.method == 'POST':
        # Retrieve data from the HTML form
        bio = request.POST.get('bio')
        picture = request.FILES.get('picture')
        phone = request.POST.get('phone')

        # Check if the user already has a UserProfile instance
        if hasattr(user, 'userprofile'):
            # Update the existing UserProfile instance
            profile = user.userprofile
            profile.bio = bio
            profile.picture = picture
            profile.phone = phone
            profile.save()
        else:
            # Create a new UserProfile instance
            profile = UserProfile(user=user, bio=bio, picture=picture, phone=phone)
            profile.save()

        return redirect('profile')  # Redirect to profile detail page
    else:
        return render(request, 'upload_profile.html', {'user': user})

@login_required(login_url='login_view')
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    role = user_profile.role
    bio = user_profile.bio
    picture_url = user_profile.picture if user_profile.picture else None
    phone = user_profile.phone

    return render(request, 'dashboard.html', {'role': role, 'bio': bio, 'picture_url': picture_url, 'phone': phone})


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
        if picture:
            profile.picture = picture
        profile.phone = phone
        profile.save()

        return redirect('profile')  # Redirect to profile detail page
    else:
        return render(request, 'edit_profile.html', {'profile': profile})


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
    user_profile = request.user.userprofile
    if user_profile.role == 'student':
         
        published_books = Book.objects.all().order_by('-id')
        
    else:
        published_books = Book.objects.filter(published_by=user_profile)
    return render(request, 'available_books.html', {'published_books': published_books})

@login_required(login_url='login_view')
def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'book_details.html', {'book': book})

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

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('available_books')


@login_required(login_url='login_view')
def request_book(request, book_id):
   
    book = get_object_or_404(Book, pk=book_id)
    # Check if the student has already requested the book
    existing_request = Request.objects.filter(student=request.user, book=book).exists()
    if existing_request:
        # Inform the user about the duplicate request
        messages.info(request, 'You have already requested this book.')
        return redirect('student_requests')  # Redirect to the student requests page
    if request.method == 'POST':
        request_obj = Request(student=request.user, book=book)
        request_obj.save()
        messages.success(request, 'Book request successful!')
        return redirect('student_requests')  # Redirect to the student requests page

    return render(request, 'request_book.html', {'book': book})


def student_requests(request):
    # Fetch all book requests made by students
    student_requests = Request.objects.filter(student=request.user)
    context = {
        'student_requests': student_requests,
    }
    return render(request, 'student_requests.html', context)



def view_requests(request):
    pending_requests = Request.objects.filter(status='pending')
    return render(request, 'view_requests.html', {'requests': pending_requests})

def approve_request(request, request_id):
    if request.method == "POST":
        status = request.POST['status']
        request_instance = Request.objects.get(pk=request_id)
        request_instance.status = status
        request_instance.save()
    return redirect('view_requests')



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Forum

def forum(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Forum.objects.create(user=request.user, title=title, content=content)
            messages.success(request, 'Your feedback was sent. Thank you!')
            return redirect('forum')
        else:
            messages.error(request, 'Please provide both title and content.')
    
    # Fetch all forum posts
    all_posts = Forum.objects.all().order_by('-created_at')  # Order by creation date, newest first

    return render(request, 'forum.html', {'all_posts': all_posts})




def contact(request):
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            # Create and save the contact instance
            contact = Contact(name=name, email=email, subject=subject, message=message)
            contact.save()

            # Success message
            messages.success(request, "Your message has been sent successfully!")
            return redirect('thankyou')
        except Exception as e:
            # Log the error if necessary (e.g., with logging module)
            # Error message for the user
            messages.error(request, "An error occurred while sending your message. Please try again.")
    else:
        # Warning message if the request method is not POST
        messages.warning(request, "Your message request was not sent. Please try again using the form.")

    return render(request, 'contact.html')



def thankyou(request):
    return render(request,'thankyou.html')