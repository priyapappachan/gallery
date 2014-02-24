from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from django.db import models
from rec.models import User, Movie, Mrate, Mtags
from django.core.context_processors import csrf
import urllib2
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
import re
import psycopg2
import sys
from operator import itemgetter
from itertools import groupby
from random import choice



def mrecommend(user):
	con = None	
    	con = psycopg2.connect(database='mydb', user='priya')
    	cur = con.cursor()    
    	cur.execute("SELECT movie_id, rating FROM rec_mrate WHERE user_id=%s",[user.id])
    	rows = cur.fetchall() #all the movies rated by user 
    	l = []
    	real_list=[]
    	nei_set=[]	
    	for row in rows:
		cur.execute("SELECT user_id FROM rec_mrate WHERE movie_id=%s AND rating=%s", (row[0], row[1])) 
		rows1 = cur.fetchall() # all the users who liked above movie and rated same as above user.
		l = l + rows1
		real_list.append(rows1)
    	nei_set = list (set.intersection(*map(set, real_list)))	#common neighbour in all list if exists
    	l.sort() #sort the list of neighbours
    	l = list(map(itemgetter(0), groupby(l))) #remove the duplicates
    	i = len(nei_set)
    	for j in range(i, 30):
		nei_set.append(choice(l)) #neighbourhood set of user 1 randomly selected
    	real_list=[]
    	for j in range(0,30):
		cur.execute("SELECT movie_id FROM rec_mrate WHERE user_id=%s", nei_set[j])
		mvs = cur.fetchall()
		real_list = real_list + mvs
	con.close()
	return real_list


def getunicode(soup):
	body=''
  	if isinstance(soup, unicode):
  		soup = soup.replace('\'',"'")
    		soup = soup.replace('&quot;','"')
    		soup = soup.replace('&nbsp;',' ')
    		body = body + soup
  	else:
   		if not soup.contents:
    			return ''
    		con_list = soup.contents
    		for con in con_list:
     			body = body + getunicode(con)
  	return body

def search(movie):
			 
			 movie_search = '+'.join(movie.split())
			 base_url = 'http://www.imdb.com/find?q='
 			 url = base_url+movie_search+'&s=all'
			 title_search = re.compile('/title/ttd+')
			 br = Browser()
			 br.open(url)
			 link = br.find_link(url_regex = re.compile(r'/title/tt.*'))
 			 res = br.follow_link(link)
			 soup = BeautifulSoup(res.read())
			 print soup
 			 info = {}
 			 movie_title = getunicode(soup.find('title'))
 			 info['title'] = movie_title
  			 strng = ""
  			 rate = soup.find('span',itemprop='ratingValue')
 			 rating = getunicode(rate)
 			 info['rating'] = rating
 			 img = soup.find('img', {'itemprop':'image'})['src']
 			 image = getunicode(img)
 			 image = image.split('.jpg')[0]
 			# info['img'] = image
			 des = soup.find('meta',{'name':'description'})['content']
			 descp = getunicode(des)
			 info['description'] = descp
 			 genre=[]
 			 infobar = soup.find('div',{'class':'infobar'})
 			 r = infobar.find('',{'title':True})['title']
  			 genrelist = infobar.findAll('a',{'href':True})
			 for i in range(len(genrelist)-1):
  				 genre.append(getunicode(genrelist[i]))
  				 info['genre'] = genre 
 			 release_date = getunicode(genrelist[-1])
 			 info['date'] = release_date
			 return info		

def start(request): #starting page url set to www.smthn.com/
	if request.method=='GET':
		if  'e' in request.GET:
			return render_to_response('start.html',{'error':'1'},context_instance=RequestContext(request)) #if error pass error code
        	else:
            		return render_to_response('start.html',{},context_instance=RequestContext(request)) #if no error display page
    	else: #method is post
        	user_name=request.POST.get('user_name') #extract data from text field
		password=request.POST.get('password')
		all_users = User.objects.all() # load all users data to an object
		for user in all_users:	#select each users from user set
			if user_name == user.user_name and password == user.user_password: #if user name and password exist authenticate user			
				return HttpResponseRedirect('/%s/home/' % user.id) #set url to /userid
		return HttpResponseRedirect('/?e=1') #if no such user set error code to 1


