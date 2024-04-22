from django.urls import path
from .views import LoginView, VerifyCodeView, UserProfileView, ActivateInviteCodeView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('verify_code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('activate_invite_code/', ActivateInviteCodeView.as_view(), name='activate_invite_code'),
]
