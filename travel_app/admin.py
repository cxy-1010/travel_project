from django.contrib import admin

from .models import EmailVerificationCode, TravelBooking, TravelPackage, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'price', 'is_featured', 'is_active', 'display_order', 'updated_at')
    list_filter = ('is_featured', 'is_active', 'destination')
    search_fields = ('name', 'destination', 'hotel', 'transport', 'meal')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'is_active', 'display_order')


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
