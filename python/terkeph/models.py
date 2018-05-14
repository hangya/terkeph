from django.db import models

class PhUser(models.Model):
    uid = models.IntegerField(unique=True)
    slug = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20, unique=True, db_index=True)
    avatar = models.CharField(max_length=24) # max: own/slug
    latlng = models.CharField(max_length=20, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
  
    def __str__(self):
        return self.name

    def point_lat(self):
        return self.latlng.split(',')[0]
    def point_lng(self):
        return self.latlng.split(',')[1]

    def kml_point(self):
        return "%s,%s" % (self.point_lng(), self.point_lat())

    def avatar_url(self):
        return "https://prohardver.hu/dl/faces/%s.gif" % self.avatar

    def prohardver_url(self):
        return "https://prohardver.hu/tag/%s.html" % self.slug

    def permalink_url(self):
        return 'https://terkeph.hangya.net/#' + self.point_lat() + '+' + self.point_lng() + '+15'

    def prohardver_link(self):
        return "<a href=\"%s\" onclick=\"window.open('%s', '%s', 'top=80,left=190,width=656,height=650,titlebar,menubar,scrollbars,resizable');return false\"><img src=\"%s\" alt=\"\" /></a>" % (self.prohardver_url(), self.prohardver_url(), self.slug, self.avatar_url())

    prohardver_link.allow_tags = True

