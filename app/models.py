from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from embed_video.fields import EmbedVideoField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to='profile_pics', blank=True)
    phone = models.CharField(blank=True, null=True, default='00000', max_length=15)

    def __str__(self):
        return f"{str(self.user.username)} - {str(self.role)}"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)  # Assuming teacher enters author's name
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    available_copies = models.PositiveIntegerField(default=0)
    total_copies = models.PositiveIntegerField(default=0)
    cover_image = models.ImageField(upload_to='book_covers', blank=True, null=True)
    soft_copy = models.FileField(upload_to='book_soft_copies', blank=True, null=True)
    youtube_link = EmbedVideoField(blank=True,null=True)
    published_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='published_books')  # Restrict publishing to teachers

    def __str__(self):
        return f'{str(self.title)} Written By {str(self.author)} publich by {str(self.published_by)}'

class Shelf(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    # Consider adding a location field (e.g., Dewey Decimal Classification) for more detailed organization
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='assigned_books')  # Track student assigned to the book

    def __str__(self):
        return f"{self.book.title} (ISBN: {self.book.isbn}) - Assigned to: {self.assigned_to}"  # Display assigned student


class Request(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.book} ({self.status})"


from django.db import models
from django.contrib.auth.models import User

class Forum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Loan(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE)
    loaned_date = models.DateTimeField(blank=True, null=True)
    returned_date = models.DateTimeField(blank=True, null=True)

    def is_overdue(self):
        if self.loaned_date and self.due_date:
            today = datetime.now()
            return today > self.due_date
        return False

    def calculate_overdue_fine(self):
        if self.is_overdue():
            overdue_days = (datetime.now() - self.due_date).days
            return overdue_days * 10  # Fine of 10 PKR per day
        return 0

    def __str__(self):
        return f"{self.request.student} - {self.request.book} (Loaned: {self.loaned_date}, Returned: {self.returned_date})"


# Function to automatically update Loan status and calculate fines upon return
def handle_book_return(loan):
    loan.returned_date = datetime.now()
    loan.save()

    # Calculate and potentially store the overdue fine
    overdue_fine = loan.calculate_overdue_fine()
    # Consider creating a separate Fine model

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"




from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
# Signal to delete associated files when a model instance is deleted
@receiver(post_delete, sender=UserProfile)
@receiver(post_delete, sender=Book)
@receiver(post_delete, sender=Shelf)
@receiver(post_delete, sender=Request)
@receiver(post_delete, sender=Loan)
def delete_associated_files(sender, instance, **kwargs):
    # Define the paths to the files you want to delete
    if sender == UserProfile:
        if instance.picture:
            if os.path.isfile(instance.picture.path):
                os.remove(instance.picture.path)
    elif sender == Book:
        if instance.cover_image:
            if os.path.isfile(instance.cover_image.path):
                os.remove(instance.cover_image.path)
        if instance.soft_copy:
            if os.path.isfile(instance.soft_copy.path):
                os.remove(instance.soft_copy.path)
    elif sender == Shelf:
        # Handle deletion of associated files for Shelf if needed
        pass
    elif sender == Request:
        # Handle deletion of associated files for Request if needed
        pass
    elif sender == Loan:
        # Handle deletion of associated files for Loan if needed
        pass


