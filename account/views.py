from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import status
from .models import User, UserProfile

from .serializers import UserSerializer, UserProfileSerializer


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Сохраняем пользователя
            return JsonResponse({'auth_code': user.auth_code})
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeView(APIView):
    def get(self, request):
        return render(request, 'verify_code.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            auth_code = request.data.get('auth_code')
            try:
                user = User.objects.get(phone_number=phone_number, auth_code=auth_code)
                user.generate_invite_code()
                return JsonResponse({'message': 'Successfully verified code'})
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid phone number or authentication code'},
                                    status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    def get(self, request):
        phone_number = request.GET.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number)
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            referrals = user.referrals.all().values_list('phone_number', flat=True)
            serializer = UserProfileSerializer(user_profile)
            return render(request, 'profile.html', {'user': user, 'referrals': referrals, 'user_profile': user_profile})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class ActivateInviteCodeView(APIView):
    def get(self, request):
        return render(request, 'activate_invite.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            invite_code = request.data.get('invite_code')
            try:
                user = User.objects.get(phone_number=phone_number)
                referred_user = User.objects.get(invite_code=invite_code)
                user_profile, _ = UserProfile.objects.get_or_create(user=user)
                if user_profile.used_invite_code:
                    return JsonResponse({'error': 'User has already activated an invite code'},
                                        status=status.HTTP_400_BAD_REQUEST)
                user_profile.used_invite_code = invite_code
                user_profile.save()

                user.referred_by = referred_user
                user.save()

                return JsonResponse({'message': 'Invite code activated successfully'})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User or invitee does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
