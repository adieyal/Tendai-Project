from django.contrib import admin
import models

class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'timestamp', 'amount', 'inconsistent')
    list_filter = ('medicine', 'facility')

class MedicineRestockExpectationAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'timestamp', 'start', 'end', 'amount', 'inconsistent')
    list_filter = ('medicine', 'facility')

class MedicineRestockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'timestamp', 'start', 'end', 'amount', 'inconsistent')
    list_filter = ('medicine', 'facility')

admin.site.register(models.MedicineStock, MedicineStockAdmin)
admin.site.register(models.MedicineRestockExpectation, MedicineRestockExpectationAdmin)
admin.site.register(models.MedicineRestock, MedicineRestockAdmin)
