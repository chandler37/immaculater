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
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import RedirectView
from jwt_auth.views import obtain_jwt_token
import oauth2_provider.views as oauth2_views
from todo import views

urlpatterns = [
    url(r'^todo/', include('todo.urls')),
    url(r'^$', RedirectView.as_view(url='/todo'), name='go-to-todo'),
    url(r'^admin/', admin.site.urls),
    url(r'^slack/', include('django_slack_oauth.urls')),
    url(r'^v1-api-token-auth$', obtain_jwt_token),
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

if settings.BE_AN_OAUTH_PROVIDER:
    # OAuth2 provider endpoints
    oauth2_endpoint_views = [
        url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
        url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
        url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
    ]

    def _superuser(u):
        return u.is_superuser and u.is_active

    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        url(r'^applications/$',
            user_passes_test(_superuser)(oauth2_views.ApplicationList.as_view()),
            name="list"),
        url(r'^applications/register/$',
            user_passes_test(_superuser)(oauth2_views.ApplicationRegistration.as_view()),
            name="register"),
        url(r'^applications/(?P<pk>\d+)/$',
            user_passes_test(_superuser)(oauth2_views.ApplicationDetail.as_view()),
            name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$',
            user_passes_test(_superuser)(oauth2_views.ApplicationDelete.as_view()),
            name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$',
            user_passes_test(_superuser)(oauth2_views.ApplicationUpdate.as_view()),
            name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        url(r'^authorized-tokens/$',
            user_passes_test(_superuser)(oauth2_views.AuthorizedTokensListView.as_view()),
            name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$',
            user_passes_test(_superuser)(oauth2_views.AuthorizedTokenDeleteView.as_view()),
            
            name="authorized-token-delete"),
    ]

    urlpatterns += [
        # OAuth 2 endpoints:
        url(r'^o/', include(oauth2_endpoint_views, namespace="oauth2_provider")),
        url(r'^api/hello', views.DLCApiEndpoint.as_view()),
    ]
