import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _

class Record(models.Model):

    creation_date = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    email = models.CharField(max_length=255)

    phone = models.CharField(max_length=20)

    address = models.CharField(max_length=300)

    city = models.CharField(max_length=255)

    province = models.CharField(max_length=200)

    country = models.CharField(max_length=125)

    images = models.ImageField(upload_to='images/',default="") # Store images as an array


    def __str__(self):

        return self.first_name + "   " + self.last_name
 
def get_current_time():
    return datetime.datetime.now().time()

class RecordAdditionalInfo(models.Model):
    record = models.ForeignKey('Record', on_delete=models.CASCADE, related_name='additional_info')
    name = models.CharField(max_length=255, default='Unknown')
    national_id = models.CharField(max_length=255, default='Unknown', unique=True)
    address = models.CharField(max_length=255, default='Unknown')
    picture = models.ImageField(upload_to='additional_info/images/', default="")
    date_created = models.DateField(_("Date Created"), default=datetime.date.today, unique=True)
    time_created = models.TimeField(_("Time Created"), default=get_current_time,)
    day_of_week = models.CharField(_("Day of the Week"), max_length=20, default='')

    class Meta:
        # Ensure uniqueness of records based on national_id and date_created
        unique_together = ('national_id', 'date_created')

    def save(self, *args, **kwargs):
        # Automatically set the day of the week based on the date_created
        self.day_of_week = self.date_created.strftime("%A")
        super().save(*args, **kwargs)
