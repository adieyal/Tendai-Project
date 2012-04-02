from django.contrib import admin
import models

class ScorecardStoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.ScorecardStory, ScorecardStoryAdmin)
