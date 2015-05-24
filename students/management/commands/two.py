#!/usr/local/bin/python
# coding: utf-8
import os, sys
from django.core.management.base import NoArgsCommand
from students.models import Score, Theme, Grade, Student
import datetime


class Command(NoArgsCommand):

    def handle(self, **options):
        themes = Theme.objects.filter()
        a=0
        themesList = []
        for each in themes:
            if each.hours_count*Student.objects.filter(grade=each.grade).count() > Score.objects.filter(theme=each).count():

                print str(a)+' '+each.theme_name.encode('utf-8').strip()
                themesList.append(each.theme_name)
                a+=1
        number = raw_input("Choose the theme: ")

        theme = Theme.objects.get(theme_name=themesList[int(number)])
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