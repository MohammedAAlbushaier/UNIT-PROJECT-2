from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Campaign, Donation, Accomplishment, CampaignImage

# Register your models here.


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('userprofile',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class CampaignImageInline(admin.TabularInline):
    model = CampaignImage
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'progress_percentage')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    inlines = [CampaignImageInline]

    def progress_percentage(self, obj):
        return f"{obj.progress_percentage:.0f}%"

    progress_percentage.short_description = 'Progress'


class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'amount', 'campaign', 'donation_date', 'anonymous')
    list_filter = ('campaign', 'donation_date', 'anonymous')
    search_fields = ('donor__username', 'donor__first_name', 'donor__last_name', 'message')
    date_hierarchy = 'donation_date'


class AccomplishmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    list_filter = ('date',)
    search_fields = ('title', 'description')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(Accomplishment, AccomplishmentAdmin)