# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals
from django.http import HttpResponse
from django.template import Context, loader
#from django.shortcuts import render
from students.models import Theme, Score, Student, Grade, Passwords, Test, PassedTest, Question, Subject, Achieves, Journal, Schedule, Foursquare
import pygal
from pygal.style import Style, LightenStyle
from pygal.colors import darken, lighten
from django.utils.safestring import mark_safe
#import locale
#import cron
#import json
import datetime
from constants import urlPattern
#import sys
from math import floor, ceil
import hashlib
from twython import Twython, TwythonError
from django.db.models import Q
import lxml.html as html
import random
import requests

BlueStyle = Style(
    background='transparent',
    plot_background='transparent',
    foreground='rgba(0, 0, 0, 0.9)',
    foreground_light='rgba(0, 0, 0, 0.9)',
    foreground_dark='rgba(0, 0, 0, 0.6)',
    opacity='.5',
    opacity_hover='.9',
    transition='250ms ease-in',
    colors=(
        '#00b2f0', '#43d9be', '#0662ab', darken('#00b2f0', 20),
        lighten('#43d9be', 20), lighten('#7dcf30', 10), darken('#0662ab', 15),
        '#ffd541', '#7dcf30', lighten('#00b2f0', 15), darken('#ffd541', 20)))

ranks = ['рядовой','сержант','старшина','прапорщик','лейтенант','капитан','майор','подполковник','полковник','генерал','маршал', 'тупыш']


def choice(request):
    theme_list = Theme.objects.all()
    grades = list(Grade.objects.filter(~Q(grade_name='NaN')))
    subjects = list(Subject.objects.all())
    scores = {}
    for each in theme_list:
        scores[each.id] = len(Score.objects.filter(theme=each.id))==len(Student.objects.filter(grade=each.grade.id))*each.hours_count
    template = loader.get_template('students/choice.html')
    context = Context({
        'grade_list': grades,
        'subjects':subjects,
        'theme_list': theme_list,
        'scores':scores,
        'urlPattern': urlPattern,

    })
    return HttpResponse(template.render(context))

def visitChoice(request):
    grades = list(Grade.objects.filter(~Q(grade_name='NaN')))
    template = loader.get_template('students/visitChoice.html')
    context = Context({
        'grade_list': grades,
        'urlPattern': urlPattern,

    })
    return HttpResponse(template.render(context))

def visit(request,class_id):
    day = datetime.date.today()
    thisGrade = Grade.objects.get(pk=class_id)
    classSchedule = Schedule.objects.filter(grade=thisGrade)
    classJournal = Journal.objects.filter(grade=thisGrade)
    namesId = Student.objects.filter(grade=thisGrade)
    names = []
    for each in namesId:
        names.append(each.name)
    names.sort()

    #firstDayOfScope = day - datetime.timedelta(weeks=2)
    firstDayOfScope = day

    dates = []
    rowDates = []
    counter=0

    while len(rowDates)<16:
        dayLessons = classSchedule.filter(weekDay=firstDayOfScope.weekday()).order_by('-startHour')
        if (dayLessons):
            for everyLesson in dayLessons:
                lessonStart = datetime.datetime(firstDayOfScope.year,firstDayOfScope.month,firstDayOfScope.day,everyLesson.startHour,everyLesson.startMinute,0,0) - datetime.timedelta(minutes=20)
                lessonEnd = lessonStart + datetime.timedelta(minutes=65)
                if (classJournal.filter(checkTime__range = (lessonStart, lessonEnd))):
                    if firstDayOfScope.day<10:
                        dayStr = '0'+str(firstDayOfScope.day)
                    else:
                        dayStr= str(firstDayOfScope.day)
                    if firstDayOfScope.month<10:
                        monthStr = '0'+str(firstDayOfScope.month)
                    else:
                        monthStr = str(firstDayOfScope.month)
                    dates.insert(0,dayStr+'/'+monthStr)
                    rowDates.insert(0,lessonStart)
                    counter+=1
        firstDayOfScope-=datetime.timedelta(days=1)
        if (not classJournal.filter(checkTime__lt = firstDayOfScope)):
            break

    visits = []

    for idiot in names:
        idiotVisits = [idiot]
        stud = Student.objects.get(name=idiot)
        idiotQuery = Journal.objects.filter(name=stud)
        for date in rowDates:
            lessonStart = date +  datetime.timedelta(minutes=25)
            lessonEnd = date +  datetime.timedelta(minutes=65)

            if (idiotQuery.filter(checkTime__range=(date,lessonStart))):
                idiotVisits.append(2)
            elif (idiotQuery.filter(checkTime__range=(lessonStart,lessonEnd))):
                idiotVisits.append(1)
            else:
                idiotVisits.append(0)
        visits.append(idiotVisits)

    template = loader.get_template('students/visit.html')
    context = Context({
        'dates': dates,
        'visits':visits,
        'grade':thisGrade.grade_name,
        'urlPattern': urlPattern,

    })
    return HttpResponse(template.render(context))

