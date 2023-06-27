from django.contrib import admin
from BookDB.models import *
# Register your models here.
admin.site.register(Authors)
admin.site.register(Genres)
admin.site.register(BOOKS)
admin.site.register(Issued)
admin.site.register(Customer)

