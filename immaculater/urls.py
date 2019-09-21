"""immaculater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from jwt_auth.views import obtain_jwt_token
from todo import views

urlpatterns = [
    url(r'^todo/', include('todo.urls')),
    url(r'^$', RedirectView.as_view(url='/todo'), name='go-to-todo'),
    url(r'^admin/', admin.site.urls),
    url(r'^slack/', include('django_slack_oauth.urls')),
    url(r'^v1-api-token-auth$', obtain_jwt_token),
    url(r'^overload-phasers$', views.overload_phasers),
]
if settings.USE_ALLAUTH:
    urlpatterns += [
        url(r'^accounts/', include('allauth.urls')),
    ]
else:
    urlpatterns += [
        url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
        url(r'^accounts/logout/$', views.LogoutView.as_view(), name='logout'),
    ]
