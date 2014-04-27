from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from django.db import models
from rec.models import User, Movie, Mrate, Mtags, Session, Book, Brate, Btags, Friend
from django.core.context_processors import csrf
import urllib2, urllib
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
import re
import psycopg2
import sys
from operator import itemgetter
from itertools import groupby
from random import choice
from cPickle import loads, dumps
from django.views.decorators.cache import cache_control

def movieRecommend(user):
	con = None	
    	con = psycopg2.connect(database='mydb', user='priya')
    	cur = con.cursor()    
    	cur.execute("SELECT movie_id, rating FROM rec_mrate WHERE user_id=%s ORDER BY rating DESC",[user.id])
	rows = cur.fetchall() #all the movies rated by user 
	l = []
	real_list=[]
	i=0
	j=0
	temp_list=[]

	nei_set=[]	
	for row in rows:
		cur.execute("SELECT user_id,rating FROM rec_mrate WHERE movie_id=%s AND rating=%s AND user_id <> %s ORDER BY rating DESC", 
		(row[0], row[1], user.id)) 
		rows1 = cur.fetchall() # all the users who liked above movie and rated same as above user.
		i=i+1
		real_list.append(rows1)

	l=real_list
	for j in range(0,i):
		nei_set = list (set.intersection(*map(set, real_list)))
		if len(nei_set) < 10:
			real_list.pop()
			continue
		else:
			real_list.pop()		
			break

	#nei_set.sort(reverse=True,key=lambda element:element[1])
	neighbours = map(itemgetter(0),nei_set);		
	con.close()
	return neighbours

def bookRecommend(user):
	con = None	
    	con = psycopg2.connect(database='mydb', user='priya')
    	cur = con.cursor()    
    	cur.execute("SELECT isbn FROM rec_brate WHERE user_id=%s ORDER BY rating DESC",[user.id])
	rows = cur.fetchall() #all the movies rated by user 

	l=[]

	for row in rows:
		cur.execute("SELECT user_id FROM rec_brate WHERE isbn=%s and user_id <> %s ORDER BY rating DESC", (row[0],user.id)) 
		rows1 = cur.fetchall() # all the users who liked above movie and rated same as above user.
		
		l = l + rows1
	l.sort() #sort the list of neighbours
	l = list(map(itemgetter(0), groupby(l)))
	return l
	
def searchMovie(movie):
		 movie_search = '+'.join(movie.split())
		 base_url = 'http://www.imdb.com/find?q='
 		 url = base_url+movie_search+'&s=all'
		 title_search = re.compile('/title/ttd+')
		 br = Browser()
		 br.open(url)
		 link = br.find_link(url_regex = re.compile(r'/title/tt.*'))
 		 res = br.follow_link(link)
		 soup = BeautifulSoup(res.read())
 		 info = {}
 		 movie_title = getunicode(soup.find('title'))
		 movie_title = movie_title.split(' - IMDb')[0]
		 print movie_title
 		 info['title'] = movie_title
		 try:
  		 	rate = soup.find('span',itemprop='ratingValue')
			rating = getunicode(rate)
			rating = rating[:5]
 		 	info['rating'] = rating 
		 except :
			info['rating']='Not available'	
 		
 		 
		 try :
			img = soup.find('img', {'itemprop':'image'})['src']
		 except  :
			return 1
 		 image = getunicode(img)
 		 info['image'] = image
		 try :
			des = soup.find('meta',{'name':'description'})['content']
		 except  :
			return 1
		 
		 descp = getunicode(des)
		 info['description'] = descp
 		 genre=[]
 		 infobar = soup.find('div',{'class':'infobar'})
 		 try :
			r = infobar.find('',{'title':True})['title']
		 except  :
			return 1
  		 genrelist = infobar.findAll('a',{'href':True})
		 for i in range(len(genrelist)-1):
  			genre.append(getunicode(genrelist[i]))
		 gnre =""
		 for gnr in genre:
			gnre = gnre + str(gnr) + ','
		 gnre = gnre[:-1] 
  		 info['genre'] = gnre 
 		 release_date = getunicode(genrelist[-1])
 		 info['date'] = release_date
		 return info
