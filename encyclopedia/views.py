from dataclasses import fields
from operator import truediv
import random
from django.shortcuts import render
from django.http import HttpResponse
from markdown2 import Markdown
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse


from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows': 10}), initial="Write content here")
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

pages = util.list_entries() #might be useless

# take user to random page
def randomPage(request):
    # gets a random object from a list
    random_page = random.choice(util.list_entries())
    # redirects to entry
    return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs = {'title':random_page}))

# edint entry's content in a textarea
def edit(request, title):
    entryPage = util.get_entry(title)
    if entryPage is None:
        return  render(request, "encyclopedia/doesNotExist.html")
    # create new form an populate it with existing content
    form = NewEntryForm()
    form.fields["title"].initial = title
    form.fields["title"].widget = forms.HiddenInput() # cannot edit the title, so hide it
    form.fields["text"].initial = entryPage
    form.fields["edit"].initial = True
    # renders newPage.html were changes can be saved
    return render(request, "encyclopedia/newPage.html", {
        "form":form,
        "edit": form.fields["edit"].initial,
        "title": form.fields["title"].initial
    })

# allow user to create a new entry in the wiki
def newPage(request):
    # if the user submitted the form
    if request.method == "POST":
        form = NewEntryForm(request.POST) # fill the form with their submission
        if form.is_valid(): # server side form check
            # get data from submitted form
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            # if entry doesn't exist or we are editing a page we save the page and redirect to the entry's page
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,text) 
                return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs = {'title':title}))
            else:
                # render section of newPage.html saying page already exists
                return render(request, "encyclopedia/newPage.html",{
                    "form": form,
                    "existing": True, # flag
                    "entry": title
                })
        else: 
            # display invalid form to user
            return render(request, "encyclopedia/newPage.html", {
                "form": form,
                "existing": False
            })

    # request method is not POST, render new form
    else:
        return render(request, "encyclopedia/newPage.html", {
        "form": NewEntryForm(),
        "existing": False
    })

# type a query into the search box in the sidebar to search for an encyclopedia entry
def search(request):
    query = request.GET.get('q','') #store what the user typed into the search bar
    # if the entry exists, redirect user to the entry's page
    if (util.get_entry(query) is not None):
        #kwargs passes query as the wiki/<str:title> param
        return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs = {'title':query})) 
    else:   # if query doesn't match an existing entry, display list of entries with the query as a substring
        entry_list = []
        for entry in util.list_entries():
            if query.upper() in entry.upper():
                entry_list.append(entry)          
        return render(request, "encyclopedia/index.html", {
        "search": True, # used to alter index html of entry lists 
        "query": query,
        "list": entry_list
    })

#renders a list of all entries with clickable links
def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

#takes a GET request and wiki/<str:title> param to render an entry page
def entry(request, title):
    #get entry info and display it as html
    if util.get_entry(title) is not None:
        an_entry = util.get_entry(title)
        markdowner = Markdown()
        return render(request, "encyclopedia/entries.html", {
            "content":markdowner.convert(an_entry), 
            "title": title
        })
    else:
        #if entry is NONE display the doesNotExit page
        return render(request, "encyclopedia/doesNotExist.html")



