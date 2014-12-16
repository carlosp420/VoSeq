from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^browse/$', views.browse, name='browse'),
    url(r'^search/$', views.search, name='search'),
    url(r'^p/(?P<voucher_code>.+)/$', views.show_voucher, name='show_voucher'),
    url(r'^s/(?P<voucher_code>.+)/(?P<gene_code>.+)/$', views.show_sequence, name='show_sequence'),
)