def searchBook(book):
		book = str(book)
		book_search = '+'.join(book.split())
		base_url = 'http://www.goodreads.com/search?utf8=%E2%9C%93&q='
		url = base_url+book_search+'&search_type=books'
		title_search = re.compile('/book/show/')
		br = Browser()
		br.open(url)
		link = br.find_link(url_regex = re.compile(r'/book/show/*'))
		res = br.follow_link(link)
		soup = BeautifulSoup(res.read())
		print 'hello world'
		while True:

			isb = soup.find('span', itemprop="isbn")
			if not isb:
				newBook = soup.find('div',{'class':'otherEdition'})
				try :
 					Book = newBook.find('a',{'href':True})['href']
				except :
					return 1
				link =br.find_link(url_regex = re.compile(Book))
				res = br.follow_link(link)
				soup = BeautifulSoup(res.read())
	
			else :
				break
		info = {}

		isb = soup.find('span', itemprop="isbn")
		isbn = getunicode(isb)
		info['isbn']=isbn
		author = getunicode(soup.find('title'))
		start = ' by '
		end = ' Reviews'
		author = author[author.find(start)+4:author.find(end)-2]
		book_title = getunicode(soup.find('h1'))
		info['author'] = author
		info['title'] = book_title
		try :
			descri = soup.find('div',id="description")
		except :
					return 1
		des = getunicode(descri)
		start = '...more'
		end  = '(less)'
		des = des[des.find(start)+7:des.find(end)]
		des = ' '.join(des.split())
		des = des[:1000]
		info['description'] = des
		try :
			img = soup.find('img', {'id':'coverImage'})['src']
		except :
					return 1
		image = getunicode(img)
		info['image'] = image
		det = soup.find('span', itemprop="numberOfPages")
		details = getunicode(det)
		info['details'] = details
		rat = soup.find('span',{'class':'stars staticStars'})
		rate = getunicode(rat)
		info['rating'] = rate[:4]
		return info
	
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

#starting page url set to www.smthn.com/
def startPage(request): 
	if request.method=='GET':
		if  'e' in request.GET:
			return render_to_response('start.html',{'error':'1'},context_instance=RequestContext(request))
			 #if error pass error code
        	else:
            		return render_to_response('start.html',{},context_instance=RequestContext(request))
			 #if no error display page
    	else: 
        	userName=request.POST.get('user_name') 
		#extract data from text field
		password=request.POST.get('password')
		try:
			user = User.objects.get(user_name = userName)
			#search for user with given user name
		except User.DoesNotExist:
			return HttpResponseRedirect('/?e=1')
			 #if no such user set error code to 1
		if password == user.user_password:
		 #if user name and password exist authenticate user	
			try :
					
					ses = Session.objects.latest('id') 
					#get the highest session id
					val = ses.id + 1
			except Session.DoesNotExist:
					val = 1
			newSession = Session(id=val, user_id = user.id, login='y',mcount = 0, bcount = 0)
			newSession.save()    	
			#create a new session for the user						
			return HttpResponseRedirect('/%s/home' % val) #set url to /session id/home
		return HttpResponseRedirect('/?e=0')
			 #if password is incorrect set error code to 1
		


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
		try :
					
				ses = Session.objects.latest('id') 
				#get the highest session id
				val = ses.id + 1
		except Session.DoesNotExist:
				val = 1
		newSession = Session(id=val, user_id = new_user.id, login='y',mcount = 0, bcount = 0)
		newSession.save()    	
		#create a new session for the user
		return  HttpResponseRedirect('/%s/initial' % val)

