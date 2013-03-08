from django.db import models
from django.conf import settings
from os import path

import devices.models
import openrosa.models

class MenuItem(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey('MenuItem', blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True, verbose_name='Redirect URL', help_text='This menu item will redirect to this URL if it is entered.')
    page = models.ForeignKey('Page', blank=True, null=True)
    enabled = models.BooleanField(default=True)
    
    @property
    def link(self):
        if self.page or self.url:
            return True
        return False
    
    @property
    def dropdown(self):
        if self.menuitem_set.count() == 0:
            return False
        return True
    
    @property
    def submenu(self):
        return self.menuitem_set.filter(enabled=True)
    
    def get_href(self):
        if self.url:
            return self.url
        if self.page:
            return self.page.get_absolute_url()
        return None
    
    def __unicode__(self):
        if self.parent:
            return u'%s > %s' % (self.parent, self.name)
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=32)
    path = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.name

class Page(models.Model):
    slug = models.CharField(max_length=64)
    template = models.ForeignKey('Template')
    title = models.CharField(max_length=64)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return "/page/%s/" % (self.slug)

    def __unicode__(self):
        return self.title

class Story(models.Model):
    STATES = (('n', 'New'),
              ('e', 'Edited'),
              ('p', 'Published'),
              ('q', 'Pending'),
              ('r', 'Rejected'))
    RESOURCES = path.join(settings.MEDIA_ROOT, 'openrosa', 'submissions', 'images')
    submission = models.ForeignKey(openrosa.models.ORFormSubmission)
    heading = models.TextField()
    content = models.TextField()
    photo = models.FilePathField(path=RESOURCES, recursive=True, match=".*\.jpg")
    monitor = models.ForeignKey(devices.models.CommunityWorker)
    country = models.ForeignKey(devices.models.Country)
    status = models.CharField(max_length=1, choices=STATES)
    
    @property
    def imageurl(self):
        p = self._meta.get_field('photo').path
        ROOT = path.join(settings.MEDIA_URL, 'openrosa', 'submissions', 'images')
   	m = self.photo.replace('/home/sarpam/code/tendai/server/tendai/media/openrosa/submissions/images', ROOT, 1)
        return m.replace(p, ROOT, 1)
    
    def get_absolute_url(self):
        return self.submission.submissionworkerdevice.get_absolute_url()
    
    def __unicode__(self):
        return u'%s' % (self.heading)
    
    class Meta:
        verbose_name_plural = 'Stories'
