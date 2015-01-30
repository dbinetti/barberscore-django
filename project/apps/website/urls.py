from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^contests/$', views.ContestList.as_view(), name='contest-list'),
    url(r'^contests/(?P<slug>[a-zA-Z0-9-]+)/$', views.ContestDetail.as_view(), name='contest-detail'),

    url(r'^districts/$', views.DistrictList.as_view(), name='district-list'),
    url(r'^districts/(?P<slug>[a-zA-Z0-9-]+)/$', views.DistrictDetail.as_view(), name='district-detail'),

    url(r'^singers/$', views.SingerList.as_view(), name='singer-list'),
    url(r'^singers/(?P<slug>[a-zA-Z0-9-]+)/$', views.SingerDetail.as_view(), name='singer-detail'),

    url(r'^choruses/$', views.ChorusList.as_view(), name='chorus-list'),
    url(r'^choruses/(?P<slug>[a-zA-Z0-9-]+)/$', views.ChorusDetail.as_view(), name='chorus-detail'),

    url(r'^quartets/$', views.QuartetList.as_view(), name='quartet-list'),
    url(r'^quartets/(?P<slug>[a-zA-Z0-9-]+)/$', views.QuartetDetail.as_view(), name='quartet-detail'),

]
