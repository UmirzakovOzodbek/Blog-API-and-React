from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import VerificationCode
from .serializers import CustomUserSerializer, CheckEmailVerificationCodeSerializer, SendEmailVerificationCodeSerializer
from rest_framework.permissions import AllowAny


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendEmailVerificationCodeView(APIView):

    @swagger_auto_schema(request_body=SendEmailVerificationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendEmailVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        code = get_random_string(allowed_chars="0123456789", length=6)
        verification_code, _ = (
            VerificationCode.objects.update_or_create(email=email, defaults={"code": code, "is_verified": False})
        )
        verification_code.expired_at = verification_code.last_sent_time + timedelta(seconds=30)
        verification_code.save(update_fields=["expired_at"])
        subject = "Email registration"
        # message = f"Your email verification code {code}"
        verification_email_url = reverse("check-email")
        message = f"Click to confirm email:\n " \
                  f"http://localhost:8000{verification_email_url}?email={email}&code={code}"
        send_mail(
            subject, message, from_email=settings.EMAIL_HOST_USER, recipient_list=[email]
        )
        return Response({"detail": "Successfully sent email verification code."})


class CheckEmailVerificationCodeView(CreateAPIView):
    queryset = VerificationCode.objects.all()
    serializer_class = CheckEmailVerificationCodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        code = serializer.validated_data.get("code")
        verification_code = self.get_queryset().filter(email=email, is_verified=False).order_by(
            "-last_sent_time").first()
        if verification_code and verification_code.code != code and verification_code.is_expire:
            raise ValidationError("Verification code invalid.")
        verification_code.is_verified = True
        verification_code.save(update_fields=["is_verified"])
        return Response({"detail": "Verification code is verified."})


class CheckEmailVerificationCodeWithParams(APIView):

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        code = request.query_params.get("code")
        verification_code = (
            VerificationCode.objects.filter(email=email, is_verified=False).order_by("-last_sent_time").first()
        )
        if verification_code and verification_code.code != code:
            raise ValidationError("Verification code invalid.")
        verification_code.is_verified = True
        verification_code.save(update_fields=["is_verified"])
        return Response({"detail": "Verification code is verified."})



