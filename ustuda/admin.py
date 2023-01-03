from django.contrib import admin
from .models import Comments,Comments_Holder, Announcements, Payment_Information, Courses,Profile, Skills, Tutorial,Schools,Materials,Classes,Notification


# Register your models here.

admin.site.register(Courses)
admin.site.register(Profile)
admin.site.register(Skills)
admin.site.register(Tutorial)
admin.site.register(Schools)
admin.site.register(Materials)
admin.site.register(Classes)
admin.site.register(Notification)
admin.site.register(Announcements)
admin.site.register(Payment_Information)
admin.site.register(Comments)
admin.site.register(Comments_Holder)
