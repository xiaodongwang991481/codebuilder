from django.conf.urls import url

from codebuilder.api.accounts import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
]
