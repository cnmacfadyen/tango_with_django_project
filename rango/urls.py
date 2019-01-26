from django.conf.urls import url
from rango import views

# look for any sequence of alphanumeric characters after rango/category/.../
# (\w) or hyphens (\-), matching as many as we like ([ ]+)
# character sequence will then be stored in the category_name_slug parameter
# and passed to views.show_category()

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/$', 
		views.show_category, name='show_category'),
]