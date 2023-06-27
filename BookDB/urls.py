from django.urls import path, include
from BookDB import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('',views.openpage,name='startpage'),
    path('BookDB/',views.main, name='landing'),
    path('BookDB/search',views.searchT),
    path('BookDB/Remaining',views.remBooks),
    path('BookDB/alreadyIssued',views.issBooks),
    path('BookDB/moreDetails',views.moreDet,name='more_details'),
    path('BookDB/borrowBook',views.borBook),
    path('BookDB/buyBook',views.buyBook),
    path('BookDB/borrowBook/generateI/<int:issue_id>',views.generate_invoice,name='invoice'),
    
    path('BookDB/registerUser', views.register_CUST ),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('BookDB/loginUser/', views.login, name="loginu" ),
    path('BookDB/logoutUser/',views.logout),
    
    path('BookDB/showAuth', views.getAutho),
    path('BookDB/inputAuth', views.postAutho),
    path('BookDB/updateAuthor/<int:pk>/', views.updateAuthor),
    path('BookDB/delAuthor/<int:pk>/', views.delAuthor),    
    
    path('BookDB/showGenre', views.getGenre),
    path('BookDB/inputGenre', views.postGenre),    
    path('BookDB/updateGenre/<int:pk>/', views.updateGenre),
    path('BookDB/delGenre/<int:pk>/', views.delGenre),
    
    path('BookDB/showBook', views.getBook),
    path('BookDB/inputBook', views.postBook),
    path('BookDB/updateBook/<int:pk>/', views.updateBook),    
    path('BookDB/delBook/<int:pk>/', views.delBook),
    
    path('BookDB/showCust', views.getCust),
    path('BookDB/inputCust', views.postCust),    
    path('BookDB/updateCust/<int:pk>/', views.updateCustomer),
    path('BookDB/delCust/<int:pk>/', views.delCust),
    
    path('BookDB/showIss', views.getIss),
    path('BookDB/inputIss', views.postIss),
    path('BookDB/updateIss/<int:pk>/', views.updateIssued),
    path('BookDB/delIss/<int:pk>/', views.delIssued),
]