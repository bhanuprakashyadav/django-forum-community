# Contains URL table routing
from django.urls import path
from . import views



# -------------------------------COME BACK AFTER WATCHING SYSTEM DESIGN ((ALL)) VIDEOS.-----------------------------




urlpatterns = [
    
    path('', views.index, name='index'), # use anywhere like, return redirect('/) will goes to index.html
    path('register/', views.register, name='register'),
    path('post_reply/', views.post_reply, name='post_reply'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/<str:username>/', views.dashboard_view, name='dashboard_view'),
    path('check_login/', views.check_login, name='check_login'), # check_login in index.html script for ajax
    path('create_post/', views.create_post, name='create_post'), # actual link to send for creating post
    path('post/<uuid:post_id>/', views.post, name='post'), #  <h2><a href="{% url 'post' post.post_id %}">{{ post.post_title }}</a></h2>
    path('post/<uuid:post_id>/reply/<int:reply_id>/delete/', views.views_delete_reply, name='delete_reply'),  # For deleting replies
    path('post/<uuid:post_id>/delete/', views.views_delete_post, name='delete_post'),
]