def semestr(request,class_id,sort_id):


    line_chart = pygal.HorizontalBar(fill=True, interpolate='cubic',
                                     style=BlueStyle, show_legend=False, no_data_text='No scores yet',
                                     margin=0, padding=0,title_font_size=0, value_font_size=13, label_font_size=10, title = None, disable_xml_declaration=True, print_values = True)

    day = datetime.date(2015,1,1)
    endDay = datetime.date(2015,5,31)
    thisGrade = Grade.objects.get(pk=class_id)
    allThemes = Theme.objects.filter(grade=thisGrade, end__range = (day,endDay) )

    allStudents = Student.objects.filter(grade=thisGrade)
    allMarks=[]
    thisIdiots = []

    for idiots in allStudents:
        thisIdiots.append(idiots.name)
    thisIdiots.sort()

    for idiots in thisIdiots:
        thisIdiotMarks = []
        semestrSum = 0
        for each in allThemes:
            thisThemeMarks = Score.objects.filter(theme=each,student_name__name=idiots)
            sum, count, countMarks = 0,0,0
            for mark in thisThemeMarks:
                if mark.score>=0:
                    sum +=mark.score
                else:
                	count+=1
            if thisThemeMarks.count()<each.hours_count:
                sum = sum + 12*(each.hours_count-thisThemeMarks.count())
            countMarks=each.hours_count-count
            sum = int(round(sum / countMarks))

            rowDates = []
            classSchedule = Schedule.objects.filter(grade=each.grade)
            firstDayOfScope = each.start
            a = each.end-each.start
            for day in range(a.days):
                dayLessons = classSchedule.filter(weekDay=firstDayOfScope.weekday())
                if (dayLessons):
                    for everyLesson in dayLessons:
                        lessonStart = datetime.datetime(firstDayOfScope.year,firstDayOfScope.month,firstDayOfScope.day,everyLesson.startHour,everyLesson.startMinute,0,0) - datetime.timedelta(minutes=20)
                        lessonEnd = lessonStart + datetime.timedelta(minutes=65)
                        if (Journal.objects.filter(checkTime__range = (lessonStart, lessonEnd))):
                            rowDates.append(lessonStart)
                firstDayOfScope+=datetime.timedelta(days=1)
            stud = Student.objects.get(name=idiots)
            allVisits = Journal.objects.filter(checkTime__range=(each.start,each.end),name = stud)
            sumOfVisits=0.0
            if allVisits:
                for date in rowDates:
                    lessonStart = date +  datetime.timedelta(minutes=25)
                    lessonEnd = date +  datetime.timedelta(minutes=65)
                    if (allVisits.filter(checkTime__range=(date,lessonStart))):
                        sumOfVisits+=2

                    elif (allVisits.filter(checkTime__range=(lessonStart,lessonEnd))):
                        sumOfVisits+=1
            if rowDates:
                sumOfVisits = sumOfVisits/len(rowDates)
            else:
                sumOfVisits = 0
            #print (idiots+' '+each.theme_name+' '+str(sumOfVisits))
            if sumOfVisits>1.7:
                sum+=1
                if sum>12:
                    sum=12
            semestrSum +=sum
            #print (idiots+' '+each.theme_name+' '+str(sum))
        if allThemes:
            allMarks.append(int(round(semestrSum/allThemes.count())))
        else:
            allMarks.append(12)

    if int(sort_id) == 2:
        outputIdiots = [x for (y,x) in sorted(zip(allMarks,thisIdiots))]
        allMarks.sort()
        line_chart.add('', allMarks)
        line_chart.x_labels = outputIdiots
    else:
        line_chart.add('', reversed(allMarks))
        line_chart.x_labels = reversed(thisIdiots)
    title = "Оценки за II семестр "+thisGrade.grade_name+" класс"

    template = loader.get_template('students/diagram.html')


    content = str(HttpResponse(line_chart.render()))
    content = content[39:]
    context = Context({'diagram': mark_safe(content),
                       'urlPatternBtn': urlPattern+'/semestr/',
                       'urlPattern':urlPattern,
                       'theme_id':class_id,
                       'theEnd': 0,
                       'sort_id':sort_id,
                       'title': title})

    return HttpResponse(template.render(context))

