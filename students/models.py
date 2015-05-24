from django.db import models
from datetime import datetime
from smart_selects.db_fields import ChainedForeignKey
from django.core.validators import ValidationError
from django.contrib import messages
from django import forms

# Create your models here.
class Grade(models.Model):
    grade_name = models.CharField(max_length=4)
    def __unicode__ (self):
        return self.grade_name



class Student(models.Model):
    name = models.CharField(max_length = 200)
    grade = models.ForeignKey(Grade)
    nfcId = models.CharField(max_length=50)
    def __unicode__ (self):
        return self.name

class Foursquare(models.Model):
    student = models.ForeignKey(Student)
    token = models.CharField(max_length=50)

class Passwords(models.Model):
    password = models.CharField(max_length=20)
    student = models.ForeignKey(Student)
    def __unicode__ (self):
        return self.password

class Subject(models.Model):
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name

class Theme (models.Model):
    theme_name = models.CharField(max_length = 200)
    hours_count = models.IntegerField()
    grade = models.ForeignKey(Grade)
    subject = models.ForeignKey(Subject)
    start = models.DateTimeField(default=datetime.now)
    end = models.DateTimeField(default=datetime.now)
    def __unicode__(self):
        return self.theme_name

class Test(models.Model):
    name = models.CharField(max_length=100)
    theme = models.ForeignKey(Theme)
    minutes = models.IntegerField()
    prop = models.CharField(max_length=100)
    def __unicode__ (self):
        return self.name

class Question(models.Model):
    test = models.ForeignKey(Test)
    choice_text = models.CharField(max_length=1500)
    def __unicode__(self):
        return self.choice_text

class PassedTest(models.Model):
    student = models.ForeignKey(Student)
    test = models.ForeignKey(Test)
    startTime = models.DateTimeField(default=datetime.now)
    def __unicode__(self):
        return self.student.name

class Score(models.Model):
    grade = models.ForeignKey(Grade)
    theme = ChainedForeignKey(Theme,
           chained_field = "grade",
           chained_model_field = "grade",
           show_all=False,
           auto_choose=True)
    student_name = ChainedForeignKey(Student,
           chained_field = "grade",
           chained_model_field = "grade",
           show_all=False,
           auto_choose=True)
    score_date = models.DateTimeField(default=datetime.now)
    score = models.IntegerField()
    def clean(self):
        allMarks = Score.objects.filter(theme=self.theme,student_name=self.student_name)
        if allMarks.count() >= self.theme.hours_count and not self.pk:
            raise ValidationError({'pub_date': 'All marks posted'})



class Schedule(models.Model):
    grade = models.ForeignKey(Grade)
    subject = models.ForeignKey(Subject)
    weekDay = models.IntegerField()
    startHour = models.IntegerField()
    startMinute = models.IntegerField()
    def __unicode__(self):
        return self.grade.grade_name


class Journal(models.Model):
    grade = models.ForeignKey(Grade)
    name = ChainedForeignKey(Student,
           chained_field = "grade",
           chained_model_field = "grade",
           show_all=False,
           auto_choose=True)
    checkTime = models.DateTimeField(default=datetime.now)
    def __unicode__(self):
        return self.name.name


class Achieves(models.Model):
    achieve = models.CharField(max_length=100,primary_key=True)
    def __unicode__(self):
        return self.achieve



class Student_achieves(models.Model):
    name = models.ForeignKey(Student)
    achieve = models.ForeignKey(Achieves)
    date = models.DateTimeField()
    def __unicode__(self):
        return self.name.name + '-' +  self.achieve.achieve

