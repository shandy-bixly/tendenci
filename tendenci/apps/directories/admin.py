from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.directories.models import DirectoryPricing
from tendenci.apps.directories.affiliates.models import AllowedConnection
from tendenci.apps.directories.forms import DirectoryPricingForm
from tendenci.apps.directories.models import Category as DirectoryCategory
from tendenci.apps.theme.templatetags.static import static


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ['headline', 'create_dt']

# admin.site.register(Directory, DirectoryAdmin)

class DirectoryPricingAdmin(admin.ModelAdmin):
    list_display = ['duration', 'regular_price', 'premium_price',
                    'regular_price_member', 'premium_price_member', 'status']
    fieldsets = (
        (None, {'fields': ('duration', 'regular_price', 'premium_price',
                           'regular_price_member', 'premium_price_member', 'status',)}),
    )
    form = DirectoryPricingForm

admin.site.register(DirectoryPricing, DirectoryPricingAdmin)


class CategoryAdminInline(admin.TabularInline):
    fieldsets = ((None, {'fields': ('name', 'slug', 'position')}),)
    prepopulated_fields = {'slug': ['name']}
    model = DirectoryCategory
    extra = 0
    verbose_name = _("Directory Sub-Category")
    verbose_name_plural = _("Directory Sub-Categories")
    ordering = ['name']


class DirectoryCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'sub_categories',
        'slug',
        'position'
    ]
    list_display_links = ('id', )
    list_editable = ['position']
    inlines = (CategoryAdminInline,)
    prepopulated_fields = {'slug': ['name']}
    fieldsets = ((None, {'fields': ('name', 'slug')}),)
    ordering = ['position']
    
    class Media:
        css = {
            "all": (static("css/websymbols.css"),)
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
        )

    @mark_safe
    def sub_categories(self, instance):
        return ', '.join(DirectoryCategory.objects.filter(parent=instance).values_list('name', flat=True))

    def get_queryset(self, request):
        qs = super(DirectoryCategoryAdmin, self).get_queryset(request)
        return qs.filter(parent__isnull=True)


class AllowedConnectionAdmin(admin.ModelAdmin):
    list_display = ['corp_type', 'allow_connected_by']
    fieldsets = (
        (None, {'fields': ('corp_type', 'member_types')}),
    )
    
    def allow_connected_by(self, instance):
        return ', '.join([m.name for m in instance.member_types.all()])
    allow_connected_by.short_description = 'Allow to be connected by'


admin.site.register(AllowedConnection, AllowedConnectionAdmin)
admin.site.register(DirectoryCategory, DirectoryCategoryAdmin)
