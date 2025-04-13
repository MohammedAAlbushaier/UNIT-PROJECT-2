from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('campaigns/', views.campaign_list, name='campaigns'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/new/', views.campaign_create, name='campaign_create'),
    path('campaigns/<int:pk>/edit/', views.campaign_update, name='campaign_update'),
    path('campaigns/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('campaigns/<int:pk>/donate/', views.donate, name='campaign_donate'),
    path('signup/', views.signup, name='signup'),
    path('donate/', views.donate, {'pk': None}, name='donate'),
    path('profile/', views.profile, name='profile'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('donate/', views.general_donate, name='donate'),
]