def initialPage(request,sId):
	userSession = Session.objects.get(id=sId)
		#session data
	user = User.objects.get(id=userSession.user_id) 
		#get user data to an object

	if request.method=='GET':
		return render_to_response('initial_rating.html',{'user':user, 'Session' : userSession},context_instance=RequestContext(request))
	else:
		select = request.POST.get('selection')
		name = request.POST.get('name')
	
		if select == 'M' :
			try :
				movie = Movie.objects.get(movie_name__iexact = name)
			except Movie.DoesNotExist :
				movieInfo = searchMovie(name)
				if movieInfo == 1 :
					return HttpResponseRedirect('/%s/initial/?e=1' % sId)
				idVal = Movie.objects.latest('id').id + 1 
				movieId = Movie.objects.latest('movie_id').movie_id + 1
				movie = Movie(id = idVal, movie_id = movieId, movie_name = name, genre = str(movieInfo['genre']),
			 	release_date =movieInfo['date'], description =movieInfo['description'], imdb_rating= movieInfo['rating'],
				image_url =movieInfo['image'], title = movieInfo['title'])
				movie.save()
			print name
			return HttpResponseRedirect('/%s/movie/%s' % (sId,movie.id))
		elif select == 'B':
			try :
				book = Book.objects.get(book_name__iexact = name)
			except Book.DoesNotExist :
				bookInfo = searchBook(name)
				if bookInfo == 1 :
					return HttpResponseRedirect('/%s/initial/?e=1' % sId)
				idVal = Book.objects.latest('id').id + 1 
				book = Book(id = idVal, isbn = bookInfo['isbn'], book_name = name,
			 	description =bookInfo['description'], rating= bookInfo['rating'],
				image_url =bookInfo['image'], book_title = bookInfo['title'], author = bookInfo['author'],
				details = bookInfo['details'])
				book.save()
			return HttpResponseRedirect('/%s/book/%s' % (sId,book.id))
		
		rate = request.POST.get('rate1')
		if rate > 0:
				rte = Mrate.objects.latest('rate_id')
				movie = Movie.objects.get(movie_name__iexact = 'troy')
				newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id=movie.movie_id , wlist ='y', 					rating = rate)
				newRate.save()
				userSession.mcount = userSession.mcount + 1;
		rate = request.POST.get('rate2')
		if rate > 0:
				rte = Mrate.objects.latest('rate_id')
				movie = Movie.objects.get(movie_name__iexact = 'toy story')
				newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id=movie.movie_id , wlist ='y', 					rating = rate)
				newRate.save()
				userSession.mcount = userSession.mcount + 1;
		rate = request.POST.get('rate3')
		if rate > 0:
				rte = Mrate.objects.latest('rate_id')
				movie = Movie.objects.get(movie_name__iexact = 'die hard')
				newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id=movie.movie_id , wlist ='y', 					rating = rate)
				newRate.save()
				userSession.mcount = userSession.mcount + 1;
		rate = request.POST.get('rate4')
		if rate > 0:
				rte = Mrate.objects.latest('rate_id')
				movie = Movie.objects.get(movie_name__iexact = 'Forrest Gump')
				newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id=movie.movie_id , wlist ='y', 					rating = rate)
				newRate.save()
				userSession.mcount = userSession.mcount + 1;
		rate = request.POST.get('rate5')
		if rate > 0:
				rte = Mrate.objects.latest('rate_id')
				movie = Movie.objects.get(movie_name__iexact = 'jumanji')
				newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id=movie.movie_id , wlist ='y', 					rating = rate)
				newRate.save()
				userSession.mcount = userSession.mcount + 1;
		
		
		rate = request.POST.get('rate6')
		if rate > 0:
				rte = Brate.objects.latest('rate_id')
				book = Book.objects.get(book_name__iexact = 'The God of Small Things')
				newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn = book.isbn, wlist ='y', rating = rate)
				newRate.save()
				userSession.bcount += 1
		rate = request.POST.get('rate7')
		if rate > 0:
				rte = Brate.objects.latest('rate_id')
				book = Book.objects.get(book_name__iexact = 'Little Altars Everywhere')
				newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn = book.isbn, wlist ='y', rating = rate)
				newRate.save()
				userSession.bcount += 1
		rate = request.POST.get('rate8')
		if rate >0:
				rte = Brate.objects.latest('rate_id')
				book = Book.objects.get(book_name__iexact = 'Harry Potter and the Sorcerers Stone')
				newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn = book.isbn, wlist ='y', rating = rate)
				newRate.save()
				userSession.bcount += 1
		rate = request.POST.get('rate9')
		if rate > 0:
				rte = Brate.objects.latest('rate_id')
				book = Book.objects.get(book_name__iexact = 'twilight')
				newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn = book.isbn, wlist ='y', rating = rate)
				newRate.save()
				userSession.bcount += 1
		rate = request.POST.get('rate10')
		if rate > 0:
				rte = Brate.objects.latest('rate_id')
				book = Book.objects.get(book_name__iexact = 'To Kill a Mockingbird')
				newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn = book.isbn, wlist ='y', rating = rate)
				newRate.save()
				userSession.bcount += 1
		
		return HttpResponseRedirect('/%s/home' % sId)
		
		
