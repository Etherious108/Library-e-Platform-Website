from rest_framework import serializers
from BookDB.models import Authors, Genres, BOOKS, Issued, Customer

class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model=Authors
        fields=('AuthorFName','AuthorLName')
        
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model=Genres
        fields='__all__'
        
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model=BOOKS
        fields=('__all__')
        depth=2
        
class IssuedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Issued
        fields=('IssueDate','BookID','CustomerID')
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=('CustomerFName','CustomerLName','CustomerPNo')
        
