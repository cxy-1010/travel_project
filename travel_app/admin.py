from django.contrib import admin
from .models import (
    Destination, TourPackage, Hotel, RoomType, Flight, SeatClass,
    ExtraService, Testimonial, BlogPost, SpecialOffer, Subscriber,
    Booking, UserReview, Favorite, UserProfile,
)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'country', 'city')


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'price', 'duration_days', 'rating', 'is_recommended', 'is_active')
    list_filter = ('is_recommended', 'is_active', 'destination')
    search_fields = ('name',)
    list_editable = ('is_recommended', 'is_active')


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'stars', 'price_per_night', 'rating')
    list_filter = ('stars', 'city')
    search_fields = ('name', 'city')
    inlines = [RoomTypeInline]


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price_per_night', 'capacity', 'available_rooms')
    list_filter = ('hotel',)


class SeatClassInline(admin.TabularInline):
    model = SeatClass
    extra = 1


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('airline', 'flight_number', 'origin_city', 'destination_city', 'price', 'departure_time', 'flight_type')
    list_filter = ('airline', 'flight_type', 'origin_city', 'destination_city')
    search_fields = ('airline', 'origin_city', 'destination_city')
    date_hierarchy = 'departure_time'
    inlines = [SeatClassInline]


@admin.register(SeatClass)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ('flight', 'class_type', 'price', 'available_seats')
    list_filter = ('class_type',)


@admin.register(ExtraService)
class ExtraServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'price', 'is_active')
    list_filter = ('service_type', 'is_active')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'location', 'rating', 'is_active')
    list_filter = ('rating', 'is_active')
    search_fields = ('guest_name',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'published_date', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'author')
    date_hierarchy = 'published_date'


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'original_price', 'discount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active',)
    search_fields = ('email',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking_type', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'booking_type')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('extra_services',)


@admin.register(UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'review_type', 'title', 'rating', 'is_approved', 'created_at')
    list_filter = ('review_type', 'rating', 'is_approved')
    search_fields = ('title', 'user__username')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite_type', 'created_at')
    list_filter = ('favorite_type',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'preferred_currency')
    search_fields = ('user__username',)
