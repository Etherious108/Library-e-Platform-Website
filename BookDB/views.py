from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site 
from django.contrib import messages 
from django.core.mail import EmailMessage
from django.db.models import Subquery
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string 


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.decorators import api_view

import jwt
from jwt.exceptions import InvalidTokenError
from BookDB.models import Authors, Issued, Customer, Genres, BOOKS
from BookDB.forms import *
from BookDB.serializer import * 
from BookDB.tokens import account_activation_token  

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

def openpage(request):
    return render(request,'page.html')

def logout(request):
    try:
        auth_logout(request)
        messages.success(request,'You have been Logged out Successfully')
        return redirect('startpage')
    except Exception as e:
        print(e)
        return HttpResponse(e)
    
    
@api_view(['GET','POST'])
def remBooks(request):
    try:
        # Retrieve token from session
        token = request.session.get('token')

        if not token:
            raise AuthenticationFailed('Invalid or expired token')

        try:
            # Verify and decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = Customer.objects.get(id=user_id)
            if not user.is_active:
                raise InvalidTokenError('User is inactive')
        except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidTokenError, User.DoesNotExist) as e:
            print(e)
            raise AuthenticationFailed('Invalid or expired token')

        # Fetch books and serialize
        form = SearchForm(request.POST or None)
        books_not_issued = BOOKS.objects.exclude(id__in=Subquery(Issued.objects.values('BookID_id')))
        if request.method == 'POST' and form.is_valid():
            searchtext = form.cleaned_data.get('searchtext')            
            books_not_issued = searchT(searchtext,books_not_issued)        
            
        BSerializer = BookSerializer(books_not_issued, many=True)
        # print(BSerializer.data)
        context = {
            "Books": BSerializer.data,
            "form" : form,
            "Type" : "Remaining",
        }
        return render(request, 'page1.html', context)
    except AuthenticationFailed as e:
        print(e)
        messages.error(request, 'Please Login')
        return redirect('loginu')


@api_view(['GET','POST'])
def issBooks(request):    
    try:
        # Retrieve token from session
        token = request.session.get('token')

        if not token:
            raise AuthenticationFailed('Invalid or expired token')

        try:
            # Verify and decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = Customer.objects.get(id=user_id)
            if not user.is_active:
                raise InvalidTokenError('User is inactive')
        except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidTokenError, User.DoesNotExist) as e:
            print(e)
            raise AuthenticationFailed('Invalid or expired token')

        # Fetch books and serialize
        form = SearchForm(request.POST or None)
        books_issued = BOOKS.objects.filter(id__in=Subquery(Issued.objects.values('BookID_id')))
        if request.method == 'POST' and form.is_valid():
            searchtext = form.cleaned_data.get('searchtext')            
            books_issued = searchT(searchtext,books_issued)        
            
        BSerializer = BookSerializer(books_issued, many=True)
        # print(BSerializer.data)
        context = {
            "Books": BSerializer.data,
            "form" : form,
            "Type" : "Already Issued",
        }
        return render(request, 'page1.html', context)
    except AuthenticationFailed as e:
        print(e)
        messages.error(request, 'Please Login')
        return redirect('loginu')
            
@api_view(['GET','POST'])
def main(request):
    try:
        # Retrieve token from session
        token = request.session.get('token')

        if not token:
            raise AuthenticationFailed('Invalid or expired token')

        try:
            # Verify and decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            request.session['uid']=user_id
            user = Customer.objects.get(id=user_id)
            if not user.is_active:
                raise InvalidTokenError('User is inactive')
        except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidTokenError, User.DoesNotExist) as e:
            print(e)
            raise AuthenticationFailed('Invalid or expired token')

        # Fetch books and serialize
        form = SearchForm(request.POST or None)
        books = BOOKS.objects.all()
        if request.method == 'POST' and form.is_valid():
            searchtext = form.cleaned_data.get('searchtext')            
            books = searchT(searchtext,books)                
            
        BSerializer = BookSerializer(books, many=True)
        # print(BSerializer.data)
        context = {
            "Books": BSerializer.data,
            "form" : form,
            "Type" : "All",
        }
        return render(request, 'page1.html', context)
    except AuthenticationFailed as e:
        print(e)
        messages.error(request, 'Please Login')
        return redirect('loginu')

