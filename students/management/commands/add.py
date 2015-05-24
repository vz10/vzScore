#!/usr/local/bin/python
# coding: utf-8
import os, sys
from django.core.management.base import NoArgsCommand
from students.models import Score, Achieves
import datetime
import lxml.html as html
from twython import Twython, TwythonError


def tweetSomething (text):
    APP_KEY = 'StNRV6kswinBGjEaxxftaFv9J'
    APP_SECRET = 'lLkVr0V2kRmEq1jBYfEJ5NnbLCcutJGhUopciSTIOgFeNIT9Ji'
    OAUTH_TOKEN = '56944567-wryXx642TN2AS6x7RcneXFG2HFFuUAhVPP0FxgZqB'
    OAUTH_TOKEN_SECRET = 'JZwaXpaSJCYzHyE1FM1UBu6aHPRygSbiDv4Ykiq8PyAT4'
    #Requires Authentication as of Twitter API v1.1
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    try:
        twitter.update_status(status=text)
        print 'i tweeted'
        #print 'no tweet'
    except TwythonError as e:
        print e

class Command(NoArgsCommand):



    def handle(self, **options):
        #
        # ronaldo_main_domain_stat = 'http://ua.tribuna.com/cristiano-ronaldo/'
        # page = html.parse(ronaldo_main_domain_stat)
        # a = page.getroot().find_class('short-statistic').pop()
        # t = a.getchildren()
        # f= t[1].getchildren()
        # goals = f[1].text_content()
        #
        # try:
        #     f = open('ronaldo', 'r')
        #     newOne = int(goals)
        #     old = int(f.readline())
        #     if newOne == old:
        #         #print('same count of goals')
        #         f.close()
        #     else:
        #         #randomMarks(12,newOne-old)
        #         #print (str(newOne-old))
        #         f.close()
        #         f = open('ronaldo', 'w')
        #         f.write(goals)
        #         f.close()
        # except:
        #     f = open('ronaldo', 'w')
        #     f.write(goals)
        #     f.close()
        #
        # messi_main_domain_stat = 'http://ua.tribuna.com/messi/'
        # page = html.parse(messi_main_domain_stat)
        # a = page.getroot().find_class('short-statistic').pop()
        # t = a.getchildren()
        # f= t[1].getchildren()
        # goals = f[1].text_content()
        #
        # try:
        #     f = open('messi', 'r')
        #     newOne = int(goals)
        #     old = int(f.readline())
        #     if newOne == old:
        #         #print('same count of goals')
        #         f.close()
        #     else:
        #         #randomMarks(2,newOne-old)
        #         #print (str(newOne-old))
        #         f.close()
        #         f = open('messi', 'w')
        #         f.write(goals)
        #         f.close()
        # except:
        #     f = open('messi', 'w')
        #     f.write(goals)
        #     f.close()


        day = datetime.datetime.today()-datetime.timedelta(days=1)
        f = open('workfile', 'r')
        if f.readline()==str(datetime.date.today()):
             f.close()
             print 'too much for one day'
             return 0
        else:
             f.close()
             f = open('workfile', 'w')
             f.write(str(datetime.date.today()))
             f.close()
        startDay = datetime.datetime(day.year,day.month,day.day,0,0,0,0)
        endDay = datetime.datetime(day.year,day.month,day.day,23,59,59,0)
        sc = Score.objects.filter(score_date__range=(startDay,endDay))
        countScores= [0,0,0,0,0,0,0,0,0,0,0,0]

        for each in sc:
             countScores[each.score-1]+=1
        thereIsSomeScores=False
        tweetingStr = "Вчера было выставлено: \n"
        for each in range(12):
             if countScores[each]>0:
                 thereIsSomeScores=True
                 addString = str(each+1)+' - '+str(countScores[each])+' шт. \n'
                 tweetingStr+=addString
        if thereIsSomeScores==True:
            tweetSomething(tweetingStr)
        else:
            print 'no scores today'



