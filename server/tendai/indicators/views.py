from django.db.models import Q

from utils import JSONView, last_day_of_month
import devices.models
import models

class CostPerSubmissionView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data = self.cost_per_submission()
        return { 'cost_per_submission': data }
    
    def cost_per_submission(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.cost_per_submission_for_country(country)
        return data
    
    def cost_per_submission_for_country(self, country):
        submissions = devices.models.SubmissionWorkerDevice.objects.all_valid.filter(community_worker__country=country).count()
        cost = models.Disbursement.objects.total_for_country(country, self.year, self.month)
        if cost and submissions:
            return cost/submissions
        return 0.0


class CostPerMedicineSubmissionView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data =  self.cost_per_medicine_submission()
        return { 'cost_per_medicine_submission': data }
    
    def cost_per_medicine_submission(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.cost_per_medicine_submission_for_country(country)
        return data
    
    def cost_per_medicine_submission_for_country(self, country):
        submissions = devices.models.SubmissionWorkerDevice.objects.medicines_submissions.filter(community_worker__country=country).count()
        cost = models.Disbursement.objects.total_for_country(country, self.year, self.month)
        if cost and submissions:
            return cost/submissions
        return 0.0


class InteractionLevelView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data = self.interaction_level()
        return { 'moh_interaction': data }
    
    def interaction_level(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.interaction_level_for_country(country)
        return data
    
    def interaction_level_for_country(self, country):
        interaction = models.MOHInteractionLevel.objects.default_for_country(country)
        if interaction:
            return { 'level': interaction.level, 'comment': interaction.comment }
        return { 'level': 0, 'comment': '' }


class TotalSubmissionsView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data = self.submissions()
        return { 'total_submissions': data }
    
    def submissions(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.submissions_for_country(country)
        return data
    
    def submissions_for_country(self, country):
        last_day = last_day_of_month(self.year, self.month)
        query = Q(community_worker__country=country)
        query &= Q(created_date__lte=last_day)
        submissions = devices.models.SubmissionWorkerDevice.objects.all_valid.filter(query).count()
        return submissions


class MedicineSubmissionsView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data = self.submissions()
        return { 'medicine_submissions': data }
    
    def submissions(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.submissions_for_country(country)
        return data
    
    def submissions_for_country(self, country):
        last_day = last_day_of_month(self.year, self.month)
        query = Q(community_worker__country=country)
        query &= Q(created_date__lte=last_day)
        submissions = devices.models.SubmissionWorkerDevice.objects.medicines_submissions.filter(query).count()
        return submissions


class CombinedView(JSONView):
    views = [
        CostPerSubmissionView,
        CostPerMedicineSubmissionView,
        InteractionLevelView,
        TotalSubmissionsView,
        MedicineSubmissionsView,
        ]
    
    def get_json_data(self, *args, **kwargs):
        data = {}
        for view in self.views:
            instance = view(**kwargs)
            data.update(instance.get_json_data())
        return data
