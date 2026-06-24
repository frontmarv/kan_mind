from django.urls import path
from .views import BoardListView, board_single_view


urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board_view'),
    path('boards/<int:pk>/', board_single_view, name='board_single_view'),
]
