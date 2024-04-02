from django.contrib import admin

# Register your models here.

from . models import Record,RecordAdditionalInfo

admin.site.register(Record)
admin.site.register(RecordAdditionalInfo)

