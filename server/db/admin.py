from django.contrib import admin
from django.contrib.auth.models import Group

from db import models

admin.site.site_header = "Feed WatchDog"
admin.site.unregister(Group)


@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Stream)
class StreamAdmin(admin.ModelAdmin):
    list_select_related = ("source", "receiver")