#home page pass session id to ths page
def homePage(request,sId):
	userSession = Session.objects.get(id=sId)
		#session data
	user = User.objects.get(id=userSession.user_id) 
		#get user data to an object
	if request.method=='GET':  
		if  'e' in request.GET:
			code = 1
		else:
			code = None
		if userSession.mrec == None or userSession.mcount >= 5:
				movUsr = movieRecommend(user)
				userSession.mrec = dumps(movUsr)
				userSession.save()
			#save recommendations in database.
			
		else :
			movUsr = loads(str(userSession.mrec))
			#load recommendation from database

		movie =[]
		i = 10
		count = 0
		for usr in movUsr:
			mvs = Mrate.objects.filter(user_id = usr, rating = i )
			i = i - 1
			for mv in mvs:
				try :
					obj = Mrate.objects.get(movie_id =mv.movie_id, user_id =user.id)
				except Mrate.DoesNotExist:
					count = count + 1
					if count > 4 :
						break;
					obj = Movie.objects.get(movie_id =mv.movie_id)
					movie.append(obj)
			if count > 4 :
						break;

		if userSession.brec == None or userSession.bcount >= 5:
				bkUsr = bookRecommend(user)
				userSession.brec = dumps(bkUsr)
				userSession.save()
			#save recommendations in database.
			
		else :
			
			bkUsr = loads(str(userSession.brec))
			#load recommendation from database

		book =[]
		i = 10
		count = 0
		for usr in bkUsr:
			
			bks = Brate.objects.filter(user_id = usr[0], rating=i)
			i = i - 1
			
			for bk in bks:
				try :
					obj = Brate.objects.get(isbn =bk.isbn, user_id =user.id)
				except Brate.DoesNotExist:
					try :
						obj = Book.objects.get(isbn=bk.isbn)
					except Book.DoesNotExist :
							continue
					count = count + 1
					if count > 4 :
						break	
					book.append(obj)
			if count > 4 :
						break
				

			#store first four recommedations to an object 
		content_dict = {
			"User" : user,
			'Error' : code,
			'Movies' : movie,
			'Books' : book,
			'Session' : userSession
    			}
		return render_to_response('home.html',content_dict,context_instance=RequestContext(request)) 
		#display home page with dictionary context instance
	else :
		select = request.POST.get('selection')
		name = request.POST.get('name')
	
		if select == 'M' :
			try :
				movie = Movie.objects.get(movie_name__iexact = name)
			except Movie.DoesNotExist :
				movieInfo = searchMovie(name)
				if movieInfo == 1 :
					return HttpResponseRedirect('/%s/home/?e=1' % sId)
				idVal = Movie.objects.latest('id').id + 1 
				movieId = Movie.objects.latest('movie_id').movie_id + 1
				movie = Movie(id = idVal, movie_id = movieId, movie_name = name, genre = str(movieInfo['genre']),
			 	release_date =movieInfo['date'], description =movieInfo['description'], imdb_rating= movieInfo['rating'],
				image_url =movieInfo['image'], title = movieInfo['title'])
				movie.save()
			print name
			return HttpResponseRedirect('/%s/movie/%s' % (sId,movie.id))
		elif select == 'B':
			try :
				book = Book.objects.get(book_name__iexact = name)
			except Book.DoesNotExist :
				bookInfo = searchBook(name)
				if bookInfo == 1 :
					return HttpResponseRedirect('/%s/home/?e=1' % sId)
				idVal = Book.objects.latest('id').id + 1 
				book = Book(id = idVal, isbn = bookInfo['isbn'], book_name = name,
			 	description =bookInfo['description'], rating= bookInfo['rating'],
				image_url =bookInfo['image'], book_title = bookInfo['title'], author = bookInfo['author'],
				details = bookInfo['details'])
				book.save()
			return HttpResponseRedirect('/%s/book/%s' % (sId,book.id))
		elif select == 'P':
			try :
				find_user = User.objects.get(user_name = name)
			except User.DoesNotExist :
				return HttpResponseRedirect('/%s/home/?e=1' % sId)
			return HttpResponseRedirect('/%s/friend/%s' % (sId,find_user.id))
		return HttpResponseRedirect('/%s/home/?e=1' % sId)
		
			

