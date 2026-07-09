from django.contrib import admin

from .models import EmailVerificationCode, TravelBooking, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(TravelBooking)
class TravelBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'package_name', 'destination', 'travelers', 'start_date', 'status', 'booked_at')
    list_filter = ('status', 'destination', 'booked_at')
    search_fields = ('user__username', 'user__email', 'package_name', 'destination', 'contact_phone')


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'purpose', 'code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('email',)
