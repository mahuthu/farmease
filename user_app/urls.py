from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('farmer/register/', views.farmer_registration_view, name='farmer_register'),
    path('processor/register/', views.processor_registration_view, name='processor_register'),
    path('farmer/dashboard/', views.farmer_dashboard_view, name='farmer_dashboard'),  # Redirect for farmer after registration
    path('processor/dashboard/', views.processor_dashboard_view, name='processor_dashboard'),  # Redirect for processor after registration
    path('register/', views.registration_view, name='register'),
    path('api/get_product_services/', views.get_product_services, name='get_product_services'),
    path('logout', views.logout_view, name="logout"),
    path("choose_role/", views.choose_role_view, name="choose_role"),

]