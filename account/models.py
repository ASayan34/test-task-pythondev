import random
import string
from django.db import models


class User(models.Model):
    phone_number = models.CharField(max_length=30, unique=True)
    auth_code = models.CharField(max_length=4, null=True)
    invite_code = models.CharField(max_length=6, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='referrals')

    def generate_invite_code(self):
        if not self.invite_code:
            self.invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    used_invite_code = models.CharField(max_length=6, null=True)
