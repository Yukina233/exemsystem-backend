# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from backend import models

# Register your models here.
class UserListAdmin(admin.ModelAdmin):
    list_display = ['username', 'password', 'usertype']

class PaperAdmin(admin.ModelAdmin):
    list_display = ['pid', 'pname', 'teaname', 'penabled', 'stulist', 'prolist']

class TestRecordAdmin(admin.ModelAdmin):
    list_display = ['paperid', 'stuid', 'submit_time', 'answers', 'keguan_grade',
      'keguan_detail', 'zhuguan_grade', 'zhuguan_detail', 'total_score', 'confirmed']

admin.site.register(models.UserList, UserListAdmin)
admin.site.register(models.Paper, PaperAdmin)
admin.site.register(models.TestRecord, TestRecordAdmin)
