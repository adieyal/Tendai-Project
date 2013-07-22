from django.contrib import admin
import models

class ScorecardStoryAdmin(admin.ModelAdmin):
    list_display = ('community_worker', 'created_date', 'country') 

    def community_worker(self, obj):
        return obj.submission_worker_device.community_worker

    def created_date(self, obj):
        return obj.submission_worker_device.created_date

    def country(self, obj):
        return obj.submission_worker_device.community_worker.country
admin.site.register(models.ScorecardStory, ScorecardStoryAdmin)