def searchT(searchtext,booksg):
    books1 = booksg.filter(BookName__icontains=searchtext)
    books2 = booksg.filter(AuthorID__AuthorFullName__icontains = searchtext)
    books3 = booksg.filter(GenreID__Genre__icontains = searchtext)    
    books = books1.union(books2,books3,all=False)    
    return books


def moreDet(request):
    try:
        # Retrieve token from session
        token = request.session.get('token')

        if not token:
            raise AuthenticationFailed('Invalid or expired token')

        try:
            # Verify and decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = Customer.objects.get(id=user_id)
            if not user.is_active:
                raise InvalidTokenError('User is inactive')
        except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidTokenError, User.DoesNotExist) as e:
            print(e)
            raise AuthenticationFailed('Invalid or expired token')

        bid = request.GET.get('bookid')
        book = BOOKS.objects.get(pk=bid)
        bookdet=BookSerializer(book).data
        context={
            "Book" : bookdet,
        }
        return render(request,'moredetails.html',context)
    except AuthenticationFailed as e:
        print(e)
        messages.error(request, 'Please Login')
        return redirect('loginu')

def borBook(request):
    try:
        # Retrieve token from session
        token = request.session.get('token')

        if not token:
            raise AuthenticationFailed('Invalid or expired token')

        try:
            # Verify and decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = Customer.objects.get(id=user_id)
            if not user.is_active:
                raise InvalidTokenError('User is inactive')
        except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidTokenError, User.DoesNotExist) as e:
            print(e)
            raise AuthenticationFailed('Invalid or expired token')

        uid=request.session.get('uid')
        bid = request.GET.get('bookid') 
        cust = Customer.objects.get(pk=uid)
        book = BOOKS.objects.get(pk=bid)
        bookdet=BookSerializer(book).data
        msg=None    
        if(Issued.objects.filter(BookID=book, CustomerID=uid).exists()):
            messages.warning(request, 'This book is already in your collection.')
            return redirect(reverse('more_details') + f'?bookid={bid}')    
        
        form=BorrowForm(request.POST or None)
        
        if request.method == 'POST' :
            if form.is_valid():
                fromDate = form.cleaned_data.get('IssueDate')
                toDate = form.cleaned_data.get('ReleaseDate')
                if(fromDate<toDate):
                    issbook = Issued.objects.create(BookID=book,IssueDate=fromDate,ReleaseDate=toDate,CustomerID=cust,is_bought=False)
                    return redirect('invoice',issbook.id)
                    
                else:
                    msg="Borrow Time must be atleast 1 Day"
        context = {
            "form":form,
            "msg":msg,
            "Book" : bookdet,
        }
        return render(request,'borrow.html',context)
    except AuthenticationFailed as e:
        print(e)
        messages.error(request, 'Please Login')
        return redirect('loginu')
    
