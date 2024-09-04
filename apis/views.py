from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import SignUpForm, LoginForm
from django.db import IntegrityError
from .models import *
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import re
from django.contrib.auth.hashers import make_password
from django.utils.text import get_valid_filename

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
    email = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': user.user_type,
        })
    else:
        return Response({'error': 'Invalid email or password.'}, status=400)


@api_view(['POST'])
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from supabase import create_client

def generate_presigned_url(file_name):
    # Initialize Supabase client
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY
    supabase = create_client(supabase_url, supabase_key)

    # Generate presigned URL
    bucket_name = settings.SUPABASE_BUCKET
    file_path = f"uploads/{file_name}"
    response = supabase.storage.from_(bucket_name).create_signed_upload_url(file_path)

    if response.get('error'):
        raise Exception(f"Error generating presigned URL: {response['error']['message']}")

    return response['data']

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_verification_docs(request):
    if request.user.user_type == User.FARMER:
        user = request.user
        addhar_file = request.FILES.get('addhar_card')
        pan_card_file = request.FILES.get('pan_card')
        saat_baar_copy = request.FILES.get('saat_baar_copy')

        if not addhar_file or not pan_card_file or not saat_baar_copy:
            return Response({"error": "All files are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Define file paths
        addhar_file_path = f"{user.username}/addhar/{addhar_file.name}"
        pan_card_file_path = f"{user.username}/pan-card/{pan_card_file.name}"
        saat_baar_copy_path = f"{user.username}/saat-baar-copy/{saat_baar_copy.name}"

        # Save files to the default storage
        addhar_file_url = default_storage.save(addhar_file_path, ContentFile(addhar_file.read()))
        pan_card_file_url = default_storage.save(pan_card_file_path, ContentFile(pan_card_file.read()))
        saat_baar_copy_url = default_storage.save(saat_baar_copy_path, ContentFile(saat_baar_copy.read()))

        # Create or update the FarmerVerificationDocs model
        verification_doc = FarmerVerificationDocs.objects.create(
            user=user,
            addhar_card=addhar_file_url,
            pan_card=pan_card_file_url,
            satbaarcopy=saat_baar_copy_url
        )

        return Response({"message": "Documents uploaded successfully."}, status=status.HTTP_201_CREATED)
    elif request.user.user_type == User.CONSUMER:
        return Response({"message": "You are not supposed to be here"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_verification_docs(request):
    # Check if the user is a consumer
    if request.user.user_type == User.CONSUMER:
        user = request.user
        addhar_file = request.FILES.get('addhar_card')
        pan_card_file = request.FILES.get('pan_card')

        # Ensure both files are provided
        if not addhar_file or not pan_card_file:
            return Response({"error": "Both Aadhar card and PAN card files are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Define file paths with secure filenames
        addhar_file_path = f"{user.username}/addhar/{get_valid_filename(addhar_file.name)}"
        pan_card_file_path = f"{user.username}/pan-card/{get_valid_filename(pan_card_file.name)}"

        # Save files to the default storage
        try:
            addhar_file_url = default_storage.save(addhar_file_path, ContentFile(addhar_file.read()))
            pan_card_file_url = default_storage.save(pan_card_file_path, ContentFile(pan_card_file.read()))

            # Create or update the ConsumerVerificationDocs model
            verification_doc, created = ConsumerVerificationDocs.objects.update_or_create(
                user=user,
                defaults={
                    'addhar_card': addhar_file_url,
                    'pan_card': pan_card_file_url
                }
            )

            return Response({"message": "Documents uploaded successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle exceptions, such as file storage errors
            return Response({"error": f"Failed to upload documents: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.user.user_type == User.FARMER:
        # Return 403 Forbidden if the user is not allowed to perform this action
        return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    # Return 400 Bad Request for any other user types
    return Response({"message": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)