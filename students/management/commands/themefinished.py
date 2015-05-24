#!/usr/local/bin/python
# coding: utf-8
import os, sys
from django.core.management.base import NoArgsCommand
from students.models import Score, Theme, Grade, Student
import datetime



def addTwo(theme):

    namesId = Student.objects.filter(grade=theme.grade)
    score = Score.objects.filter(theme=theme)


    names = []
    for each in namesId:
        studentName = Student.objects.get(pk=each.pk).name
        names.append(studentName)

    numOfTwoScores=0
    for each in names:
        stud = Student.objects.get(name=each)

        listOfScores = score.filter(student_name=stud.pk)
        hours=int(theme.hours_count)
        numOfScores = 0
        for scores in listOfScores:
            if scores.score<0:
                hours-=1
        for scores in listOfScores:
            if scores.score>=0:
                numOfScores+=1

        if hours>numOfScores:
            for i in range(hours-numOfScores):
                twoForStud = Score(grade=theme.grade,theme=theme,student_name=stud,score=2)
                twoForStud.save()
                numOfTwoScores+=1

    print 'Добавлено '+str(numOfTwoScores)+' двоек'

class Command(NoArgsCommand):

    def handle(self, **options):
        themes = Theme.objects.filter()
        print 'start to find themes'
        for each in themes:
            if each.end.day == datetime.date.today().day and each.end.month == datetime.date.today().month:
                addTwo(each)
                print 'found theme'




