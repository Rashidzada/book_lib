from django.urls import path

from . import views
urlpatterns = [
    path('',views.index , name= 'index'),
    path('contact/',views.contact, name= 'contact'),
    path('about/',views.about,name='about'),
    path('book/',views.book,name='book'),
    path('forum/',views.forum,name='forum'),
    path('singup/',views.signup,name='signup'),
    path('login_view/',views.login_view,name='login_view'),
    path('prifile/',views.profile,name='profile'),
    path('logout_view/',views.logout_view,name='logout_view'),
    path('upload_profile/',views.upload_profile,name='upload_profile'),
    path('edit_profile',views.edit_profile,name = 'edit_profile'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('upload_book',views.upload_book,name='upload_book'),
    path('available_books/',views.available_books,name='available_books'),
    path('books/<int:book_id>/', views.book_details, name='book_details'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('request_book/<int:book_id>/', views.request_book, name='request_book'),
    path('student_requests/',views.student_requests,name='student_requests'),
    path('view_requests/', views.view_requests, name='view_requests'),
    path('approve_request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('thankyou/',views.thankyou,name= 'thankyou')

]

