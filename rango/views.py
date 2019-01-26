from rango.models import Page
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category

def index(request):

	# query the database for a list of ALL categories currently stored
	# order the categories by number of likes in descending order
	# retrieve only the top 5 or all if <5
	# place the list in context_dict
	# context_dict will be passed to the template engine

	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}

	# render the response and send it back
	return render(request, 'rango/index.html', context_dict)

def about(request):
	context_dict = {'boldmessage': "This tutorial has been put together by Caitlin"}
	return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
	# create a context dictionary which we can pass
	# to the template rendering engine
	context_dict = {}

	try:
		# can we find a category name slug with the given name?
		# if we can't, the .get() method raises a DoesNotExist exception
		# so the .get() ,ethod returns one model instance or raises an exception
		category = Category.objects.get(slug=category_name_slug)

		# retrieve all the associated pages
		# note that filter() will return a list of page objects or an empty list
		pages = Page.objects.filter(category=category)

		# adds our results list to the template context under name pages
		context_dict['pages'] = pages
		# we also add the category object from 
		# the database to the context dictionary
		# we'll use this in the template to verify that the category exists
		context_dict['category'] = category
	except Category.DoesNotExist:
		# don't do anything - template will display the no category message for us
		context_dict['category'] = None
		context_dict['pages'] = None

	# go render the response and return it to the client
	return render(request, 'rango/category.html', context_dict)


