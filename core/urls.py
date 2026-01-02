from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
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
    path('dashboard/', views.dashboard, name='dashboard'),
    # ✅ เพิ่มบรรทัดนี้สำหรับ Login (ชี้ไปที่ไฟล์ html ที่เราเพิ่งสร้าง)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # ✅ เพิ่มบรรทัดนี้สำหรับ Logout (กดแล้วเด้งกลับหน้าแรก)
    path('logout/', auth_views.LogoutView.as_view(next_page='landing_page'), name='logout'),
    path('accessories/', views.accessory_list, name='accessory_list'),
    path('accessories/add/', views.add_accessory, name='add_accessory'),
    path('accessories/delete/<int:acc_id>/', views.delete_accessory, name='delete_accessory'),
    # เพิ่มต่อท้ายใน urlpatterns
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/portal/', views.customer_portal, name='customer_portal'),
    path('customer/select/<int:rental_id>/', views.customer_select_accessories, name='customer_select_accessories'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customers/edit/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),
]