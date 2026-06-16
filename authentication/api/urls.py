from django.urls import path
from .views import UserProfileList, RegistrationView, LoginView

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('registration/', RegistrationView.as_view(),
         name='registration'),
    path('login/', LoginView.as_view(),
         name='login'),
]
