from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dresses/', views.dress_list, name='dress_list'),
    path('dresses/add/', views.add_dress, name='add_dress'),
    path('rentals/add/', views.add_rental, name='add_rental'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_history, name='customer_history'),
    path('rentals/update/<int:rental_id>/<str:status>/', views.update_rental_status, name='update_rental_status'),
    path('customers/add/', views.add_customer, name='add_customer'), # <--- เพิ่มบรรทัดนี้
    path('dresses/edit/<int:dress_id>/', views.edit_dress, name='edit_dress'),
    path('dresses/delete/<int:dress_id>/', views.delete_dress, name='delete_dress'),
    path('rentals/delete/<int:rental_id>/', views.delete_rental, name='delete_rental'),

]