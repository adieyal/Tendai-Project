from django.db.models import Q, Sum

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
        disbursements = models.Disbursement.objects.prior_to(self.year, self.month).filter(country=country)
        cost = disbursements.aggregate(Sum('amount'))['amount__sum']
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
        disbursements = models.Disbursement.objects.prior_to(self.year, self.month).filter(country=country)
        cost = disbursements.aggregate(Sum('amount'))['amount__sum']
        if cost and submissions:
            return cost/submissions
        return 0.0


class MOHInteractionLevelView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data = self.interaction_level()
        return { 'moh_interaction': data }
    
    def interaction_level(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.interaction_level_for_country(country)
        return data
    
    def interaction_level_for_country(self, country):
        interaction = models.MOHInteractionLevel.objects.prior_to(self.year, self.month).filter(country=country)
        if interaction.count():
            return { 
                'level': interaction[0].level,
                'comment': interaction[0].comment,
                }
        return { 'level': 0, 'comment': '' }


class MOHInteractionPointsView(JSONView):
    def get_json_data(self, *args, **kwargs):
        data =  self.moh_interaction_points()
        return { 'moh_interaction_points': data }
    
    def moh_interaction_points(self):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.moh_interaction_points_for_country(country)
        return data
    
    def moh_interaction_points_for_country(self, country):
        points = models.MOHInteraction.objects.prior_to(self.year, self.month).filter(country=country)
        if points.count() > 0:
            return {
                'points': points.aggregate(Sum('points'))['points__sum'],
                'comment': points[0].comment,
                }
        return { 'points': 0, 'comment': '' }


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
        MOHInteractionLevelView,
        MOHInteractionPointsView,
        CostPerSubmissionView,
        CostPerMedicineSubmissionView,
        TotalSubmissionsView,
        MedicineSubmissionsView,
        ]
    
    def get_json_data(self, *args, **kwargs):
        data = {}
        for view in self.views:
            instance = view(**kwargs)
            data.update(instance.get_json_data())
        return data