def friends(request, sId, pId):
	
	userSession = Session.objects.get(id=sId)
		#session data
	user = User.objects.get(id=userSession.user_id) 
		#get user data to an object
	frienduser = User.objects.get(id=pId) 
	if request.method == 'GET':
		try:
			f = Friend.objects.get(user_id = user.id, friend_id = frienduser.id)
		except Friend.DoesNotExist:
			f = None
			friendflag = 0
		if f!= None:
			friendflag = 1
		
		movIds = Mrate.objects.filter(user_id = pId)
		mvWatch = []
	
		for movId in movIds:
			obj = Movie.objects.get(movie_id = movId.movie_id)
			if movId.wlist == 'y':
				mvWatch.append(obj)

		bookIds = Brate.objects.filter(user_id = pId)
		bWatch = []
	
		for bookId in bookIds:
			obj = Book.objects.get(isbn = bookId.isbn)
			if bookId.wlist == 'y':
				bWatch.append(obj)

		content_dic = {
		"User" : user,
		'Friend':frienduser,
		'mWatch' : mvWatch,
		'bWatch' : bWatch,
		'Session' : userSession,
		'flag' : friendflag
    		}
		
		return render_to_response('friends.html',content_dic,context_instance=RequestContext(request))
		
	else:
		friend = request.POST.get('friend')
		if friend == 'y':
			new_friend = Friend(user_id = user.id, friend_id = frienduser.id)
			new_friend.save()
		
		#return HttpResponseRedirect('/%s/home' % (user.id))	
		return HttpResponseRedirect('/%s/friend/%s' % (sId,pId))	
 														
def movie (request, sId, mId):
	userSession = Session.objects.get(id=sId)
	movie = Movie.objects.get(id = mId)
	user = User.objects.get(id=userSession.user_id) 
 	if request.method == 'GET':
		if movie.description == None :
			movieInfo = searchMovie(movie.movie_name)
			movie.release_date =movieInfo['date']
			movie.description =movieInfo['description']
			movie.imdb_rating= movieInfo['rating']
			movie.image_url =movieInfo['image']
			movie.title = movieInfo['title']
			movie.save()
		watch = 'n'
		tag = None 
		rating = 0 
		try :
			rate = Mrate.objects.get(user_id = user.id, movie_id =movie.movie_id)
			if rate.wlist == 'y':
				rating = rate.rating
			else :
				watch = 'y'		
		except Mrate.DoesNotExist:
			rating = 0 
		
		try :
			review = Mtags.objects.get(user_id = user.id, movie_id =movie.movie_id)
			tag = review.tags
		except Mtags.DoesNotExist:
			tag = None 

# rating and reviews of friends
		rateinfo = {}
		try :
			friends = Friend.objects.filter(user_id = user.id)
		except Friend.DoesNotExist:
			friends = None
		if friends != None:
			friend_rating = []
			friend_rate = []
			rateinfos = []
		for friend in friends:
			f = User.objects.get(id = friend.friend_id)
			rateinfo['f'] = f.user_name
			
			try:
				obj = Mrate.objects.get(user_id = friend.friend_id, movie_id = movie.movie_id)
							
			except Mrate.DoesNotExist:
				friend_rating = None
				
			if friend_rating != None:
				rateinfo['r'] = obj.rating
				
			
			try:
				obje = Mtags.objects.get(user_id = friend.friend_id, movie_id = movie.movie_id)
							
			except Mtags.DoesNotExist:
				friend_rate = None
				
			if friend_rate != None:
				rateinfo['review'] = obje.tags
				print obje.tags
				print rateinfo['review']
			rateinfos.append(rateinfo)
			
		for i in rateinfos:
			print i['f']

		content_dict = {'Movie':movie,
			 'User' : user,	
			 'Session':userSession,
			 'rate' : rating,
			 'tags' : tag,
			 'rateinfos' : rateinfos,
			 'wish' :watch,
	}

