from django.conf.urls.defaults import *
import views

urlpatterns = patterns('medicine_analysis.views',
    #url(r'^json/$', 'MedicineStockView.as_view', {}, 'medicine_analysis_json'),
    url(r'^$', views.MedicineStockView.as_view(), {}, 'medicine_analysis_graph'),
    #url(r'^$', 'who_cares', {}, 'medicine_analysis_graph'),
)
