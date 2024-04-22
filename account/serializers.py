import random
import string

from rest_framework import serializers
from .models import User, UserProfile


def phone_number_validate(phone_number):
    if phone_number is None or phone_number.strip() == "":
        raise serializers.ValidationError("Phone number cannot be empty or null")
    return phone_number


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[phone_number_validate])

    class Meta:
        model = User
        fields = '__all__'

    def validate_phone_number(self, value):
        return phone_number_validate(value)

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        user, created = User.objects.get_or_create(phone_number=phone_number)
        if created:
            user.auth_code = ''.join(random.choices(string.digits, k=4))
            user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
