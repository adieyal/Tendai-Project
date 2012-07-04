from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import translation

import openrosa.models
import devices.models
import website.models

class Command(BaseCommand):
    def handle(self, *args, **options):
        exclude = [s.submission.id for s in website.models.Story.objects.all()]
        submissions = openrosa.models.ORFormSubmission.objects.filter(form__name='Tendai Story').exclude(id__in=exclude)
        with transaction.commit_on_success():
            for s in submissions:
                try:
                    media = openrosa.models.ORSubmissionMedia.objects.filter(submission=s)[0]
                except IndexError:
                    media = None
                story = website.models.Story()
                story.submission = s
                if media:
                    story.photo = media.get_absolute_path()
                story.heading = s.content.story.story_title or 'Empty'
                story.content = s.content.story.story_description or 'Empty'
                if s.submissionworkerdevice.community_worker:
                    story.monitor = s.submissionworkerdevice.community_worker
                    story.country = s.submissionworkerdevice.community_worker.country
                story.status = 'n'
                try:
                    story.save()
                except:
                    print 'Creating story for submission %d failed.' % (s.id)
