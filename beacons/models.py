import datetime
from django.contrib.postgres.fields import ArrayField

from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class BeaconUserUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=BeaconUserUserManager.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,
                                password=password
                                )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class BeaconUser(AbstractBaseUser, PermissionsMixin):
    image = models.ImageField(upload_to='images/user', blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)

    objects = BeaconUserUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.email

    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.email

    def __unicode__(self):
        return self.email

    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin

    def is_authenticated(self):
        return True


class TimestampMixin(object):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Campaign(models.Model, TimestampMixin):
    name = models.CharField(max_length=100, blank=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='campaigns')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def is_active_campaign(self):
        return self.is_active and self.start_date < timezone.now() < self.end_date


class Beacon(models.Model):
    title = models.CharField(max_length=100, blank=False)
    campaign = models.ForeignKey('Campaign', related_name='beacons', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='beacons', blank=True, null=True)
    shop = models.ForeignKey('Shop', related_name='beacons', blank=True, null=True)
    minor = models.IntegerField(default=1)
    major = models.IntegerField(default=1)
    UUID = models.CharField(max_length=36, default='00000000-0000-0000-0000-000000000000')

    def __str__(self):
        return self.title


ad_choices = {
    (0, 'full_width_image_only'),
    (1, 'full_width_image_With_content'),
    (2, 'left_image_With_content'),
}


class Ad(models.Model):
    type = models.IntegerField(default=0, choices=ad_choices)
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    campaign = models.ForeignKey('Campaign', related_name='ads')
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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='shops', choices=DAYS_OF_WEEK)
    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=200, blank=False)
    latitude = models.FloatField(default=50.044328, blank=True, null=True)
    longitude = models.FloatField(default=19.952527, blank=True, null=True)
    image = models.ImageField(upload_to='images/shops', blank=True, null=True)


class OpeningHours(models.Model):
    days = ArrayField(models.IntegerField(), size=7)
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    shop = models.ForeignKey('Shop', related_name='opening_hours')


class Promotion(models.Model):
    title = models.CharField(max_length=100, blank=False)
    points = models.IntegerField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/promotions', blank=True, null=True)
    campaign = models.ForeignKey('Campaign', related_name='promotions')


class Scenario(models.Model):
    pass


award_choices = {
    (0, 'no_image'),
    (1, 'full_width_image_With_content'),
    (2, 'left_image_With_content'),
}


class Award(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    points = models.IntegerField(blank=True)
    image = models.ImageField(upload_to='images/awards', blank=True, null=True)
    campaign = models.ForeignKey('Campaign', related_name='awards')
    type = models.IntegerField(default=0, choices=award_choices)


class UserAwards(models.Model):
    award = models.ForeignKey(Award, related_name='details')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_awards')
    favorite = models.BooleanField(default=False)
    bought = models.BooleanField(default=False)

    class Meta:
        unique_together = ('award', 'user',)


class ActionBeacon(models.Model):
    campaign = models.ForeignKey('Campaign', related_name='actions', blank=True, null=True)
    beacon = models.ForeignKey('Beacon', blank=True, null=True, related_name='actions')
    ad = models.ForeignKey('Ad', blank=True, null=True, related_name='actions')
    points = models.IntegerField(default=0)
    time_limit = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ('beacon', 'ad', 'campaign')


class UserCampaign(models.Model, TimestampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_campaign')
    campaign = models.ForeignKey('Campaign', related_name='user_details')
    user_points = models.IntegerField(default=0)

    class Meta:
        unique_together = ('campaign', 'user',)
