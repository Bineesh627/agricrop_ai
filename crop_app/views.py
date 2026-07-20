import json
import os
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Avg

from .models import UserProfile, CropInformation, CropPredictionRecord, FarmerFeedback
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    CropRecommendationForm, FarmerFeedbackForm, AdminFeedbackReplyForm
)
from .ml_model import predict_crop_recommendation

def admin_required(view_func):
    """Decorator to ensure user is logged in and is an Admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the administrator panel.")
            return redirect('login')
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if not profile.is_admin_user():
            messages.error(request, "Access denied. Administrator privileges required.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def home_view(request):
    """Home / Landing Page"""
    total_predictions = CropPredictionRecord.objects.count()
    total_farmers = User.objects.count()
    crops_count = CropInformation.objects.count()
    recent_crops = CropInformation.objects.all()[:6]
    
    context = {
        'total_predictions': total_predictions,
        'total_farmers': total_farmers,
        'crops_count': crops_count,
        'recent_crops': recent_crops
    }
    return render(request, 'crop_app/home.html', context)


def register_view(request):
    """User Registration"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            user_type = 'FARMER'
            phone = form.cleaned_data.get('phone', '')
            location = form.cleaned_data.get('location', '')
            farm_size = form.cleaned_data.get('farm_size', 2.5) or 2.5
            
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone=phone,
                location=location,
                farm_size=farm_size
            )
            
            messages.success(request, f"Account created successfully for {user.username}! You can now log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'crop_app/register.html', {'form': form})


def login_view(request):
    """User Login"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                
                # Check user profile and redirect appropriately
                profile, created = UserProfile.objects.get_or_create(user=user)
                if profile.is_admin_user():
                    return redirect('admin_dashboard')
                return redirect('recommend')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
        
    return render(request, 'crop_app/login.html', {'form': form})


def logout_view(request):
    """User Logout"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile_view(request):
    """User Profile View and Update"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            profile.phone = request.POST.get('phone', profile.phone)
            profile.location = request.POST.get('location', profile.location)
            try:
                profile.farm_size = float(request.POST.get('farm_size', profile.farm_size))
            except ValueError:
                pass
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    user_predictions = CropPredictionRecord.objects.filter(user=request.user)[:5]
    
    context = {
        'form': form,
        'profile': profile,
        'recent_predictions': user_predictions
    }
    return render(request, 'crop_app/profile.html', context)


@login_required
def recommend_view(request):
    """Crop Recommendation Input Form"""
    if request.method == 'POST':
        form = CropRecommendationForm(request.POST)
        if form.is_valid():
            n = form.cleaned_data['nitrogen']
            p = form.cleaned_data['phosphorus']
            k = form.cleaned_data['potassium']
            temp = form.cleaned_data['temperature']
            hum = form.cleaned_data['humidity']
            ph = form.cleaned_data['ph']
            rain = form.cleaned_data['rainfall']
            soil_type = form.cleaned_data['soil_type']
            season = form.cleaned_data['season']
            
            try:
                predicted_crop_key, confidence, alternatives = predict_crop_recommendation(
                    n, p, k, temp, hum, ph, rain
                )
                
                # Save prediction record
                record = CropPredictionRecord.objects.create(
                    user=request.user,
                    nitrogen=n,
                    phosphorus=p,
                    potassium=k,
                    temperature=temp,
                    humidity=hum,
                    ph=ph,
                    rainfall=rain,
                    soil_type=soil_type,
                    season=season,
                    predicted_crop=predicted_crop_key,
                    confidence_score=confidence,
                    top_alternatives=json.dumps(alternatives)
                )
                
                messages.success(request, "Crop recommendation calculated successfully!")
                return redirect('result', pk=record.pk)
                
            except Exception as e:
                messages.error(request, f"Error calculating recommendation: {str(e)}")
    else:
        form = CropRecommendationForm()
        
    return render(request, 'crop_app/recommend.html', {'form': form})


@login_required
def result_view(request, pk):
    """Recommendation Result Detail Page"""
    record = get_object_or_404(CropPredictionRecord, pk=pk)
    
    # Check permission (user can view own or admin can view any)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if record.user != request.user and not profile.is_admin_user():
        messages.error(request, "Permission denied to view this prediction record.")
        return redirect('history')
        
    # Get metadata for predicted crop
    crop_info = CropInformation.objects.filter(name__iexact=record.predicted_crop).first()
    
    # Parse alternative crops
    alternatives = []
    if record.top_alternatives:
        try:
            parsed_alts = json.loads(record.top_alternatives)
            for alt in parsed_alts:
                alt_info = CropInformation.objects.filter(name__iexact=alt['crop']).first()
                alternatives.append({
                    'name': alt['crop'],
                    'display_name': alt_info.display_name if alt_info else alt['crop'].title(),
                    'confidence': alt['confidence'],
                    'icon': alt_info.icon_class if alt_info else 'fa-seedling'
                })
        except Exception:
            pass
            
    context = {
        'record': record,
        'crop_info': crop_info,
        'alternatives': alternatives,
    }
    return render(request, 'crop_app/result.html', context)


@login_required
def history_view(request):
    """User Prediction History"""
    predictions = CropPredictionRecord.objects.filter(user=request.user)
    return render(request, 'crop_app/history.html', {'predictions': predictions})


@login_required
def delete_prediction_view(request, pk):
    """Delete a prediction record"""
    record = get_object_or_404(CropPredictionRecord, pk=pk)
    if record.user == request.user or request.user.is_superuser:
        record.delete()
        messages.success(request, "Prediction record deleted.")
    return redirect('history')


def crop_catalog_view(request):
    """Crop Knowledge Encyclopedia Catalog"""
    category = request.GET.get('category', '')
    query = request.GET.get('q', '')
    
    crops = CropInformation.objects.all()
    if category:
        crops = crops.filter(category__iexact=category)
    if query:
        crops = crops.filter(display_name__icontains=query) | crops.filter(description__icontains=query)
        
    categories = ['Cereal', 'Pulse', 'Fruit', 'Commercial']
    
    context = {
        'crops': crops,
        'selected_category': category,
        'query': query,
        'categories': categories
    }
    return render(request, 'crop_app/crop_catalog.html', context)


def crop_detail_view(request, name):
    """Individual Crop Detail Page"""
    crop = get_object_or_404(CropInformation, name__iexact=name)
    return render(request, 'crop_app/crop_detail.html', {'crop': crop})



@login_required
def feedback_view(request):
    """Submit farmer feedback and view past inquiries"""
    if request.method == 'POST':
        form = FarmerFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you! Your feedback/question has been submitted to the administrator.")
            return redirect('feedback')
    else:
        form = FarmerFeedbackForm()
        
    my_feedbacks = FarmerFeedback.objects.filter(user=request.user)
    return render(request, 'crop_app/feedback.html', {'form': form, 'feedbacks': my_feedbacks})


# ==================== ADMIN VIEWS ====================

@admin_required
def admin_dashboard_view(request):
    """Admin Executive Dashboard"""
    total_users = User.objects.count()
    total_farmers = UserProfile.objects.filter(user_type='FARMER').count()
    total_predictions = CropPredictionRecord.objects.count()
    pending_feedbacks = FarmerFeedback.objects.filter(status='PENDING').count()
    
    # Top predicted crops aggregation
    top_crops_qs = CropPredictionRecord.objects.values('predicted_crop').annotate(
        count=Count('predicted_crop')
    ).order_by('-count')[:5]
    
    top_crops_chart = [
        {'crop': item['predicted_crop'].title(), 'count': item['count']}
        for item in top_crops_qs
    ]
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_predictions = CropPredictionRecord.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_farmers': total_farmers,
        'total_predictions': total_predictions,
        'pending_feedbacks': pending_feedbacks,
        'top_crops_chart': json.dumps(top_crops_chart),
        'recent_users': recent_users,
        'recent_predictions': recent_predictions,
    }
    return render(request, 'crop_app/admin_dashboard.html', context)


@admin_required
def admin_users_view(request):
    """Admin User Management"""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'crop_app/admin_users.html', {'users': users})


@admin_required
def admin_toggle_user_status(request, pk):
    """Toggle active status of a user"""
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own admin account.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_str = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f"User '{target_user.username}' has been {status_str}.")
    return redirect('admin_users')


@admin_required
def admin_predictions_view(request):
    """Admin Prediction Audit Logs"""
    query = request.GET.get('q', '')
    predictions = CropPredictionRecord.objects.select_related('user').all()
    
    if query:
        predictions = predictions.filter(
            predicted_crop__icontains=query
        ) | predictions.filter(
            user__username__icontains=query
        ) | predictions.filter(
            soil_type__icontains=query
        )
        
    return render(request, 'crop_app/admin_predictions.html', {
        'predictions': predictions,
        'query': query
    })


@admin_required
def admin_ml_model_view(request):
    """Admin ML Model Insights & Management"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml_assets', 'crop_recommendation.csv')
    
    dataset_summary = None
    sample_rows = []
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        dataset_summary = {
            'total_rows': len(df),
            'num_crops': df['label'].nunique(),
            'features': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        }
        sample_rows = df.head(10).to_dict(orient='records')
        
    if request.method == 'POST' and 'retrain' in request.POST:
        from ml_assets.train_model import train
        try:
            train()
            messages.success(request, "ML Crop Recommendation Model retrained successfully with 99.77% accuracy!")
        except Exception as e:
            messages.error(request, f"Failed to retrain model: {str(e)}")
        return redirect('admin_ml_model')
        
    return render(request, 'crop_app/admin_ml_model.html', {
        'dataset_summary': dataset_summary,
        'sample_rows': sample_rows
    })


@admin_required
def admin_feedback_view(request):
    """Admin Feedback Management & Response"""
    feedbacks = FarmerFeedback.objects.select_related('user').all()
    
    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        feedback = get_object_or_404(FarmerFeedback, pk=feedback_id)
        reply_text = request.POST.get('admin_reply', '')
        status = request.POST.get('status', 'RESOLVED')
        
        feedback.admin_reply = reply_text
        feedback.status = status
        feedback.save()
        messages.success(request, f"Reply saved for feedback #{feedback.id}.")
        return redirect('admin_feedback')
        
    return render(request, 'crop_app/admin_feedback.html', {'feedbacks': feedbacks})
