from django.contrib import admin
import models

class CommunityWorkerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organisation', 'phone_number', 'country')
    list_filter = ('first_name', 'last_name', 'organisation', 'country')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'community_worker_first_name', 'community_worker_last_name', 'community_worker_organisation')
    list_filter = ('community_worker__first_name', 'community_worker__last_name', 'community_worker__organisation__name')

    def community_worker_first_name(self, obj):
        return obj.community_worker.first_name

    def community_worker_last_name(self, obj):
        return obj.community_worker.last_name

    def community_worker_organisation(self, obj):
        return obj.community_worker.organisation

class SubmissionWorkerDeviceAdmin(admin.ModelAdmin):
    list_display = ('community_worker_first_name', 'community_worker_last_name', 'community_worker_organisation', 'submission_type', 'device')
    list_filter = ('community_worker__first_name', 'community_worker__last_name', 'community_worker__organisation__name', 'device__device_id', 'submission__form__name')
    date_hierarchy = "created_date"

    def community_worker_first_name(self, obj):
        return obj.community_worker.first_name

    def community_worker_last_name(self, obj):
        return obj.community_worker.last_name

    def community_worker_organisation(self, obj):
        return obj.community_worker.organisation

    def submission_type(self, obj):
        return obj.submission.form.name

    def device(self, obj):
        return self.device.device_id

admin.site.register(models.Country)
admin.site.register(models.Organisation)
admin.site.register(models.CommunityWorker, CommunityWorkerAdmin)
admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.SubmissionWorkerDevice, SubmissionWorkerDeviceAdmin)
admin.site.register(models.CountryForm)