# rating and reviews of friends complete
		urllib.urlretrieve(movie.image_url,"/home/priya/cdrs/rec/static/myn.jpg")
		return render_to_response('moviedetails.html',content_dict,context_instance=RequestContext(request))
	

	else:
		wish = request.POST.get('wish')
		if wish == 'y' :
			rte = Mrate.objects.latest('rate_id')
			newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id = movie.movie_id, wlist ='n', rating = 0)
			newRate.save()
			
		else :		
			rate = request.POST.get('rate')
			if rate:
				rte = Mrate.objects.latest('rate_id')
				newRate = Mrate(rate_id = rte.rate_id + 1, user_id = user.id, movie_id = movie.movie_id, wlist ='y', 					rating = rate)
				newRate.save()
				userSession.mcount = userSession.mcount + 1;

			review = request.POST.get('review')
			if review: 
				tag = Mtags.objects.latest('tag_id')
				newTag = Mtags(tag_id = tag.tag_id + 1, user_id = user.id, movie_id = movie.movie_id,tags = review)
				newTag.save()
		if request.POST.get('rwish') == 'y':
			Mrate.objects.get(movie_id = movie.movie_id, user_id = user.id).delete()
		
		return HttpResponseRedirect('/%s/movie/%s' % (sId,movie.id))
		
		

def book (request, sId, bId):
	userSession = Session.objects.get(id=sId)
	book = Book.objects.get(id = bId)
	print bId
	user = User.objects.get(id=userSession.user_id)
	if request.method == 'GET':
		if book.rating == None :
			bookInfo = searchBook(book.book_name)
			book.author = bookInfo['author']
			book.description =bookInfo['description']
			book.rating= bookInfo['rating']
			book.image_url =bookInfo['image']
			book.book_title = bookInfo['title']
			book.details = bookInfo['details']
			
			book.save()
		
		urllib.urlretrieve(book.image_url,"/home/priya/cdrs/rec/static/myn.jpg")
		watch = 'n'
		tag = None 
		rating = 0 
		try :
			rate = Brate.objects.get(user_id = user.id, isbn =book.isbn)
			if rate.wlist == 'y':
				rating = rate.rating
				try :
					review = Btags.objects.get(user_id = user.id, isbn =book.isbn)
					tag = review.tags
				except Btags.DoesNotExist:
					tag = None 
			else :
				watch = 'y'
	
		except Brate.DoesNotExist:
			rating = 0 

# rating and reviews of friends
		rateinfo = {}
		try :
			friends = Friend.objects.filter(user_id = user.id)
		except Friend.DoesNotExist:
			friends = None
		if friends != None:
			friend_rating = []
			friend_rate = []
			rateinfos = []
		for friend in friends:
			f = User.objects.get(id = friend.friend_id)
			rateinfo['f'] = f.user_name
			
			try:
				obj = Brate.objects.get(user_id = friend.friend_id, isbn =book.isbn)
							
			except Brate.DoesNotExist:
				friend_rating = None
				
			if friend_rating != None:
				rateinfo['r'] = obj.rating
				
			
			try:
				obje = Btags.objects.get(user_id = friend.friend_id, isbn =book.isbn)
							
			except Btags.DoesNotExist:
				friend_rate = None
				
			if friend_rate != None:
				rateinfo['review'] = obje.tags
				print obje.tags
				print rateinfo['review']
			rateinfos.append(rateinfo)
			
		for i in rateinfos:
			print i['f']

		
# rating and reviews of friends complete
		content_dict = {'Book':book,
			 'User' : user,	
			 'Session':userSession,
			'rate' : rating,
			 'tags' : tag,
			 'rateinfos' : rateinfos,
			 'wish' :watch 	}
		return render_to_response('bookdetails.html',content_dict,context_instance=RequestContext(request))
	

	else:
		wish = request.POST.get('wish')
		if wish == 'y' :
			rte = Brate.objects.latest('rate_id')
			newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn= book.isbn, wlist ='n', rating = 0)
			newRate.save()
		else :		
			rate = request.POST.get('rate')
			if rate:
				rte = Brate.objects.latest('rate_id')
				newRate = Brate(rate_id = rte.rate_id + 1, user_id = user.id, isbn = book.isbn, wlist ='y', rating = rate)
				newRate.save()
				userSession.bcount += 1

			review = request.POST.get('review')
			if review: 
				tag = Btags.objects.latest('tag_id')
				newTag = Btags(tag_id = tag.tag_id + 1, user_id = user.id, isbn = book.isbn, tags = review)
				newTag.save()

		if request.POST.get('rwish') == 'y':
			Brate.objects.get(isbn = book.isbn, user_id = user.id).delete()
		
		return HttpResponseRedirect('/%s/book/%s' % (sId,book.id))
		
		

