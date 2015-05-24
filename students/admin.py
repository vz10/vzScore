from django.contrib import admin
from students.models import Student, Score, Theme, Grade, Achieves, Passwords, Test, PassedTest, Question, Subject, Journal, Schedule, Foursquare


class ScoreAdmin(admin.ModelAdmin):
    fieldsets = [('Theme', {'fields': ['grade','theme', 'student_name', 'score']}),
                 ('Date', {'fields': ['score_date'], 'classes': ['collapse']})]
    list_display = ('student_name', 'theme', 'score', 'grade','score_date')
    list_filter = ['theme','grade']
    date_hierarchy = 'score_date'

class JournalAdmin(admin.ModelAdmin):
    fieldsets = [('Theme', {'fields': ['grade','name',]}),
                 ('Date', {'fields': ['checkTime'], 'classes': ['collapse']})]
    list_display = ('name','grade','checkTime')
    list_filter = ['grade']

admin.site.register(Score, ScoreAdmin)


class ThemeAdmin(admin.ModelAdmin):
    list_display = ('theme_name', 'grade', 'hours_count', 'subject', 'end')
    list_filter = ['grade']

class StudentsAdmin(admin.ModelAdmin):
    list_display = ('name','grade','nfcId','pk')
    list_filter = ['grade']

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('grade','weekDay','startHour','startMinute')
    list_filter = ['grade']

class PassedAdmin (admin.ModelAdmin):
    list_display = ('student','test','startTime')
    list_filter = ['student']

class TestAdmin (admin.ModelAdmin):
    list_display = ('name', 'theme', 'minutes')
    list_filter = ['name']

class passwrodsAdmin(admin.ModelAdmin):
    list_display = ('student','password')
    list_filter = ['student']

class hackerAdmin(admin.ModelAdmin):
    list_display = ('name', 'counte')
    list_filter = ['name']

class swarmAdmin(admin.ModelAdmin):
    list_display = ('student', 'token')
    list_filter = ['student']

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Student, StudentsAdmin)
admin.site.register(Grade)
admin.site.register(Foursquare,swarmAdmin)
admin.site.register(Achieves)
admin.site.register(Passwords,passwrodsAdmin)
admin.site.register(Test,TestAdmin)
admin.site.register(PassedTest, PassedAdmin)
admin.site.register(Question)
admin.site.register(Subject)
admin.site.register(Journal,JournalAdmin)
admin.site.register(Schedule,ScheduleAdmin)

