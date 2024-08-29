from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .forms import SignUpForm, LoginForm
from django.db import IntegrityError
from .models import *
from .utils.upload_to_supabase import upload_file_to_supabase
from django.conf import settings
from rest_framework import status
import re
from django.contrib.auth.hashers import make_password
# Create your views here.

@api_view(['POST'])
def signup_view(request):
    if request.method == 'POST':
        data = request.data
        
        print(data)
        name = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password1 = data.get('password1')
        password2 = data.get('password2')
        user_type = data.get('user_type')
        
        # Validate data
        if not name or not email or not phone_number or not password1 or not password2 or not user_type:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if password1 != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the user already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the user
        try:
            user = User(
                username=name,
                email=email,
                phone_number=phone_number,
                password=make_password(password1),  # Ensure the password is hashed
                user_type=user_type
            )
            user.save()
            print("done")
            
            # Generate tokens (assuming you have JWT setup)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            print(f"Database error: {e}")
            return Response({"error": "Database error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@api_view(['POST'])
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def upload_verification_docs(request):
    if request.method == 'POST':
        user = request.user
        addhar_file = request.FILES.get('addhar_card')
        pan_card_file = request.FILES.get('pan_card')

        # Upload files to Supabase
        addhar_file_path = f"addhar/{addhar_file.name}"
        pan_card_file_path = f"pan-card/{pan_card_file.name}"

        addhar_upload_path = upload_file_to_supabase(addhar_file, settings.SUPABASE_BUCKET, addhar_file_path)
        pan_upload_path = upload_file_to_supabase(pan_card_file, settings.SUPABASE_BUCKET, pan_card_file_path)

        # Save the paths in the model instance
        verification_doc = VerificationDocs.objects.create(
            user=user,
            addhar_card=addhar_upload_path,
            pan_card=pan_upload_path
        )
        verification_doc.save()

        return redirect('success_url')

    return render(request, 'upload_docs.html')
