from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm
from .forms import ReservationForm


from .models import Hotel, Room, Reservation


class Home(TemplateView):
    template_name = "base_home.html"


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
        return super().get_queryset().filter(user=self.request.user)



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


class ResDelete(LoginRequiredMixin, DeleteView):
    model = Reservation
    success_url = reverse_lazy("res_list")
    template_name = "hoteles/reservation_confirm_delete.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


# --------- Registro / Contacto ---------
class Registro(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


class Contacto(TemplateView):
    template_name = "contacto.html"