def generate_invoice(request,issue_id):    
    issued = Issued.objects.get(pk=issue_id)
    customer = issued.CustomerID
    book = issued.BookID
    from_date = issued.IssueDate
    to_date = issued.ReleaseDate

    # Define the content for the PDF invoice
    company_name = "KD-Library"
    borrow_invoice = "Borrow-Invoice:"
    issued_id = str(issued.id)
    customer_details = [
        ("Customer", f"{customer.CustomerFName} {customer.CustomerLName}"),
        ("Phone Number", customer.CustomerPNo),
        ("Email", customer.CustEmail)
    ]
    table_title = "Invoice Details"
    table_data = [
        ["Book ID", "Book Name", "Author", "From", "To"],
        [str(book.id), book.BookName, book.AuthorID.AuthorFullName, str(from_date), str(to_date)]
    ]

    # Set up the PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'
    response['Content-Title'] = 'Library Invoice'
    

    # Create the PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles for the invoice content
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        name='HeadingStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=24,
        spaceAfter=12,
        spaceBefore=12,
        textDecoration='underline'
    )
    subheading_style = ParagraphStyle(
        name='SubheadingStyle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=18,
        spaceAfter=12,
        spaceBefore=12,
        textDecoration='underline'
    )
    customer_style = ParagraphStyle(
        name='CustomerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=14,
        spaceAfter=12,
    )
    table_title_style = ParagraphStyle(
        name='TableTitleStyle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceBefore=12,
        spaceAfter=12,
        textDecoration='underline'
    )
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]

    elements.append(Paragraph(company_name, heading_style))
    elements.append(Paragraph(f"{borrow_invoice} {issued_id}", subheading_style))
    elements.append(Spacer(1, 36))
    customer_details_paragraphs = [
        Paragraph(f"<b>{name}:</b> {value}", customer_style) for name, value in customer_details
    ]
    elements.extend(customer_details_paragraphs)
    elements.append(Spacer(1, 36))
    elements.append(Paragraph(table_title, table_title_style))
    table = Table(table_data, style=table_style, colWidths=[70, 200, 100, 80, 80])
    elements.append(table)
    congratulations = "Congratulations on successfully borrowing '{}'!".format(book.BookName)
    congratulations2 = "Regards,"
    congratulations3 = "KD-Library."
    congratulations_style2 = ParagraphStyle(name='CongratulationsStyle', parent=styles['Normal'], fontName='Helvetica-BoldOblique', fontSize=12, alignment=1, spaceAfter=20)
    congratulations_style = ParagraphStyle(name='CongratulationsStyle', parent=styles['Normal'], fontName='Helvetica-BoldOblique', fontSize=12, alignment=0, spaceAfter=20)
    bottom_spacer = Spacer(1, 250)

    # Build the PDF document
    elements.append(bottom_spacer)
    elements.append(Paragraph(congratulations, congratulations_style2))
    elements.append(Paragraph(congratulations2, congratulations_style))
    elements.append(Paragraph(congratulations3, congratulations_style))

    # Build the PDF document
    doc.build(elements)
    # Get the PDF content from the buffer and attach it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response



  
def buyBook(request):
    bid = request.GET.get('bookid')
    book = BOOKS.objects.get(pk=bid)
    bookdet=BookSerializer(book).data
    return render(request,'base.html',{"messages":"This Page is still under construction.\n\nWe Regret any Incovenience caused."})

def login(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            cemail = form.cleaned_data.get('CustEmail')
            password = form.cleaned_data.get('password')
            user = authenticate(CustEmail=cemail, password=password)
            if user is not None:
                if user.is_active:
                    try:
                        auth_login(request,user)
                        
                        # Generate JWT
                        refresh = RefreshToken.for_user(user)

                        # Obtain the new token
                        token = str(refresh.access_token)

                        # Store the token in the session
                        request.session['token'] = token

                        # Pass the token to the landing page
                        return redirect('landing')
                    except Exception as e:
                        print(e)
                else:
                    msg = 'Your account is inactive'
            else:
                msg = 'You have entered incorrect username or password'
        else:
            msg = 'Error has occurred. Try Again'
    return render(request, 'login.html', {'form': form, 'msg': msg})

    

def register_CUST(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.is_active=False
            user.save()
            current_site = get_current_site(request) 
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user) 
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}"
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('acc_active_email.html', {  
                'user': user,  
                'activation_link': activation_link,  
            })  
            to_email = form.cleaned_data.get('CustEmail')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            )  
            email.send()              
            return render(request,'base.html',{"messages":'Please confirm your email address to complete the registration'})  
        else:
            msg = 'Form is not valid'
            return render(request, 'regist.html', {'form': form, 'msg': msg})
    else:
        form = UserRegister()
        return render(request, 'regist.html', {'form': form})
    
