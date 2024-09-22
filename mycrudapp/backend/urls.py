
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('post_reply/', views.post_reply, name='post_reply'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/<str:username>/', views.dashboard_view, name='dashboard_view'),
    path('check_login/', views.check_login, name='check_login'),
    path('create_post/', views.create_post, name='create_post'),
    path('post/<uuid:post_id>/', views.post, name='post'),
    path('post/<uuid:post_id>/reply/<int:reply_id>/delete/',
         views.views_delete_reply, name='delete_reply'),
    path('post/<uuid:post_id>/delete/',
         views.views_delete_post, name='delete_post'),
]
