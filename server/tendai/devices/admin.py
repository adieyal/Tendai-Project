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

def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Active selected submissions"

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = "Deactivate selected submissions"

def mark_as_valid(modeladmin, request, queryset):
    queryset.update(verified=True, valid=True)
mark_as_valid.short_description = "Mark selected submissions as valid"

def mark_as_invalid(modeladmin, request, queryset):
    queryset.update(verified=True, valid=False)
mark_as_invalid.short_description = "Mark selected submissions as invalid"

class SubmissionWorkerDeviceAdmin(admin.ModelAdmin):
    list_display = ('community_worker', 'community_worker_organisation', 'submission_type', 'facility', 'device')
    list_filter = ('active', 'community_worker__first_name', 'community_worker__last_name', 'community_worker__organisation__name', 'device__device_id', 'submission__form__name', 'community_worker__country__name')
    date_hierarchy = "created_date"
    actions = [mark_as_invalid, mark_as_valid]

    def facility(self, obj):
        content = obj.submission.content
        submission_type = self.submission_type(obj)
        if not content: return ""

        try:
            if submission_type == "Facility Form":
                return content.section_name.facility_name
            elif submission_type == "Medicines Form":
                return content.section_general.facility_name
        except:
            return "Not Found"
        return ""

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
    list_filter = ('form', 'language', 'countries')

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
    list_filter = ('countries', 'form')
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
