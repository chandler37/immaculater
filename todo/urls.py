from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    url(r'^fivehundred1423457234$', views.five_hundred, name='five_hundred'),
    url(r'^account$', views.account, name='account'),
    url(r'^cli$', views.update_todolist, name='update_todolist'),
    url(r'^view/(?P<slug>.*)$', views.view, name='view'),
    url(r'^action/(?P<uid>-?\d+)$', views.action, name='action'),
    url(r'^context/(?P<uid>-?\d+)$', views.context, name='context'),
    url(r'^contexts$', views.contexts, name='contexts'),
    url(r'^dl$', views.dl, name='dl'),
    url(r'^weekly_review$', views.weekly_review, name='weekly_review'),
    url(r'^about$', views.about, name='about'),
    url(r'^share$', views.share, name='share'),
    url(r'^shortcuts$', views.shortcuts, name='shortcuts'),
    url(r'^project/(?P<uid>-?\d+)$', views.project, name='project'),
    url(r'^projects$', views.projects, name='projects'),
    url(r'^api$', views.api, name='api'),
    url(r'^slackapi$', views.slackapi, name='slackapi'),
    url(r'^help$', views.help, name='help'),
    url(r'^login$', views.login, name='login'),
    url(r'^txt(\.(?P<the_view_filter>.*)|)$', views.as_text, name='as_text'),
    url(r'^text$', views.as_text2, name='as_text2'),
    url(r'^search$', views.search, name='search'),
    url(r'^privacy.html$', views.privacy, name='privacy'),
    url(r'^v1/create_jwt$', views.create_jwt, name='create_jwt'),
    url(r'^mergeprotobufs$', views.mergeprotobufs, name='mergeprotobufs'),
]

if settings.USE_ALLAUTH:
    urlpatterns.append(
        url(r'^discordapi$', views.discordapi, name='discordapi'))
