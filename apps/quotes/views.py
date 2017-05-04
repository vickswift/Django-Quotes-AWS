from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from .models import User, Quote
# Create your views here.

def index(request):
    return render(request, 'quotes/index.html')

def register(request):
    if request.method == 'GET':
        return redirect ('/')
    newuser = User.objects.validate(request.POST)
    print newuser
    if newuser[0] == False:
        for each in newuser[1]:
            messages.error(request, each) #for each error in the list, make a message for each one.
        return redirect('/')
    if newuser[0] == True:
        messages.success(request, 'Well done')
        request.session['id'] = newuser[1].id
        return redirect('/quotes')

def login(request):
    if 'id' in request.session:
        return redirect('/quotes')
    if request.method == 'GET':
        return redirect('/')
    else:
        user = User.objects.login(request.POST)
        print user
        if user[0] == False:
            for each in user[1]:
                messages.add_message(request, messages.INFO, each)
            return redirect('/')
        if user[0] == True:
            messages.add_message(request, messages.INFO,'Welcome, You are logged in!')
            request.session['id'] = user[1].id
            return redirect('/quotes')


def quotes(request):
    if 'id' not in request.session:
        return redirect ("/")
    quotes= Quote.objects.all().exclude(favourite__id=request.session['id'])
    print "quotes:", quotes
    favourites= Quote.objects.filter(favourite__id=request.session['id'])
    user= User.objects.get(id=request.session['id'])
    notfav= Quote.objects.exclude(favourite__id=request.session['id'])
    print "notfav:", notfav
    others= Quote.objects.all().exclude(favourite__id=request.session['id'])

    # others = User.objects.all().exclude(quotes__id=request.session['id'])
    context = {
        "user": user,
        "quotes": quotes,
        "favourites": favourites,
        "others": others
    }
    return render(request, 'quotes/quotes.html', context)

def createquote(request):
    if request.method != 'POST':
        messages.error(request, "Nice Try... please insert item in Field")
        return redirect ("/quotes")
    newquote= Quote.objects.quoteval(request.POST, request.session["id"])
    print 80 * ('*'), newquote
    if newquote[0]== False:
            for each in newquote[1]:
                messages.add_message(request, messages.INFO, each)
            return redirect('/quotes')
    # if 'errors' in newquote:
    #     messages.error(request, newquote['errors'])
    #     return redirect('/quotes')
    else:
        return redirect('/quotes')

def show(request, quote_id):
    creator= User.objects.filter(quoter__id= quote_id)
    quotes= Quote.objects.filter(favourite=creator)
    count= Quote.objects.filter(favourite=creator).count()
    print quotes
    # except quote.DoesNotExist:
    #     messages.info(request,"quotes Not Found")
    #     return redirect('/quotes')
    context={
        "count": count,
        "quotes": quotes,
        "creator": creator
        # "others": User.objects.filter(joiner__id=quotes.id).exclude(id=quotes.creator.id),
    }
    return render(request, 'quotes/showquote.html', context)

def addfav(request, quote_id):
    if request.method != "POST":
        messages.error(request,"What Item?")
        return redirect('/')
    else:
        add_fav= Quote.objects.addfav(request.session['id'],quote_id)
        if 'errors' in add_fav:
            messages.error(request, add_fav['errors'])
        return redirect('/quotes')

def removefav(request, quote_id):
    if request.method != "GET":
        messages.error(request,"Nice Try, Can't remove like this!")
        return redirect('/')
    else:
        remove_fav= Quote.objects.removefav(request.session['id'],quote_id)
        if 'errors' in remove_fav:
            messages.error(request, remove_fav['errors'])
            return redirect('/quotes')
        else:
            return redirect('/quotes')

#
# def delete(request, id):
#     try:
#         target= quotes.objects.get(id=id)
#     except quotes.DoesNotExist:
#         messages.info(request,"Message Not Found")
#         return redirect('/quotes')
#     target.delete()
#     return redirect('/quotes')
# #

def logout(request):
    if 'id' not in request.session:
        return redirect('/')
    print "*******"
    print request.session['id']
    del request.session['id']
    return redirect('/')
