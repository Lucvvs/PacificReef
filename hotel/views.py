from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm
from .forms import ReservationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from datetime import date
from .forms import CustomUserCreationForm
import requests
from django.conf import settings

from .models import Hotel, Room, Reservation


class Home(TemplateView):
    template_name = "base_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        url = "https://my.meteoblue.com/packages/basic-1h_basic-day"
        params = {
            "apikey": settings.METEOBLUE_API_KEY,
            "lat": -33.4569,   # Santiago
            "lon": -70.6483,
            "asl": 556,
            "format": "json"
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()

            # 👇 Guardar los próximos 7 días como lista
            clima = []
            if "data_day" in data and "time" in data["data_day"]:
                for i in range(min(7, len(data["data_day"]["time"]))):
                    clima.append({
                        "fecha": data["data_day"]["time"][i],
                        "temp_max": data["data_day"]["temperature_max"][i],
                        "temp_min": data["data_day"]["temperature_min"][i],
                        "precip": data["data_day"]["precipitation"][i],
                    })
            context["clima"] = clima
        except Exception as e:
            print("Error consultando Meteoblue:", e)
            context["clima"] = []

        return context

    


# --------- Hoteles ---------
class HotelList(ListView):
    model = Hotel
    ordering = ["name"]
    paginate_by = 10

class HotelDetail(DetailView):
    model = Hotel

class HotelCreate(CreateView):
    model = Hotel
    fields = ["name","city","address","stars","description"]
    success_url = reverse_lazy("hotel_list")

class HotelUpdate(UpdateView):
    model = Hotel
    fields = ["name","city","address","stars","description"]
    success_url = reverse_lazy("hotel_list")

class HotelDelete(DeleteView):
    model = Hotel
    success_url = reverse_lazy("hotel_list")


# --------- Habitaciones ---------
class RoomList(ListView):
    model = Room
    ordering = ["hotel__name","number"]
    paginate_by = 20
    template_name = "hoteles/room_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current"] = "room_list"
        return ctx
        

class RoomDetail(DetailView):
    model = Room
    template_name = "hoteles/room_detail.html"

class RoomCreate(CreateView):
    model = Room
    fields = ["hotel","number","room_type","capacity","price_per_night","is_active"]
    success_url = reverse_lazy("room_list")

class RoomUpdate(UpdateView):
    model = Room
    fields = ["hotel","number","room_type","capacity","price_per_night","is_active"]
    success_url = reverse_lazy("room_list")

class RoomDelete(DeleteView):
    model = Room
    success_url = reverse_lazy("room_list")


# --------- Reservas ( usuario logueado) ---------
class ResList(LoginRequiredMixin, ListView):
    model = Reservation
    ordering = ["-check_in"]
    paginate_by = 20
    template_name = "hoteles/reservation_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current"] = "res_list"
        ctx["today"] = now().date()
        return ctx