def index(request):
    template = loader.get_template('students/index.html')
    context = Context({'urlPattern': urlPattern, })
    return HttpResponse(template.render(context))

def kharkiv(request):
    template = loader.get_template('students/kharkiv.html')
    context = Context({'urlPattern': urlPattern, })
    return HttpResponse(template.render(context))

def about(request):
    template = loader.get_template('students/about.html')
    context = Context({'urlPattern': urlPattern, })
    return HttpResponse(template.render(context))

def contacts(request):
    template = loader.get_template('students/contacts.html')
    context = Context({'urlPattern': urlPattern, })
    return HttpResponse(template.render(context))

def diagram(request, theme_id, sort_id):
    maxScore = 12
    try:
        score = Score.objects.filter(theme=theme_id)
    except Theme.DoesNotExist:
        raise
    hoursInThisTheme = Theme.objects.get(pk=theme_id).hours_count
    theme = Theme.objects.get(pk=theme_id)

    theEnd = 0
    timeToEnd = theme.end.date() - datetime.date.today();
    print theme.end.date().year
    if timeToEnd.days<3 and timeToEnd.days>=0:

        theEnd = str(theme.end.date().month)+'/'+str(theme.end.date().day)+'/'+str(theme.end.date().year) + ' 23:59:00'



    line_chart = pygal.HorizontalBar(fill=True, interpolate='cubic',
                                     style=BlueStyle, show_legend=False, no_data_text='No scores yet',
                                     margin=0, padding=0,title_font_size=0, label_font_size=10,value_font_size=11, title = None, disable_xml_declaration=True, print_values = True)

    names, allScores, namesWithScores, namesWhoReached,  s = [], [], [], [], ' '
    namesId = Student.objects.filter(grade=Theme.objects.get(pk=theme_id).grade)

    for each in namesId:
        studentName = Student.objects.get(pk=each.pk).name
        names.append(studentName)
    names.sort()

    rowDates = []
    classSchedule = Schedule.objects.filter(grade=theme.grade)
    firstDayOfScope = theme.start
    a = theme.end-theme.start
    for each in range(a.days):
        dayLessons = classSchedule.filter(weekDay=firstDayOfScope.weekday())
        if (dayLessons):
            for everyLesson in dayLessons:
                lessonStart = datetime.datetime(firstDayOfScope.year,firstDayOfScope.month,firstDayOfScope.day,everyLesson.startHour,everyLesson.startMinute,0,0) - datetime.timedelta(minutes=20)
                lessonEnd = lessonStart + datetime.timedelta(minutes=65)
                if (Journal.objects.filter(checkTime__range = (lessonStart, lessonEnd))):
                    rowDates.append(lessonStart)
        firstDayOfScope+=datetime.timedelta(days=1)
    for each in names:
        goodAttendent = False;
        stud = Student.objects.get(name=each)
        allVisits = Journal.objects.filter(checkTime__range=(theme.start,theme.end),name = stud)
        sumOfVisits=0.0
        if allVisits:
            for date in rowDates:
                lessonStart = date +  datetime.timedelta(minutes=25)
                lessonEnd = date +  datetime.timedelta(minutes=65)
                if (allVisits.filter(checkTime__range=(date,lessonStart))):
                    sumOfVisits+=2

                elif (allVisits.filter(checkTime__range=(lessonStart,lessonEnd))):
                    sumOfVisits+=1

            sumOfVisits = sumOfVisits/len(rowDates)


        listOfScores = score.filter(student_name=stud.pk)
        currentScore = maxScore
        hours=hoursInThisTheme
        numOfScores=0
        for scores in listOfScores:
            if scores.score<0:
                hours-=1
        for scores in listOfScores:
            if scores.score>=0:
                currentScore -= (maxScore - float(scores.score)) / hours
                numOfScores+=1
        if sumOfVisits>1.7:
            currentScore+=1
            goodAttendent = True;
            if currentScore>12:
                currentScore=12
        allScores.append(round(currentScore,2))
        if goodAttendent:
            namesWithScores.append(each+' ('+str(numOfScores)+'  из '+str(hours)+')' + unichr(0x2713))
        else:
            namesWithScores.append(each+' ('+str(numOfScores)+'  из '+str(hours)+')' + unichr(0x2573))


    if int(sort_id) == 2:
        outputIdiots = [x for (y,x) in sorted(zip(allScores,namesWithScores))]
        allScores.sort()
        line_chart.add('', allScores)
        line_chart.x_labels = outputIdiots
    else:
        line_chart.add('', reversed(allScores))
        line_chart.x_labels = reversed(namesWithScores)

    template = loader.get_template('students/diagram.html')

    content = str(HttpResponse(line_chart.render()))
    content = content[39:]
    context = Context({'diagram': mark_safe(content),
                       'urlPattern': urlPattern,
                       'urlPatternBtn':urlPattern,
                       'title': Theme.objects.get(pk=theme_id).theme_name,
                       'theme_id': theme_id,
                       'theEnd': theEnd,
                       'sort_id': sort_id})

    return HttpResponse(template.render(context))

