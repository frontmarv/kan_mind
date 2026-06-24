from django.urls import path
from .views import AssignedTasksView, task_single_view_comment, task_single_view, task_single_view_comments, ReviewingTaskView, TaskView


urlpatterns = [
    path('tasks/', TaskView.as_view(), name='tasks_list'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks_assigend'),
    path('tasks/reviewing/', ReviewingTaskView.as_view(), name='tasks_reviewing'),
    path('tasks/<int:pk>/', task_single_view, name='tasks_single_view'),
    path('tasks/<int:task_id>/comments/', task_single_view_comments,
         name='task_single_view_comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/',
         task_single_view_comment, name='task_single_view_single_delete_comment'),

]