class ResDetail(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = "hoteles/reservation_detail.html"

    def get_queryset(self):
        # Sólo el dueño (o staff) puede acceder a su reserva
        qs = super().get_queryset()
        return qs.filter(user=self.request.user) if not self.request.user.is_staff else qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current"] = "res_detail"
        reservation = self.object
        
        

        # Calcular noches (DateField en tu modelo)
        nights = None
        try:
            if reservation.check_in and reservation.check_out:
                delta = reservation.check_out - reservation.check_in
                nights = max(0, delta.days)
        except Exception:
            nights = None

        # Precio por noche: intentar sacar del room (fallback 0.00)
        price_per_night = Decimal('0.00')
        room = getattr(reservation, 'room', None)
        if room:
            try:
                price_per_night = Decimal(str(getattr(room, 'price_per_night', 0) or 0))
            except Exception:
                price_per_night = Decimal('0.00')

        # Subtotal (seguro)
        try:
            subtotal = (price_per_night * Decimal(nights or 1))
        except Exception:
            subtotal = Decimal(str(getattr(reservation, 'subtotal', 0) or 0))

        # Taxes / discount (intentar leer; fallback 0)
        try:
            taxes = Decimal(str(getattr(reservation, 'taxes', 0) or 0))
        except Exception:
            taxes = Decimal('0.00')
        try:
            discount = Decimal(str(getattr(reservation, 'discount', 0) or 0))
        except Exception:
            discount = Decimal('0.00')

        # Total: preferir campo explícito en la reserva si existe
        total = None
        if getattr(reservation, 'total_price', None) is not None:
            try:
                total = Decimal(str(reservation.total_price))
            except Exception:
                total = None
        if not total:
            try:
                total = subtotal + taxes - discount
            except Exception:
                total = Decimal('0.00')

        # Otros campos amigables
        currency = getattr(reservation, 'currency', 'CLP')
        status = getattr(reservation, 'status', None) or 'Pendiente'
        code = getattr(reservation, 'code', None) or None

        # Lógica simple de cancelación: permitimos cancelar si el check_in está en el futuro
        can_cancel = False
        try:
            if reservation.check_in and reservation.check_in > date.today():
                can_cancel = True
        except Exception:
            can_cancel = False

        # contexto final
        ctx.update({
            'nights': nights,
            'price_per_night': price_per_night,
            'subtotal': subtotal,
            'taxes': taxes,
            'discount': discount,
            'total': total,
            'currency': currency,
            'status': status,
            'code': code,
            'can_cancel': can_cancel,
        })
        return ctx


@login_required
def res_cancel(request, pk):
    """
    Vista POST para cancelar una reserva.
    - Si la reserva tiene un campo 'status', lo marcará como 'cancelled' y la guardará.
    - Si no existe ese campo, la eliminará.
    - Solo el dueño o staff puede cancelar.
    """
    reservation = get_object_or_404(Reservation, pk=pk)

    # permisos: solo dueño o staff
    if reservation.user and reservation.user != request.user and not request.user.is_staff:
        raise PermissionDenied("No tienes permiso para cancelar esta reserva.")

    # solo aceptar POST (formulario de confirmación)
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('res_detail', pk=reservation.pk)

    # comprobar confirm hidden field opcional
    confirm = request.POST.get('confirm', None)

    if not confirm:
        messages.warning(request, "No se confirmó la cancelación.")
        return redirect('res_detail', pk=reservation.pk)

    # Intentar marcar estado o eliminar
    if hasattr(reservation, 'status'):
        try:
            reservation.status = 'cancelled'
            reservation.save()
            messages.success(request, f"Reserva #{reservation.pk} cancelada correctamente.")
        except Exception:
            messages.error(request, "No fue posible cancelar la reserva. Contacta al administrador.")
    else:
        # si no hay campo status, borramos (opcional: puedes cambiar esto)
        try:
            reservation.delete()
            messages.success(request, "Reserva eliminada correctamente.")
        except Exception:
            messages.error(request, "No fue posible eliminar la reserva. Contacta al administrador.")

    return redirect('res_list')



class ResCreate(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("res_list")
    template_name = "hoteles/reservation_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # si estás en el formulario de creación, marca "Mis reservas"
        ctx["current"] = "res_list"
        return ctx

class ResUpdate(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("res_list")
    template_name = "hoteles/reservation_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # cuando editas una reserva queremos que el nav marque "Mis reservas"
        ctx["current"] = "res_list"   # o "res_detail" si prefieres ese valor
        return ctx


class ResDelete(LoginRequiredMixin, DeleteView):
    model = Reservation
    success_url = reverse_lazy("res_list")
    template_name = "hoteles/reservation_confirm_delete.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


# --------- Registro / Contacto ---------
class Registro(CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm    
    success_url = reverse_lazy('login')


class Contacto(TemplateView):
    template_name = "contacto.html"
    


@login_required
def res_invoice(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    # permisos: sólo el dueño o staff
    if reservation.user and reservation.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    # calcular noches y totales (misma lógica que ResDetail)
    nights = None
    try:
        if reservation.check_in and reservation.check_out:
            nights = max(0, (reservation.check_out - reservation.check_in).days)
    except Exception:
        nights = None

    # price per night desde room (fallback 0)
    price_per_night = Decimal('0.00')
    room = getattr(reservation, 'room', None)
    if room:
        try:
            price_per_night = Decimal(str(getattr(room, 'price_per_night', 0) or 0))
        except Exception:
            price_per_night = Decimal('0.00')

    try:
        subtotal = price_per_night * Decimal(nights or 1)
    except Exception:
        subtotal = Decimal(str(getattr(reservation, 'subtotal', 0) or 0))

    taxes = Decimal(str(getattr(reservation, 'taxes', 0) or 0))
    discount = Decimal(str(getattr(reservation, 'discount', 0) or 0))

    # total preferido por campo o calculado
    total = None
    if getattr(reservation, 'total_price', None) is not None:
        try:
            total = Decimal(str(reservation.total_price))
        except Exception:
            total = None
    if not total:
        try:
            total = subtotal + taxes - discount
        except Exception:
            total = Decimal('0.00')

    context = {
        'reservation': reservation,
        'nights': nights,
        'price_per_night': price_per_night,
        'subtotal': subtotal,
        'taxes': taxes,
        'discount': discount,
        'total': total,
        'currency': getattr(reservation, 'currency', 'CLP'),
    }
    return render(request, 'reservations/invoice.html', context)





#Funcion ara el clima
def get_weather_meteoblue():
    url = "https://my.meteoblue.com/packages/basic-1h_basic-day"
    params = {
        "apikey": "wtsb78MJjGLBo9rl",   # tu key
        "lat": -33.4569,
        "lon": -70.6483,
        "asl": 556,
        "format": "json"
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    # 👉 Debug: imprime la respuesta en consola
    print(data)

    if "data_day" in data and "time" in data["data_day"]:
        return {
            "fecha": data["data_day"]["time"][0],
            "temp_max": data["data_day"]["temperature_max"][0],
            "temp_min": data["data_day"]["temperature_min"][0],
            "precip": data["data_day"]["precipitation"][0],
        }
    return None


def home(request):
    clima = get_weather_meteoblue()
    return render(request, "home.html", {"clima": clima})