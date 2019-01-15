from django.db import models
from django.contrib.postgres.fields import JSONField


class UserData(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    password = models.CharField(max_length=200, null=False, blank=False)
    current_post_count = models.IntegerField(default=0)
    current_like_count = models.IntegerField(default=0)
    additional_information = JSONField(null=True, blank=True)

    def __str__(self):
        return 'Name: %s, Email: %s, Post: %s, Like: %s, Password: %s' % (
            self.name, self.email, self.current_post_count, self.current_like_count, self.password)


class PostData(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=200, null=False, blank=False)
    like_count = models.IntegerField(default=0)
    owner = models.ForeignKey(UserData, related_name='posts', on_delete=models.CASCADE)

    def __str__(self):
        return 'Like: %s, Owner: %s' % (self.like_count, self.owner.name)
