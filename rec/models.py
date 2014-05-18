from django.db import models

class User(models.Model):
	user_name = models.CharField(max_length=200, unique=True)
	user_password = models.CharField(max_length=100)
	mail_id = models.EmailField(unique=True)
	phonenumber =models.CharField(max_length=20,blank=True)

class Movie(models.Model):
	movie_name = models.CharField(max_length=300)
	genre = models.CharField(max_length=500)
	imdb_rating = models.CharField(max_length=5)
	description = models.CharField(max_length=500,default='null')
	release_date = models.CharField(max_length=25)
	
class Mrate(models.Model):
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
	isbn = models.CharField(max_length=25,primary_key=True)
	book_name = models.CharField(max_length=300)
	book_author = models.CharField(max_length=100)
	book_year = models.IntegerField()
	book_publisher = models.CharField(max_length=200)
	book_image  = models.CharField(max_length=300)

class Brate(models.Model):
	user_id = models.IntegerField()
	isbn = models.CharField(max_length=25)
	rating = models.IntegerField()
	wlist = models.CharField(max_length=10, default='y')
	
