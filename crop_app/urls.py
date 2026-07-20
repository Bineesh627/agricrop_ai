from django.urls import path
from . import views

urlpatterns = [
    # Public & Auth Routes
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Farmer / User Routes
    path('recommend/', views.recommend_view, name='recommend'),
    path('result/<int:pk>/', views.result_view, name='result'),
    path('history/', views.history_view, name='history'),
    path('history/delete/<int:pk>/', views.delete_prediction_view, name='delete_prediction'),
    path('catalog/', views.crop_catalog_view, name='crop_catalog'),
    path('crop/<str:name>/', views.crop_detail_view, name='crop_detail'),
    path('feedback/', views.feedback_view, name='feedback'),
    
    # Admin Control Panel Routes
    path('admin-panel/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/users/toggle/<int:pk>/', views.admin_toggle_user_status, name='admin_toggle_user'),
    path('admin-panel/predictions/', views.admin_predictions_view, name='admin_predictions'),
    path('admin-panel/ml-model/', views.admin_ml_model_view, name='admin_ml_model'),
    path('admin-panel/feedback/', views.admin_feedback_view, name='admin_feedback'),
]
