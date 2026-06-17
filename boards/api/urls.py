from django.urls import path
from .views import BoardListView

urlpatterns = []

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
]
