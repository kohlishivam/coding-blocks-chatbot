from django.db import models

# Create your models here.

class User(models.Model):
	fb_id = models.CharField(max_length=128)
	email = models.CharField(max_length=50)
	batch = models.URLField()

	def __unicode__(self):  #For Python 2, use __str__ on Python 3
	    return self.email


class Messages(models.Model):
	fb_id = models.CharField(max_length=128)
	name = models.CharField(max_length=50)
	profile_url = models.URLField()
	locale = models.CharField(max_length=50)
	gender = models.CharField(max_length=10)

	#TODO: add date time field (assignment)

	message = models.CharField(max_length=1000)

	def __unicode__(self):  #For Python 2, use __str__ on Python 3
	    return self.name