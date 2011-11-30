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

class CountryFormAdmin(admin.ModelAdmin):
    list_display = ('form_name', 'language', 'form_version')

    def form_name(self, country_form):
        return country_form.form.name

    def form_version(self, country_form):
        return country_form.form.majorminorversion

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'country')
    list_filter = ('country',)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'value',)

class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'form', 'medicine_countries')
    list_filter = ('countries',)
    ordering = ("name",)

    def medicine_countries(self, model):
        countries = model.countries.order_by("name")
        return ", ".join(country.name for country in countries)

admin.site.register(models.Country)
admin.site.register(models.Organisation)
admin.site.register(models.DosageForm)
admin.site.register(models.Medicine, MedicineAdmin)
admin.site.register(models.District, DistrictAdmin)
admin.site.register(models.Currency, CurrencyAdmin)
admin.site.register(models.Language)
admin.site.register(models.CommunityWorker, CommunityWorkerAdmin)
admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.SubmissionWorkerDevice, SubmissionWorkerDeviceAdmin)
admin.site.register(models.CountryForm, CountryFormAdmin)