def movieRec(request, sId):
	userSession = Session.objects.get(id=sId)
	user = User.objects.get(id=userSession.user_id) 
	if request.method == 'GET' :
		recUsr = loads(str(userSession.mrec))
			#load recommendation from database
		i = 10
		count = 0
		movie =[]
		for usr in recUsr:
			mvs = Mrate.objects.filter(user_id = usr, rating = i )
			i = i - 1
			for mv in mvs:
				try :
					obj = Mrate.objects.get(movie_id =mv.movie_id, user_id =user.id)
				except Mrate.DoesNotExist:
					count = count + 1
					if count > 30 :
						break;
					obj = Movie.objects.get(movie_id =mv.movie_id)
					movie.append(obj)
			if count > 30:
				break;
		content_dict = {
			"User" : user,
			'Movies' : movie,
			'Session' : userSession
    			}
		return render_to_response('movierec.html',content_dict,context_instance=RequestContext(request)) 
		#display home page with dictionary context instance

def bookRec(request, sId):
	userSession = Session.objects.get(id=sId)
	user = User.objects.get(id=userSession.user_id) 
	if request.method == 'GET' :
		recUsr = loads(str(userSession.brec))
			#load recommendation from database

		book =[]
		i = 10
		count = 0
		for usr in recUsr:
			
			bks = Brate.objects.filter(user_id = usr[0], rating=i)
			i = i - 1
			
			for bk in bks:
				try :
					obj = Brate.objects.get(isbn =bk.isbn, user_id =user.id)
				except Brate.DoesNotExist:
					try :
						obj = Book.objects.get(isbn=bk.isbn)
					except Book.DoesNotExist :
							continue
					count = count + 1
					if count > 30 :
						break;
					book.append(obj)
				if count > 30 :
						break;
		content_dict = {
			"User" : user,
			'Books' : book,
			'Session' : userSession
    			}
		return render_to_response('bookrec.html',content_dict,context_instance=RequestContext(request)) 
		#display home page with dictionary context instance

def profilePage(request, sId):
	userSession = Session.objects.get(id=sId)
	user = User.objects.get(id=userSession.user_id) 
	movIds = Mrate.objects.filter(user_id = user.id)
	mvWatch = []
	mvWish = []
	rating = []
	for movId in movIds:
		obj = Movie.objects.get(movie_id = movId.movie_id)
		if movId.wlist == 'y':
			mvWatch.append(obj)
		else:
			mvWish.append(obj)
	bkRead = []
	bkWish = []
	bookIds = Brate.objects.filter(user_id = user.id)
	for bookId in bookIds:
		obj = Book.objects.get(isbn = bookId.isbn)
		if bookId.wlist == 'y':
			bkRead.append(obj)
		else:
			bkWish.append(obj)

	content_dict = {
			"User" : user,
			'Watch' : mvWatch,
			'Wish' :mvWish,
			'Read' : bkRead,
			'bWish' : bkWish,
			'Session' : userSession
    			}
	return render_to_response('profile.html',content_dict,context_instance=RequestContext(request)) 

def changePassword(request,sId):
	userSession = Session.objects.get(id=sId)
	user = User.objects.get(id=userSession.user_id) 
	if request.method == 'GET':
		if  'e' in request.GET:
			return render_to_response('pswdchange.html',{"User":user, "Session": userSession, 
			'error':1} ,context_instance=RequestContext(request)) 
			 #if error pass error code
        	else:
            		return render_to_response('pswdchange.html',{"User":user, "Session": userSession,
			 "error": None},context_instance=RequestContext(request)) 
			 #if no error display page
	else:
		old_password=request.POST.get('old_password')
		new_password=request.POST.get('new_password')
		if user.user_password != old_password:
			return HttpResponseRedirect('/%s/profile/pswdchange/?e=1' % sId)
		else :
			user.user_password = new_password
			user.save()
			return HttpResponseRedirect('/%s/profile/' % sId)


def logoutPage(request,uId):
	Session.objects.filter(user_id = uId).delete()
	#@cache_control(no_cache=True, must_revalidate=True)
	return HttpResponseRedirect('/')
		
				 
		
