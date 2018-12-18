from django.db import models


class Document(models.Model):
    file = models.FileField(upload_to="")


class Specialty(models.Model):
    name = models.CharField(default='', max_length=100)


class Location(models.Model):
    name = models.CharField(default='', max_length=100)


class Provider(models.Model):
    first_name = models.CharField(default='', max_length=50)
    last_name = models.CharField(default='', max_length=50)
    specialty = models.ForeignKey(Specialty, related_name='providers', on_delete=models.CASCADE)


class Patient(models.Model):
    mrn = models.IntegerField(default=-1)
    name = models.CharField(default='', max_length=100)


class Transfusion(models.Model):
    patient = models.ForeignKey(Patient, related_name='transfusions', on_delete=models.CASCADE)
    blood_product = models.CharField(default='', max_length=100)
    issue_time = models.DateTimeField()
    transfusions_on_day = models.IntegerField(default=-1)
    din = models.CharField(default='', max_length=20)
    num_units = models.IntegerField(default=-1)
    product = models.CharField(default='', max_length=20)
    test_type = models.CharField(default='', max_length=20)
    test_result = models.CharField(default='', max_length=20)
    test_accession = models.CharField(default='', max_length=20)
    test_time = models.DateTimeField()
    location = models.ForeignKey(Location, related_name='transfusions', on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, related_name='transfusions', on_delete=models.CASCADE)
