from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    # construct a dictionary to pass to the template engine as its context
    # note the key boldmessage is the same as {{ boldmessage }} in the template!
    # Crunchy, creamy text originates here but is rendered in the template
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage': "This tutorial has been put together by Caitlin"}
    return render(request, 'rango/about.html', context=context_dict)



