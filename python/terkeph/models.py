from django.db import models

class PhUser(models.Model):
  uid = models.IntegerField(unique=True)
  slug = models.CharField(max_length=20, unique=True)
  name = models.CharField(max_length=20, unique=True, db_index=True)
  avatar = models.CharField(max_length=24) # max: own/slug
  point_lat = models.DecimalField(max_digits=8, decimal_places=6)
  point_lng = models.DecimalField(max_digits=9, decimal_places=6)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  
  def __unicode__(self):
    return self.name

  def point(self):
    return "%s,%s" % (self.point_lat, self.point_lng)

  def kml_point(self):
    return "%s,%s" % (self.point_lng, self.point_lat)

  def avatar_url(self):
    return "https://prohardver.hu/dl/faces/%s.gif" % self.avatar

  def prohardver_url(self):
    return "https://prohardver.hu/tag/%s.html" % self.slug

  def permalink_url(self):
    return 'https://terkeph.hangya.net/#' + str(self.point_lat) + '+' + str(self.point_lng) + '+15'

  def prohardver_link(self):
    return "<a href=\"%s\" onclick=\"window.open('%s', '%s', 'top=80,left=190,width=656,height=650,titlebar,menubar,scrollbars,resizable');return false\"><img src=\"%s\" alt=\"\" /></a>" % (self.prohardver_url(), self.prohardver_url(), self.slug, self.avatar_url())

  prohardver_link.allow_tags = True