def signup(request): #sign up page. url/signup/
	if request.method=='GET':
		return render_to_response('signup.html',RequestContext(request)) #if get display page
	else:
		name=request.POST.get('username')
		password = request.POST.get('password')
        	mail = request.POST.get('mail')
		phone = request.POST.get('number') #extraxt data from form fields
		new_user=User(user_name=name,user_password=password,mail_id=mail,phonenumber=phone) #pass data to object
		new_user.save() #commit data to database
		#return render_to_response('initial_rating.html',{'user':new_user},context_instance=RequestContext(request))
		return HttpResponseRedirect('/%s' % new_user.id) #set url to home page /userid

def initial(request,uId):
	if request.method=='GET':
		user = User.objects.get(id=uId)
		return render_to_response('initial_rating.html',{'user':user},context_instance=RequestContext(request))#if get display page
	else:
		
		user = User.objects.get(id=uId)
		troy=request.POST.get('troy_rating')
		nemo=request.POST.get('nemo_rating')
		m = Movie.objects.get(movie_name ='Troy')
		if troy >=0 :
			new_rating = Mrate(user_id=user.id,movie_id=m.movie_id,rating=troy,wlist='y')
			new_rating.save()
		m = Movie.objects.get(movie_name ='Finding Nemo')
		if nemo >=0 :
		#new_rating = Mrate(user_id=user.id,movie_id=m.movie_id,rating=troy,wlist='y')
			new_rating = Mrate(user_id=user.id,movie_id=m.movie_id,rating=nemo,wlist='y')
			new_rating.save()
		user = User.objects.get(id=uId)
		return HttpResponseRedirect('/%s/home/' % user.id)


def home(request,uId): #home page pass user id to ths page
	if  'e' in request.GET:
		code = 1
	else:
		code = None
	user = User.objects.get(id=uId) #get user data to an object
	#real_list = mrecommend(user)
	
	all_models_dict = { #rec val
			"user" : user,
			'error' : code,
			"extra_context" : {"movie1" :Movie.objects.get(id=11),
	                 	          "movie2": Movie.objects.get(id=22),
					   "movie3": Movie.objects.get(id=33),
	                	           }
    			}
	return render_to_response('home.html',all_models_dict,context_instance=RequestContext(request)) #display home page with dictionary context 														instance

def movie (request, uId):
	if 'q' in request.GET:
 		 movie_input = request.GET['q']
		 info = {}
		 try: 
		 	movie = Movie.objects.get(movie_name__iexact = movie_input)	
		 except Movie.DoesNotExist:
			movie = None
		 if movie != None :
			 if movie.description == 'null':
 		 		info = search(movie_input)
				movie.description = info['description']
				movie.save()
				movie.release_date = info['date']
				movie.save()
				movie.imdb_rating = info['rating']
				movie.save()
				
			 else:
				
				info['title'] = movie.movie_name
				info['genre'] = movie.genre
				info['description'] = movie.description
				info['date'] = movie.release_date
				info['rating'] = movie.imdb_rating
				
		 else:
			
			info = search(movie_input)
			movie = Movie(movie_name = movie_input,genre = info['genre'],description = info['description'],release_date = info['date'], imdb_rating = info['rating'])
			movie.save()
							
			
	 	 user = User.objects.get(id=uId)
		 
		 try: 
			
		 	movie_rate = Mrate.objects.get(user_id = user.id, movie_id = movie.id)	
		 except Mrate.DoesNotExist:
			movie_rate = None
		 if movie_rate != None:
			rated_row = Mrate.objects.get(user_id = user.id,movie_id = movie.id)
			return render_to_response('moviedetails.html',{'Movie':info,'rated_row':rated_row},context_instance=RequestContext(request))
		 else: 
			return render_to_response('moviedetails_rate.html',{'Movie':info,'user':user},context_instance=RequestContext(request))
	else:
			user = User.objects.get(id=uId)
			
			user_rating = request.POST.get('r')
			select = request.POST.get('wlist')
			if select == '1':
				o1 = Mrate(user_id = user.id,movie_id=111,rating=user_rating,wlist = 'y')
				o1.save()
			if select == '2':
				o1 = Mrate(user_id = user.id,movie_id=movie.id,rating = 0,wlist = 'n')
				o1.save()			
			return HttpResponseRedirect('/%s/home/' % user.id)
	
	#return HttpResponseRedirect('/%s/?e=1' % uId) #set url to /userid			
 	

#done by jisa
def change_password(request):
	#user = User.objects.get(user_password=request.POST.get('old_password')
	#user.user_password=request.POST.get('new_password')
	#user.save()
	User.objects.filter(user_password=request.POST.get('old_password')).update(user_password=request.POST.get('new_password'))
	#cant save
	return HttpResponseRedirect(profile.html)
				 
		
