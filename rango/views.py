from rango.models import Page
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

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
	# prints out whether the method is a GET or POST
	print(request.method)
	# prints out the user name, if no one is logged in it prints 'AnonymousUser'
	print(request.user)
	return render(request, 'rango/about.html', {})

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

def add_category(request):
	form = CategoryForm()

	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# save the new category to the database
			cat = form.save(commit=True)
			# now that the category is saved 
			# we could give a confirmation message
			# but since the most recent category added is on the index page
			# then we can direct the user back to the index page
			return index(request)
		else:
			# the supplied form contains errors -
			# just print them to the terminal
			print(form.errors)

	# will handle the bad form, new form, or no form supplied cases
	# render the form with error messages (if any)
	return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		# Have we been provided with a valid form?
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
			return show_category(request, category_name_slug)
		else:
			# the supplied form contains errors -
			# just print them to the terminal
			print(form.errors)

	context_dict = {'form':form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	# a boolean value for telling the template whether 
	# the registration was successful
	# set to false initially 
	# code changes value to true when registration succeeds
	registered = False

	# if it's a HTTP POST, we're interested in processing form data
	if request.method == 'POST':
		# attempt to grab the information from the raw form information
		# note that we make use of both UserForm and UserProfileForm
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		#If the 2 forms are valid:
		if user_form.is_valid() and profile_form.is_valid():
			#save the user's form data to the database
			user = user_form.save()

			# now we hash the password with the set_password method
			# once hashed, we can update the user object
			user.set_password(user.password)
			user.save()

			# now sort out the UserProfile instance
			# since we need to set the user attribute ourselves,
			# we set commit = False. this delays saving the model 
			# until we're ready, to avoid integrity problems

			profile = profile_form.save(commit=False)
			profile.user = user

			# did the user provide a profile picture?
			# if so, we need to get it from the input form and 
			# put it in the UserProfile model
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# now we save the UserProfile model instance 
			profile.save()
			# update our variable to indicate that the template registration was successful
			registered=True
		else:
			# invalid form or forms 
			# print problems to the terminal
			print(user_form.errors, profile_form.errors)
	else:
		# not a HTTP POST, so we render our form using 2 ModelForm instances
		# these forms will be blank, ready for user input
		user_form = UserForm()
		profile_form = UserProfileForm()

	# render the template depending on the context
	return render(request,
				'rango/register.html',
				{'user_form': user_form,
				'profile_form': profile_form,
				'registered': registered})




