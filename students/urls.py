from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from students import views
from students.models import Theme, Score

urlpatterns = patterns('', url(r'^$',views.index,name='index'),
	url(r'choice/$',views.choice,name='choice'),
	url(r'about/$',views.about,name='about'),
	url(r'contacts/$',views.contacts,name='contacts'),
	url(r'^(?P<theme_id>\d)/(?P<sort_id>\d)/$',views.diagram, name='diagram'),
    url(r'^(?P<theme_id>\d\d)/(?P<sort_id>\d)/$',views.diagram, name='diagram'),
    url(r'cron/$',views.cr,name='cr'),
    url(r'achieve/$',views.achieve,name='achieve'),
    url(r'test/$',views.test,name='test'),
    url(r'passcheck/$',views.passcheck,name='passcheck'),
    url(r'testing/$',views.testing,name='testing'),
    url(r'addscore/$',views.addScore,name='addScore'),
    url(r'checkapp/$',views.checkapp,name='checkapp'),
    url(r'tweet/$',views.tweet,name='tweet'),
    url(r'visitChoice/$',views.visitChoice,name='visitChoice'),
    url(r'visit/(?P<class_id>\d)/$',views.visit, name='visit'),
    url(r'semestr/(?P<class_id>\d)/(?P<sort_id>\d)$',views.semestr, name='semestr'),
    url(r'swarm/(?P<student_id>\d)/$',views.swarm,name='swarm'),
    url(r'swarm/(?P<student_id>\d\d)/$',views.swarm,name='swarm'),
    url(r'swarm/(?P<student_id>\d\d\d)/$',views.swarm,name='swarm'),
    url(r'addswarm/$',views.addSwarm,name='addSwarm'),
    url(r'kharkiv/$',views.kharkiv,name='kharkiv'),
    )