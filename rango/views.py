from rango.models import Page
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime

def index(request):

	# query the database for a list of ALL categories currently stored
	# order the categories by number of likes in descending order
	# retrieve only the top 5 or all if <5
	# place the list in context_dict
	# context_dict will be passed to the template engine
	request.session.set_test_cookie()
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}

	# call the helper function to handle the cookies
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	# obtain response object early so we can add cookie information
	response = render(request, 'rango/index.html', context=context_dict)
	# return the response back to the user, updating any cookies that need changed
	return response

def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()

	context_dict = {}
	# prints out whether the method is a GET or POST
	print(request.method)
	# prints out the user name, if no one is logged in it prints 'AnonymousUser'
	print(request.user)

	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	response = render(request, 'rango/about.html', context=context_dict)
	return response

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

@login_required
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

@login_required
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

def user_login(request):
	# if the request is a HTTP POST, try to pull out the relevant information
	if request.method == 'POST':
		# gather the username and password provided by the user
		# this information is obtained from the login form
		# we use request.POST.get('variable') as opposed to 
		# request.POST['variable'], because the request.POST.get('variable')
		# returns None if the value does not exist, while the other method will raise a KeyError Exception	
		username = request.POST.get('username')
		password = request.POST.get('password')

		# use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is
		user = authenticate(username=username, password=password)

		# if we have a User object, the details are correct
		# if None, no user with matching credentials was found
		if user:
			# is the account active? it could have been disabled
			if user.is_active:
				# if the account is valid and active, we can log the user in
				# we'll send the user back to the homepage
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				# an inactive account was used - no logging in!
				return HttpResponse("Your Rango account is disabled")
		else:
			# bad login details were provided so no logging in!
			print("Invalid login details: {0}, {1}".format(username, password))
			#context_dict = {'bad_details': "Invalid login details supplied."}
			#return render(request, 'rango/login.html', context_dict)
			return HttpResponse("Invalid login details supplied.")			

	# the request is not a HTTP POST, so display the login form
	# this scenario would most likely be a HTTP GET
	else:
		# no context variables to pass to the template system, hence
		# the blank dictionary object
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
	# since we know the user is logged in, we can now just log them out
	logout(request)
	# take the user back to the homepage
	return HttpResponseRedirect(reverse('index'))

# this is not a view, just a helper function because it doesn't return a response object
# this helper function takes request and response objects because we want to be able to access 
# the incoming cookies from the request and add or update cookies in the response

def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val

def visitor_cookie_handler(request):
	# get the no. of visits to the site
	# if the cookie exists, the value returned is cast to an integer
	# if the cookie doesn't exist, the the default value of 1 is used
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
	
	# if it's been more than a day since the last visit...
	if(datetime.now() - last_visit_time).seconds > 0:
		visits = visits + 1
		# update the last visit cookie now that we have updated the count
		# store session cookies from the server side in the request.session[] dictionary
		request.session['last_visit'] = str(datetime.now())
	else:
		# set the last visit cookie
		request.session['last_visit'] = last_visit_cookie

	# update/set the visits cookie
	request.session['visits'] = visits