def achieve(request):
    template = loader.get_template('students/achieve.html')
    day = datetime.date.today()
    weekDay = []
    for i in range(1,7):
        sunday = day - datetime.timedelta(days=day.weekday()) + datetime.timedelta(weeks=-i+1)
        monday = day - datetime.timedelta(days=day.weekday()) + datetime.timedelta(weeks=-i)
        weekDay.append([monday,sunday])

    lastWeekScores = Score.objects.filter(score_date__range=(weekDay[0][0], weekDay[0][1]),score__gt=0)

    #lastWeekScores = Score.objects.all();
    clever, dumb = ['Батозский','Батозский','Батозский'], ['Содин','Содин','Содин']
    nanGrade = Grade.objects.get(grade_name='NaN')
    student_list = Student.objects.filter(~Q(grade=nanGrade)).order_by('name')
    scores, dumbs, both = [], [], []
    achieveList = []
    achieveDict = {}
    rankDict={}
    for each in student_list:
        oneStScore = lastWeekScores.filter(student_name=each)
        #print each.name
        if oneStScore:
            a, b = 0, 0
            for score in oneStScore:
                #print score.score
                if score.score >=0:
                    a += score.score
                    b += 1
            if b > 0:
                scores.append(a/b+b/100)
                dumbs.append(each.name)
    i = len (scores)

    for each in range(i):
        s = max(scores)
        i = scores.index(s)
        both.append([dumbs.pop(i),scores.pop(i)])
    if len(scores) >= 6:
        cleverNum = 3
        dumbNum = 3
    else:
        cleverNum =  3 if int(floor(len(both) / 2))>3 else int(floor(len(both)))
        dumbNum = 3 if int(ceil(len(both) / 2))>3 else int(ceil(len(both) / 2))

    for i in range(cleverNum):
        clever[i] = both[i][0]

    for i in range(dumbNum):
        dumb[i] = both[-1 - i][0]

    for each in student_list:
        studentThemes = Theme.objects.filter(grade=Student.objects.get(name=each).grade)
        studentScore = Score.objects.filter(student_name=each)
        rank=0
        for eachTheme in studentThemes:
            oneThemeScores = studentScore.filter(theme=eachTheme)
            sum = amount = 0
            if len(oneThemeScores) == eachTheme.hours_count:
                for eachScore in oneThemeScores:
                    if eachScore.score>0:
                        sum+=eachScore.score
                        amount+=1
                if rank<9 and sum/amount>6:
                    rank+=1
                elif rank > -1 and sum/amount<4:
                    rank -=1
        rankDict[each.name]=rank

        weekScore = Score.objects.filter(student_name=each, score__gt=0)
        appendList = []
        for i in weekDay:
            lastWeekScores = [score.score for score in weekScore.filter(score_date__range=(i[0], i[1]))]
            if lastWeekScores:
                a=0
                for score in lastWeekScores:
                    if score>=0:
                        a += score
                appendList.append('images/a' + str(a // len(lastWeekScores)) + '.png')

        #achieveList.append([each.name,appendList])
        achieveDict[each.name]=appendList

    a = 'ЦУКЕНГШЩЗХФВЙЬЪЫАПРОЛДЖЭЯЧСМИТБЮ'
    alphabet = [each for each in a]
    alphabet.sort()
    StudAlphabet = []
    for letter in alphabet:
        letterQuery = Student.objects.filter(name__startswith=letter)
        letterList = []
        for each in letterQuery:
        	appendName =  ranks[rankDict[each.name]] + ' ' + each.name
        	letterList.append([appendName,achieveDict[each.name],'images/rabbid' + str(rankDict[each.name]) + '.jpg'])
    

        #if letter == 'Б':
        #    letterList.append(['генерал Батозский',['images/a13.jpg']
        #        ,'images/rabbid9.jpg'])
        if 0 < len(letterList):
            letterList.sort()
            StudAlphabet.append([letter,letterList])

    context = Context({'urlPattern': urlPattern,
                   'clever':clever ,
                   'dumb': dumb,
                   'alphabet':StudAlphabet})
    return HttpResponse(template.render(context))

def addSwarm(request):
    template = loader.get_template('students/swarmAdd.html')
    a = 'ЦУКЕНГШЩЗХФВЙЬЪЫАПРОЛДЖЭЯЧСМИТБЮ'
    alphabet = [each for each in a]
    alphabet.sort()
    StudAlphabet = []
    for letter in alphabet:
        letterQuery = Student.objects.filter(name__startswith=letter)
        letterList = []
        for each in letterQuery:
        	letterList.append([each.name,each.pk])
        if 0 < len(letterList):
            letterList.sort()
            StudAlphabet.append([letter,letterList])

    context = Context({'urlPattern': urlPattern,
                      'alphabet':StudAlphabet})

    return HttpResponse(template.render(context))

def addScore(request):
    studentName = request.POST.get('name',False)
    testName = request.POST.get('test',False)
    mark = request.POST.get('mark',False)
    student = Student.objects.get(name=studentName)
    test = Test.objects.get(name=testName)
    time = (test.minutes+1)*60
    nowTime = datetime.datetime.now()
    passTest = PassedTest.objects.get(student=student,test=test)

    themeName = Test.objects.get(name=testName).theme
    gradeName = Test.objects.get(name=testName).theme.grade


    if (nowTime-passTest.startTime).total_seconds()<time:
        mark = Score(score=mark,student_name=student,theme=themeName,grade=gradeName)
        mark.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('no')

def test(request):
    template = loader.get_template('students/test.html')
    password = list(Passwords.objects.all())
    context = Context({'urlPattern': urlPattern,
                       'passwords':password})
    return HttpResponse(template.render(context))

def passcheck(request):
    N = request.POST.get('name',False)
    P = request.POST.get('password',False)
    template = loader.get_template('students/testChoice.html')
    st = Student.objects.get(name=N)
    studentQ=Passwords.objects.get(student=st)
    if studentQ.password == P:
        passed = PassedTest.objects.filter(student=st)
        tests = Test.objects.filter(theme__grade=st.grade)
        context = Context({'urlPattern': urlPattern,
                       'tests':tests,
                       'passed':passed,
                       'student':N})
        return HttpResponse(template.render(context))
    else:
        template = loader.get_template('students/testfound.html')
        context = Context({'urlPattern': urlPattern})
        return HttpResponse(template.render(context))

def testing(request):
    N = request.POST.get('student',False)
    P = request.POST.get('testName',False)
    student = Student.objects.get(name=N)
    test = Test.objects.get(name=P)
    time = test.minutes
    if not PassedTest.objects.filter(student=student,test=test):
        passed = PassedTest(student=student,test=test)
        passed.save()

    quest = Question.objects.filter(test__name=P)
    template = loader.get_template('students/testing.html')
    context = Context({'urlPattern': urlPattern,
                       'test':P,
                       'time': time,
                       'poll':quest,
                       'student':N})
    return HttpResponse(template.render(context))

def checkapp(request):
    name = request.GET.get('name',False)
    if name:
        student = Student.objects.get(name=name)
        themes = Theme.objects.filter(grade=student.grade)
        subjects = set([each.subject for each in themes])
        if student:
            respond='['
            for each in subjects:

                marksList = []
                themeInThisSubject = Theme.objects.filter(subject=each,grade=student.grade).latest('id')
                marks = Score.objects.filter(student_name__name=name,theme=themeInThisSubject).order_by('-score_date')[:2]
                for everyMark in marks:
                    marksList.append(everyMark.score)
                respond = respond+'["'+each.name+'","'+themeInThisSubject.theme_name+'",'+str(marksList)+']'+','
            respond=respond[:-1]+']'
            return HttpResponse(respond)
        else:
            return HttpResponse('There is no such name in base')
    else:
       return HttpResponse('1')

def cr(request):
    num=request.GET.get('nfc',False)
    #hash = hashlib.md5()
    #hash.update(num)

    if Student.objects.filter(nfcId = num):
    	stud = Student.objects.get(nfcId = num)
        now = datetime.datetime.today()
        nowAgo = now - datetime.timedelta(minutes=45)
        if Journal.objects.filter(checkTime__range=(nowAgo,now),name=stud):
           return HttpResponse('idiot')
        else:
            if Foursquare.objects.filter(student=stud):
                req = requests.post('https://api.foursquare.com/v2/checkins/add?venueId=4c764b3d1b30a093d496f109&m=swarm&v=20130815&broadcast=twitter&oauth_token='+Foursquare.objects.get(student=stud).token)
                #print req.json()
            classSchedule = Schedule.objects.filter(grade=stud.grade)
            dayLessons = classSchedule.filter(weekDay=now.weekday())
            if dayLessons:
                trueVisit = True
                for each in dayLessons:
                    lessonStart = datetime.datetime(now.year,now.month,now.day,each.startHour,each.startMinute,0,0) - datetime.timedelta(minutes=20)
                    if ((now-lessonStart).seconds//60)<65:
                        trueVisit = False
                if trueVisit:
                    return HttpResponse('wrong time')
                visit = Journal(grade=stud.grade,name=stud)
                visit.save()
            else:
                return HttpResponse('wrong day')
    else:
        g = Grade.objects.get(grade_name='NaN')
        newNFC = Student(name='unknown NFC',grade=g,nfcId=num)
        newNFC.save()
    return HttpResponse('respond')

def randomMarks(whatMark, count):
    #print (str(whatMark)+ ' '+ str(count))
    allStudents = Student.objects.all()
    names = []
    for each in allStudents:
        names.append(each.name)
    random.seed()
    luckyTheme = Theme.objects.get(pk=1)
    for each in range(count):
        lucky = random.randint(0,len(names))
        luckyStudent = Student.objects.get(name=names[lucky])
        luckyStudentThemes = Theme.objects.filter(grade=luckyStudent.grade)
        for theme in luckyStudentThemes:
            if theme.hours_count > Score.objects.filter(student_name=luckyStudent,theme=theme):
                break
        newScore = Score(grade=luckyStudent.grade,student_name=luckyStudent,score=whatMark,theme=theme)
        newScore.save()
        #print ('добавлена '+ str(whatMark))
        #print('student name '+luckyStudent.name)
        #print('theme '+theme.theme_name)

def tweetSomething (text):
     APP_KEY = 'StNRV6kswinBGjEaxxftaFv9J'
     APP_SECRET = 'lLkVr0V2kRmEq1jBYfEJ5NnbLCcutJGhUopciSTIOgFeNIT9Ji'
     OAUTH_TOKEN = '56944567-wryXx642TN2AS6x7RcneXFG2HFFuUAhVPP0FxgZqB'
     OAUTH_TOKEN_SECRET = 'JZwaXpaSJCYzHyE1FM1UBu6aHPRygSbiDv4Ykiq8PyAT4'
     #Requires Authentication as of Twitter API v1.1
     twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
     try:
         twitter.update_status(status=text)
         #print 'no tweet'
     except TwythonError as e:
         print e

def tweet(request):

    ronaldo_main_domain_stat = 'http://ua.tribuna.com/cristiano-ronaldo/'
    page = html.parse(ronaldo_main_domain_stat)
    a = page.getroot().find_class('short-statistic').pop()
    t = a.getchildren()
    f= t[1].getchildren()
    goals = f[1].text_content()

    try:
        f = open('ronaldo', 'r')
        newOne = int(goals)
        old = int(f.readline())
        if newOne == old:
            #print('same count of goals')
            f.close()
        else:
            #randomMarks(12,newOne-old)
            #print (str(newOne-old))
            f.close()
            f = open('ronaldo', 'w')
            f.write(goals)
            f.close()
    except:
        f = open('ronaldo', 'w')
        f.write(goals)
        f.close()

    messi_main_domain_stat = 'http://ua.tribuna.com/messi/'
    page = html.parse(messi_main_domain_stat)
    a = page.getroot().find_class('short-statistic').pop()
    t = a.getchildren()
    f= t[1].getchildren()
    goals = f[1].text_content()

    try:
        f = open('messi', 'r')
        newOne = int(goals)
        old = int(f.readline())
        if newOne == old:
            #print('same count of goals')
            f.close()
        else:
            #randomMarks(2,newOne-old)
            #print (str(newOne-old))
            f.close()
            f = open('messi', 'w')
            f.write(goals)
            f.close()
    except:
        f = open('messi', 'w')
        f.write(goals)
        f.close()


    day = datetime.datetime.today()-datetime.timedelta(days=1)
    f = open('workfile', 'r')
    if f.readline()==str(datetime.date.today()):
         f.close()
         return HttpResponse('fuck you')
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
    if thereIsSomeScores==False:
         return HttpResponse('nothing today')
         #tweetingStr = "Вчера не было поставлено ни одной оценки, но это не беда - значит завтра поставим в два раза больше. \n"
     #tweetingStr+="http:\\\vz10.net"

    tweetSomething(tweetingStr)
    return HttpResponse(tweetingStr)

def swarm(request, student_id):
    code=request.GET.get('code',False)
    swarmClientId = 'IUJN41BDKRQPTVGSL0C0RISCIDOG120Q4K4ZGAHHDOBXTRW0'
    swarmClientSecret = 'W0CO0WI5WDCH1NFS5GWRESOTSXZAOL5KWUMI1FID1IMPZE2L'
    req = requests.get('https://foursquare.com/oauth2/access_token?client_id='+swarmClientId+'&client_secret='+swarmClientSecret+'&grant_type=authorization_code&redirect_uri=http://vz10.net/swarm&code='+code)
    #print req.encoding
    a = req.json()

    if 'access_token' in a:
        token = Foursquare(student=Student.objects.get(pk=student_id),token=a['access_token'])
        token.save()
        return HttpResponse("Усе пройшло гарно.")
    if 'error' in a:
        token = Foursquare(student=Student.objects.get(pk=student_id),token=a['error'])
        token.save()
        return HttpResponse("Усе пройшло погано.")







