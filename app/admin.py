from django.contrib import admin
from .import models
from .models import Contact
from django.core.mail import send_mail
from Book_lib import settings
# Register your models here.
admin.site.register([models.UserProfile,models.Book,models.Loan,models.Request,models.Shelf,models.Forum])




@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'responded', 'response')
    list_filter = ('responded',)
    search_fields = ('email', 'subject')
    actions = ['mark_as_responded']

    def mark_as_responded(self, request, queryset):
        queryset.update(responded=True)
    mark_as_responded.short_description = "Mark selected messages as responded"

    def save_model(self, request, obj, form, change):
        if 'response' in form.changed_data:
            # Here you can integrate the logic to send an email to the user
            subject = f"Response to your message: {obj.subject}"
            message = f"Dear {obj.name},\n\nWe have responded to your message From JobLink:\n\n{obj.response}"
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [obj.email]
            
            # Send email
            send_mail(subject, message, email_from, recipient_list)
        super().save_model(request, obj, form, change)
