from django.contrib import admin
from .models import Flight, Guide, GuideComment, GuideFavorite, Hotel, Order, TravelNews


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'user', 'likes', 'created_at')
    search_fields = ('title', 'destination', 'content', 'user__username')
    list_filter = ('destination', 'created_at')


@admin.register(GuideComment)
class GuideCommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'guide', 'user', 'created_at')
    search_fields = ('title', 'destination', 'content', 'user__username')
    list_filter = ('destination', 'created_at')


@admin.register(GuideFavorite)
class GuideFavoriteAdmin(admin.ModelAdmin):
    list_display = ('guide', 'user', 'created_at')
    search_fields = ('guide__title', 'guide__destination', 'user__username')
    list_filter = ('created_at',)


admin.site.register(Flight)
admin.site.register(Hotel)
admin.site.register(Order)
admin.site.register(TravelNews)
