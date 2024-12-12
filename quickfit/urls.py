from django.urls import path
from . import views

urlpatterns = [
    path('', views.memory_management, name='memory_management'),
    path('allocate/', views.allocate_memory, name='allocate_memory'),
    path('deallocate/', views.deallocate_memory, name='deallocate_memory'),
    path('status/', views.memory_status, name='memory_status'),
]

