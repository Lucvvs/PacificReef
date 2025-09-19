from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings 

class Hotel(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=200, blank=True)
    stars = models.PositiveSmallIntegerField(default=3)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} — {self.city}"


class Room(models.Model):
    ROOM_TYPES = [
        ("STD", "Standard"),
        ("DLX", "Deluxe"),
        ("STE", "Suite"),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=3, choices=ROOM_TYPES, default="STD")
    capacity = models.PositiveSmallIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    # Campo imagen
    image = models.ImageField(upload_to="rooms/", blank=True, null=True)

    spaces = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("hotel", "number")

    def __str__(self):
        return f"{self.hotel.name} • Hab {self.number}"


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="reservations")
    guest_name = models.CharField(max_length=120)
    check_in = models.DateField()
    check_out = models.DateField()
    notes = models.TextField(blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        null=True, blank=True,  
    )

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError("La fecha de salida debe ser posterior al check-in.")

        overlaps = Reservation.objects.filter(
            room=self.room,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        )
        if self.pk:
            overlaps = overlaps.exclude(pk=self.pk)
        if overlaps.exists():
            raise ValidationError("La habitación ya está reservada en ese rango.")

    def __str__(self):
        return f"{self.room} — {self.check_in}→{self.check_out}"