def activate(request, uidb64, token):  
    User = settings.AUTH_USER_MODEL
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = Customer.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        return render(request,'base.html',{"messages":'Thank you for your email confirmation. Now you can login your account.'})  
    else:  
        return render(request,'base.html',{"messages":'Activation link is invalid!'})      

##

@api_view(['GET'])
def getAutho(request):
    aut=Authors.objects.all()
    serializer = AuthSerializer(aut, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postAutho(request):
    try:
        serializer = AuthSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
        else:
            return Response({'Error':str(serializer.errors)},status=400)
        return Response("Author details Inserted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})

@api_view(['PATCH'])
def updateAuthor(request,pk):
    try:
        item=Authors.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    serializer=AuthSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("Book Updated successfully")
    else:
        return Response({'Error':str(serializer.errors)},status=400)
    
@api_view(['DELETE'])
def delAuthor(request,pk):
    try:
        item=Authors.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    try:
        item.delete()
        return Response("Item deleted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})
    
####

@api_view(['GET'])
def getGenre(request):
    aut=Genres.objects.all()
    serializer = GenreSerializer(aut, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postGenre(request):
    try:
        serializer = GenreSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
        else:
            return Response({'Error':str(serializer.errors)},status=400)
        return Response("Genre details Inserted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})

@api_view(['PATCH'])
def updateGenre(request,pk):
    try:
        item=Genres.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    serializer=GenreSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("Genre Updated successfully")
    else:
        return Response({'Error':str(serializer.errors)},status=400)

@api_view(['DELETE'])
def delGenre(request,pk):
    try:
        item=Genres.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    try:
        item.delete()
        return Response("Item deleted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})
##

@api_view(['GET'])
def getBook(request):
    aut=BOOKS.objects.all()
    serializer = BookSerializer(aut, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postBook(request):
    try:
        serializer = BookSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
        else:
            return Response({'Error':str(serializer.errors)},status=400)
        return Response("Book details Inserted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})

@api_view(['PATCH'])
def updateBook(request,pk):
    try:
        item=BOOKS.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    serializer=BookSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("Book Updated successfully")
    else:
        return Response({'Error':str(serializer.errors)},status=400)

@api_view(['DELETE'])
def delBook(request,pk):
    try:
        item=BOOKS.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    try:
        item.delete()
        return Response("Item deleted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})
##    

@api_view(['GET'])
def getCust(request):
    aut=Customer.objects.all()
    serializer = CustomerSerializer(aut, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postCust(request):
    try:
        serializer = Customer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
        else:
            return Response({'Error':str(serializer.errors)},status=400)
        return Response("Customer details Inserted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})

@api_view(['PATCH'])
def updateCustomer(request,pk):
    try:
        item=Customer.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    serializer=CustomerSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("Customer Updated successfully")
    else:
        return Response({'Error':str(serializer.errors)},status=400)

@api_view(['DELETE'])
def delCust(request,pk):
    try:
        item=Customer.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    try:
        item.delete()
        return Response("Item deleted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})
##

@api_view(['GET'])
def getIss(request):
    aut=Issued.objects.all()
    serializer = IssuedSerializer(aut, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postIss(request):
    try:
        serializer = IssuedSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
        else:
            return Response({'Error':str(serializer.errors)},status=400)
        return Response("Issued details Inserted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})

@api_view(['PATCH'])
def updateIssued(request,pk):
    try:
        item=Issued.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    serializer=IssuedSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("Issued Updated successfully")
    else:
        return Response({'Error':str(serializer.errors)},status=400)
    
@api_view(['DELETE'])
def delIssued(request,pk):
    try:
        item=Issued.objects.get(id=pk)
    except:
        return Response("Said Item doesn't exist")
    try:
        item.delete()
        return Response("Item deleted Successfully")
    except Exception as e:
        return Response({'Error': str(e)})
    