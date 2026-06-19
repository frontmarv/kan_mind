from django.urls import path
from .views import AssigendTasksView, ReviewingTaskView, TaskView


urlpatterns = [
    path('tasks/', TaskView.as_view(), name='tasks_list'),
    path('tasks/assigend-to-me/', AssigendTasksView.as_view(), name='tasks_assigend'),
    path('tasks/reviewing/', ReviewingTaskView.as_view(), name='tasks_reviewing'),
    # path('tasks/<int:pk>/', board_single_view, name='tasks_single_view'),
    # path('tasks/<int:pk>/comments/', board_single_view, name='tasks_single_view_comments'),
    # path('tasks/<int:pk>/comments/<int:pk>/', board_single_view, name='tasks_single_view_single_comment'),

]
