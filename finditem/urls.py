from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^search_api', views.search_api),
	url(r'^search', views.search),
	url(r'^$', views.main),
]
