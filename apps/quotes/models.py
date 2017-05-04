from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
from datetime import date, datetime
from time import strptime
Name_Regex = re.compile(r'^[A-Za-z ]+$')

# Create your models here.
class userManager(models.Manager):
    def validate (self, postData):
        errors = []
        if len(postData['name']) < 2:
            errors.append("Name needs to be more than 1 letter")
        if not Name_Regex.match(postData['name']):
            errors.append("name can only be letters")
        if len(postData["alias"])==0:
            errors.append("Please insert Your Alias")
        elif len(postData["alias"])<2:
            errors.append("First Name needs to be 2-45 characters")
        if len(User.objects.filter(email = postData['email'])) > 0:
            errors.append("Username already exists")
        if len(postData["email"])==0:
            errors.append("Please insert an email address in the bracket")
        elif not re.search(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+.[a-zA-Z]+$', postData["email"]):
            errors.append("Please insert a valid email address")
        if postData['password'] != postData['confirm_password']:
            errors.append("Your passwords don't match")
        if len(postData['password']) < 8:
            errors.append("Password needs to be more than 8 letters")
        if str(date.today()) < str(postData['dob']):
            errors.append("Please input a valid Date. Note: DOB cannot be in the future.")
        if len(errors) == 0:
            #create the user
            newuser = User.objects.create(name= postData['name'], alias= postData['alias'], email= postData['email'], dob= postData['dob'], password= bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()))
            return (True, newuser)
        else:
            return (False, errors)

    def login(self, postData):
        errors = []
        if 'email' in postData and 'password' in postData:
            try:
                print 50*('8')
                user = User.objects.get(email = postData['email'])#userManage acceses the database using .get (finds that one user's object)
            except User.DoesNotExist: #if the user doesnt exist from the .get(.get returns nothin, this 'except' prevents an error message)
                print 50*('4')
                errors.append("Sorry, please try logging in again")
                return (False, errors)
        #password field/check
        pw_match = bcrypt.hashpw(postData['password'].encode(), user.password.encode())
        print 10*"3", user.password
        if pw_match == user.password:
            return (True, user)
        else:
            errors.append("Sorry please try again!!!!")
            return (False, errors)

class User(models.Model):
    name = models.CharField(max_length=45)
    alias = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100)
    email= models.CharField(max_length=45, blank=True, null=True)
    dob= models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = userManager()

class quoteManager(models.Manager):
    def quoteval(self,postData, id):
        curr_user = User.objects.get(id=id)
        errors=[]
        if len(postData['quoteby'])<3:
            errors.append("Quoteby Cannot be less than 2 characters!")
        if len(postData['content'])<10:
            errors.append("Message cannot be less than 10 characters!")
            return (False, errors)
        else:
            quotes = Quote.objects.create(content= postData['content'], quoteby=postData['quoteby'], contributor= curr_user)
            # addtofave= quotes.favourite.add(curr_user) #after you created the new contributor you need add the contributor object into the favourite M2M for it to recognize id matching
            print "Successfully created new quote", quotes
            return (True),

        # if len(postData['content'])<10:
        #     errors.append("Quote cannot be less than 10 characters!")
        # if len(errors) == 0:

    def addfav(self, id, quote_id):
        if len(Quote.objects.filter(id=quote_id).filter(favourite=id))>0:
            return {'errors':'You already added this favourite'}
        else:
            adder = User.objects.get(id=id)
            print "adder", adder
            addfav= Quote.objects.get(id = quote_id)
            print "adder", addfav
            addfav.favourite.add(adder)
            print "succesfully added into fav:"
            return {}

    def removefav(self, id, quote_id):
        try:
            removefav= Quote.objects.get(id=quote_id)
        except Quote.DoesNotExist:
            return {'errors':'Quote does not exist'}
        removeuser= User.objects.get(id=id)
        print "removeuser:", removeuser
        removequote= Quote.objects.get(id=quote_id)
        print "remove quote:", removequote
        removed_quote = removequote.favourite.remove(removeuser)
        print "succesfully added into fav:", removed_quote
        return {}


class Quote(models.Model):
    quoteby= models.CharField(max_length=100)
    content= models.TextField(max_length=1000)
    contributor= models.ForeignKey(User, related_name= "quoter")
    favourite= models.ManyToManyField(User, related_name="favor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = quoteManager()
