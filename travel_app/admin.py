from django.contrib import admin
from .models import Flight, FlightPrice, Hotel, HotelRoom, Package, PackageExtra, Booking, Guide, GuideComment

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_no', 'departure_city', 'arrival_city', 'departure_time']
    search_fields = ['flight_no', 'departure_city', 'arrival_city']

@admin.register(FlightPrice)
class FlightPriceAdmin(admin.ModelAdmin):
    list_display = ['flight', 'supplier', 'cabin_class', 'price']
    list_filter = ['cabin_class', 'supplier']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'stars']
    search_fields = ['name', 'city']

@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'room_type', 'price_per_night']

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'duration', 'original_price', 'discount_price', 'rating']
    search_fields = ['name', 'destination']
    list_filter = ['duration']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'num_people', 'total_price', 'status', 'travel_date']
    list_filter = ['status']
    search_fields = ['user__username', 'contact_name']

@admin.register(PackageExtra)
class PackageExtraAdmin(admin.ModelAdmin):
    list_display = ['package', 'name', 'price']

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'user', 'likes']

@admin.register(GuideComment)
class GuideCommentAdmin(admin.ModelAdmin):
    list_display = ['guide', 'user', 'content']

admin.site.site_header = '旅游网站后台管理'
admin.site.site_title = '旅游网站管理'
