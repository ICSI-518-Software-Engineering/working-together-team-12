from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[   
    path('',views.index,name='index'),
    path('post_cinemas_for_film',views.post_cinemas_for_film,name='view_cinemas_for_film'),
    path('show_cinemas_for_movie',views.show_cinemas_for_movie,name='show_cinemas_for_movie'),
    path('seat/<int:id>',views.seat,name='seat'),
    path('seat_selection/<int:cinema_id>/film/<int:film_id>/showtime/<str:showtime>/date/<str:date>/', views.seat_selection, name='seat_selection'),
    path('seat_selection/<int:cinema_id>/film/<int:film_id>/showtime/<str:showtime>/date/<str:date>/booking_view',views.booking_view,name='booking_view'),
    path('show_tickets/<int:cinema_id>/film/<int:film_id>/showtime/<str:showtime>/date/<str:date>/',views.show_tickets,name='show_tickets'),
    path('movie-search',views.movie_search,name='movie-search'),
    path('fetch-movies',views.fetch_movies,name='fetch-movies'),
    path('load-movie',views.load_movie,name='load-movie'),
    path('movie-details',views.movie_details,name='movie-details'),




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)