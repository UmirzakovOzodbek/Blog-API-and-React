from django.urls import path
from .views import (
    CustomUserCreate,
    SendEmailVerificationCodeView,
    CheckEmailVerificationCodeView,
    CheckEmailVerificationCodeWithParams
)

app_name = 'users'

urlpatterns = [
    path('create/', CustomUserCreate.as_view(), name="create_user"),
    path("email/verification/", SendEmailVerificationCodeView.as_view(), name="send-email-code"),
    path("email/check-verification/", CheckEmailVerificationCodeView.as_view(), name="check-email-code"),
    path("email/check-verification-code/", CheckEmailVerificationCodeWithParams.as_view(), name="check-email"),
]



