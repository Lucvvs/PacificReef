from django import forms
from .models import Reservation, Room
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class ReservationForm(forms.ModelForm):
    
    ROOM_TYPES_DB = [
        "Habitación Simple",
        "Habitación Doble",
        "Habitación Matrimonial",
        "Habitación Premium",
    ]

    class Meta:
        model = Reservation
        fields = ["room", "guest_name", "check_in", "check_out", "notes"]
        labels = {
            "room": "Habitación",
            "guest_name": "Nombre cliente",
            "check_in": "Fecha de llegada",
            "check_out": "Fecha de salida",
            "notes": "Notas adicionales",
        }
        widgets = {
            "room": forms.Select(attrs={"class": "form-select"}),
            "guest_name": forms.TextInput(attrs={"class": "form-control"}),
            "check_in": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "check_out": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        
        picked = []
        for rt in self.ROOM_TYPES_DB:
            qs = Room.objects.filter(room_type=rt, is_active=True).order_by("id")
            if qs.exists():
                picked.append(qs.first())

        if picked:
            self.fields["room"].queryset = Room.objects.filter(id__in=[r.id for r in picked])
       
            self.fields["room"].choices = [(r.id, r.room_type) for r in picked]
        else:
            self.fields["room"].queryset = Room.objects.none()

        # 2) Autollenar "Nombre cliente" con usuiaro
        if user:
            self.fields["guest_name"].initial = (user.get_full_name() or user.username)
        self.fields["guest_name"].disabled = True 



class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "captcha"]   