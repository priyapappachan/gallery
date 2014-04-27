from django.db import models
 ####jyothissssss
class User(models.Model):
	user_name = models.CharField(max_length=200, unique=True)
	user_password = models.CharField(max_length=100)
	mail_id = models.EmailField(unique=True)
	phonenumber = models.CharField(max_length=20,blank=True)

class Session(models.Model):
	id = models.IntegerField(primary_key = True)
	user_id = models.IntegerField()
	mrec = models.TextField(null = True)
	brec = models.TextField(null = True)
	login = models.CharField(max_length=5)
	mcount = models.IntegerField()
	bcount = models.IntegerField()

class Friend(models.Model):
	user_id = models.IntegerField()
	friend_id = models.IntegerField()

class Movie(models.Model):
	id = models.IntegerField()
	movie_id = models.IntegerField(primary_key=True)
	movie_name = models.CharField(max_length=300)
	genre = models.CharField(max_length=500)
	release_date = models.CharField(max_length=25, null = True)
	description = models.CharField(max_length=500,default='null')
	imdb_rating = models.CharField(max_length=5 ,null = True)
	image_url = models.CharField(max_length=500,null = True)
	title = models.CharField(max_length=300)

class Mrate(models.Model):
	rate_id = models.IntegerField(primary_key=True)
	user_id = models.IntegerField()
	movie_id = models.IntegerField()
	rating = models.IntegerField()
	wlist = models.CharField(max_length=10, default='y')

class Mtags(models.Model):
	user_id = models.IntegerField()
	movie_id = models.IntegerField()
	tags = models.CharField(max_length=400)
	tag_id = models.IntegerField(primary_key=True)

class Book(models.Model):
	isbn = models.CharField(max_length=300)
	book_name =  models.CharField(max_length=300)
	author =  models.CharField(max_length=300)
	description = models.CharField(max_length=1000)
	details = models.CharField(max_length=300)
	book_title = models.CharField(max_length=300)
	image_url = models.CharField(max_length=300)
	id = models.IntegerField(primary_key=True)
	rating = models.CharField(max_length=10)

class Brate(models.Model):
	user_id = models.IntegerField()
	isbn = models.CharField(max_length=50)
	rating = models.IntegerField()
	rate_id = models.IntegerField(primary_key=True)
	wlist = models.CharField(max_length=10, default='y')

class Btags(models.Model):
	tag_id = models.IntegerField(primary_key=True)
	user_id = models.IntegerField()
	isbn = models.CharField(max_length=50)
	tags = models.CharField(max_length=400)



	



	
	
