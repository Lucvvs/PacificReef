from .views import get_weather_meteoblue 

def clima_global(request):
    
    clima_data = get_weather_meteoblue()
    
    return {
        'clima': clima_data
    }