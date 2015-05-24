from students.models import Theme, Score, Student, Grade, Student_achieves
import datetime

weekAgo = datetime.date.today() - datetime.timedelta(days=7)

def check_base():
    #weekScores = Score.objects.filter(score_date__gte=weekAgo)
    #weekAgo = Score.objects.all()
    #students = Student.objects.all()
    for each in students:
        pass
        #stud = weekScores.filter(student_name = each.name)
