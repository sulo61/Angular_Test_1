from django.contrib.postgres.fields import ArrayField
from django.db import models


class TimestampMixin(object):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Campaign(models.Model, TimestampMixin):
    name = models.CharField(max_length=100, blank=False)
    owner = models.ForeignKey('auth.User', related_name='campaigns')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.name


class Beacon(models.Model):
    title = models.CharField(max_length=100, blank=False)
    user = models.ForeignKey('auth.User', related_name='beacons')
    campaign = models.ForeignKey('Campaign', related_name='beacons', blank=True, null=True)

    def __str__(self):
        return self.title


class Ad(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    campaign = models.ForeignKey('Campaign', related_name='adds')
    image = models.ImageField(upload_to='images/ads', blank=True, null=True)


DAYS_OF_WEEK = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
    (7, 'Sunday'),
)


class Shop(models.Model):
    owner = models.ForeignKey('auth.User', related_name='shops', choices=DAYS_OF_WEEK)
    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=200, blank=False)


class OpeningHours(models.Model):
    days = ArrayField(models.IntegerField(), size=7)
    open_time = models.TimeField(blank=True)
    close_time = models.TimeField(blank=True)
    shop = models.ForeignKey('Shop', related_name='opening_hours')


class Promotion(models.Model):
    title = models.CharField(max_length=100, blank=False)
    points = models.IntegerField(blank=True)
    description = models.TextField(blank=True)


class Scenario(models.Model):
    pass


class Award(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    points = models.IntegerField(blank=True)
