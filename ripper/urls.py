from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.chooseArea, name='choose area'),
    url(r'^analyze/$', views.analyze, name='analyze'),

]