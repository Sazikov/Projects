from django.db import models


class UsersInfo(models.Model):
    user_surname = models.CharField(max_length=63, default='')
    user_name = models.CharField(max_length=63, default='')
    user_name2 = models.CharField(max_length=63, default='')
    date_birth = models.DateField(db_index=True, null=True, default=None)
    comment = models.CharField(max_length=511, default='')
    time_create = models.DateTimeField(auto_now_add=True)
