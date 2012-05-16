from django.db.models import Q, Sum

from utils import JSONView, last_day_of_month
import devices.models
import openrosa.models
import facility.models
import models


class PerCountryView(JSONView):
    key = 'countrydata'
    
    def get_json_data(self, *args, **kwargs):
        data = {}
        for country in devices.models.Country.objects.all():
            data[country.code] = self.data_for_country(country)
        return { self.key: data }


class CostPerSubmissionView(PerCountryView):
    key = 'cost_per_submission'
    
    def data_for_country(self, country):
        submissions = devices.models.SubmissionWorkerDevice.objects.all_valid.filter(community_worker__country=country).count()
        disbursements = models.Disbursement.objects.prior_to(self.year, self.month).filter(country=country)
        cost = disbursements.aggregate(Sum('amount'))['amount__sum']
        if cost and submissions:
            return cost/submissions
        return 0.0


class CostPerMedicineSubmissionView(PerCountryView):
    key = 'cost_per_medicine_submission'
    
    def data_for_country(self, country):
        submissions = devices.models.SubmissionWorkerDevice.objects.medicines_submissions.filter(community_worker__country=country).count()
        disbursements = models.Disbursement.objects.prior_to(self.year, self.month).filter(country=country)
        cost = disbursements.aggregate(Sum('amount'))['amount__sum']
        if cost and submissions:
            return cost/submissions
        return 0.0


class MOHInteractionLevelView(PerCountryView):
    key = 'moh_interaction_level'
    
    def data_for_country(self, country):
        interaction = models.MOHInteractionLevel.objects.prior_to(self.year, self.month).filter(country=country)
        if interaction.count():
            return { 
                'level': interaction[0].level,
                'comment': interaction[0].comment,
                }
        return { 'level': 0, 'comment': 'No reports to date.' }


class MOHInteractionPointsView(PerCountryView):
    key = 'moh_interaction'
    def data_for_country(self, country):
        data = []
        interactions = models.MOHInteraction.objects.prior_to(self.year, self.month).filter(country=country)
        if interactions.count() > 0:
            for interaction in interactions:
                data.append(
                    { 'type': interaction.type.id,
                      'points': interaction.type.points,
                      'description': interaction.type.description
                      })
        return data


class TotalSubmissionsView(PerCountryView):
    key = 'total_submissions'
    
    def data_for_country(self, country):
        last_day = last_day_of_month(self.year, self.month)
        query = Q(community_worker__country=country)
        query &= Q(created_date__lte=last_day)
        submissions = devices.models.SubmissionWorkerDevice.objects.all_valid.filter(query).count()
        return submissions


class MedicineSubmissionsView(PerCountryView):
    key = 'medicine_submissions'
    
    def data_for_country(self, country):
        last_day = last_day_of_month(self.year, self.month)
        query = Q(community_worker__country=country)
        query &= Q(created_date__lte=last_day)
        submissions = devices.models.SubmissionWorkerDevice.objects.medicines_submissions.filter(query).count()
        return submissions


class ConsecutiveSubmissionsView(PerCountryView):
    key = 'consecutive_submissions'
    
    def data_for_country(self, country):
        facilities = [f for f in facility.models.Facility.objects.all() if f.country==country]
        if not facilities:
            return 0.0
        submissions = []
        for months_ago in range(0,3):
            month = int(self.month) - months_ago
            year = int(self.year)
            if month < 1:
                month += 12
                year -= 1
            facilities_with_submissions = []
            for f in facilities:
                if self.submissions_for_facility_in_month(f, year, month):
                    facilities_with_submissions.append(f)
            submissions.append(facilities_with_submissions)
        facilities_with_consecutive = [f for f in submissions[0] if f in submissions[1] and f in submissions[2]]
        return (float(len(facilities_with_consecutive))/float(len(facilities)))*100.0
    
    def submissions_for_facility_in_month(self, facility, year, month):
        query = Q(submission__created_date__year=year, submission__created_date__month=month)
        query &= Q(submission__form__name='Medicines Form')
        submissions = facility.facilitysubmission_set.filter(query)
        return submissions.count() > 0


class ProgressView(PerCountryView):
    key = 'progress'
    
    def data_for_country(self, country):
        reports = models.TendaiProgressReport.objects.prior_to(self.year, self.month).filter(country=country)
        if reports.count():
            return {
                'reporting': {
                    'satisfactory': reports[0].reporting,
                    'comment': reports[0].reporting_comment,
                    },
                'adjustment': {
                    'satisfactory': reports[0].adjustment,
                    'comment': reports[0].adjustment_comment,
                    }
                }
        return {
                'reporting': {
                    'satisfactory': True,
                    'comment': 'No reports to date.',
                    },
                'adjustment': {
                    'satisfactory': True,
                    'comment': 'No reports to date.',
                    }
                }


class RisksView(PerCountryView):
    key = 'risk'
    
    def data_for_country(self, country):
        risks = models.Risk.objects.filter(date__year=self.year, date__month=self.month, country=country)
        if risks.count():
            return {
                'level': risks[0].level,
                'comment': risks[0].comment
                }
        return {
                'level': 'low',
                'comment': 'No situation reported.'
                }


class CombinedView(JSONView):
    views = [
        MOHInteractionLevelView,
        MOHInteractionPointsView,
        CostPerSubmissionView,
        CostPerMedicineSubmissionView,
        TotalSubmissionsView,
        MedicineSubmissionsView,
        ConsecutiveSubmissionsView,
        ProgressView,
        RisksView,
        ]
    
    def get_json_data(self, *args, **kwargs):
        data = {}
        for view in self.views:
            instance = view(**kwargs)
            data.update(instance.get_json_data())
        return data
