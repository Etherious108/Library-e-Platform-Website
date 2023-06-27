import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Authors(models.Model):
    AuthorFName = models.CharField(max_length=255)
    AuthorLName = models.CharField(max_length=255)
    AuthorFullName = models.CharField(max_length=510,null=True)
    def __str__(self):
        return(str(self.id))
    
    def save(self, *args, **kwargs):
        self.AuthorFullName = self.AuthorFName + " " + self.AuthorLName
        super(Authors, self).save(*args, **kwargs)
    
class Genres(models.Model):
    Genre = models.CharField(max_length=255)
    def __str__(self):
        return(str(self.id))

class BOOKS(models.Model):
    BookName = models.CharField(max_length=255)
    AuthorID = models.ForeignKey(Authors, on_delete=models.CASCADE, null=True)
    GenreID = models.ForeignKey(Genres, on_delete=models.CASCADE, null=True)
    BookCover = models.ImageField(upload_to='images/', null=True)
    BookDesc = models.TextField(null=True)

    def __str__(self):
        return(str(self.id))

class Customer(AbstractUser):
    username = models.CharField(max_length=10, unique=True, null=True)
    CustomerFName = models.CharField(max_length=255)
    CustomerLName = models.CharField(max_length=255)
    CustEmail = models.EmailField(_("Email Address"), unique=True)
    CustomerPNo = models.CharField(max_length=10) 
    REQUIRED_FIELDS = ['password','username']
    USERNAME_FIELD = 'CustEmail'
    @property
    def is_anonymous(self):
        return False
    
    def __str__(self):
        return(str(self.id))
   
class Issued(models.Model):
    BookID = models.ForeignKey(BOOKS, on_delete=models.CASCADE)
    IssueDate = models.DateField(default=datetime.date.today)    
    ReleaseDate = models.DateField(default=datetime.date.today)
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_bought = models.BooleanField(default=False)
    
    def __str__(self):
        return(str(self.id))
