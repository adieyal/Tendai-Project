from django.contrib import admin
import models

class CommunityWorkerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organisation')
    list_filter = ('first_name', 'last_name', 'organisation')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'community_worker_first_name', 'community_worker_last_name', 'community_worker_organisation')
    list_filter = ('community_worker__first_name', 'community_worker__last_name', 'community_worker__organisation__name')

    def community_worker_first_name(self, obj):
        return obj.community_worker.first_name

    def community_worker_last_name(self, obj):
        return obj.community_worker.last_name

    def community_worker_organisation(self, obj):
        return obj.community_worker.organisation

admin.site.register(models.Organisation)
admin.site.register(models.CommunityWorker, CommunityWorkerAdmin)
admin.site.register(models.Device, DeviceAdmin)
