from django.contrib import admin
from .models import Hotel, Room, Reservation
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name","city","stars")
    search_fields = ("name","city")
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'room_type',
        'hotel',
        'capacity',
        'price_per_night',
        'is_active',
        'spaces',
        'description',
        'image'
    )
    search_fields = ('number', 'hotel__name')
    list_filter = ('room_type', 'is_active')
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("room","guest_name","check_in","check_out")
    list_filter = ("check_in","check_out","room__hotel")
    search_fields = ("guest_name","room__number")