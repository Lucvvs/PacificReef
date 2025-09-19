from django.urls import path
from . import views
from .views import Registro, Contacto

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    
    # Hoteles
    path("hoteles/", views.HotelList.as_view(), name="hotel_list"),
    path("hoteles/nuevo/", views.HotelCreate.as_view(), name="hotel_create"),
    path("hoteles/<int:pk>/", views.HotelDetail.as_view(), name="hotel_detail"),
    path("hoteles/<int:pk>/editar/", views.HotelUpdate.as_view(), name="hotel_update"),
    path("hoteles/<int:pk>/eliminar/", views.HotelDelete.as_view(), name="hotel_delete"),

    # Habitaciones
    path("habitaciones/", views.RoomList.as_view(), name="room_list"),
    path("habitaciones/nueva/", views.RoomCreate.as_view(), name="room_create"),
    path("habitaciones/<int:pk>/", views.RoomDetail.as_view(), name="room_detail"),
    path("habitaciones/<int:pk>/editar/", views.RoomUpdate.as_view(), name="room_update"),
    path("habitaciones/<int:pk>/eliminar/", views.RoomDelete.as_view(), name="room_delete"),

    # Reservas
    path("reservas/", views.ResList.as_view(), name="res_list"),
    path("reservas/nueva/", views.ResCreate.as_view(), name="res_create"),
    path("reservas/<int:pk>/", views.ResDetail.as_view(), name="res_detail"),
    path("reservas/<int:pk>/editar/", views.ResUpdate.as_view(), name="res_update"),
    path("reservas/<int:pk>/eliminar/", views.ResDelete.as_view(), name="res_delete"),

    # Registro de Usuarios
    path("register/", Registro.as_view(), name="register"),
    path("contacto/", Contacto.as_view(), name="contacto"),
]


