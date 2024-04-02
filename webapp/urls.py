
from django.urls import path

from . import views


urlpatterns = [

    path('', views.home, name=""),

    path('register', views.register, name="register"),

    path('my-login', views.my_login, name="my-login"),

    path('user-logout', views.user_logout, name="user-logout"),

    # CRUD

    path('dashboard', views.dashboard, name="dashboard"),

    path('create-record', views.create_record, name="create-record"),

    path('update-record/<int:pk>', views.update_record, name='update-record'),

    path('record/<int:pk>', views.singular_record, name="record"),

    path('delete-record/<int:pk>', views.delete_record, name="delete-record"),

    # face detect paths
    path('face_page/', views.face_page, name='face_page'),
    path('today_page/', views.today_page, name='today_page'),
    path('week_page/', views.week_page, name='week_page'),
    path('stranger_page/', views.stranger_page, name='stranger_page'),
    # path('person/<int:record_id>/', views.today_page, name='display_person'),

    path('detect-with-webcam/', views.detectWithWebcam, name='detect_with_webcam'),
    path('detect-image/', views.detectImage, name='detect-image'),
    path('search_by_date/', views.search_by_date, name='search_by_date'),

]








