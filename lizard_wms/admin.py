"""Configuration of the admin interface"""
import urlparse

from django.contrib import admin
from django import forms
from lizard_maptree.models import Category
from lizard_wms import models

def source_domain(obj):
    """Return the domain of the WMSSource url."""
    return ("%s" % urlparse.urlparse(obj.url).netloc)

source_domain.short_description = 'Domein'

class CategoryField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.name, obj.slug)

class FeatureLineInline(admin.TabularInline):
    """Show the feature lines as inlines under their WMS source."""
    model = models.FeatureLine

    fields = ('name', 'description', 'visible', 'order_using',
              'render_as', 'in_hover', 'use_as_id',)

    ordering = ('-visible', 'order_using')
    readonly_fields = ('name',)
    extra = 0

class WMSSourceForm(forms.ModelForm):
    category = CategoryField(queryset=Category.objects.all())
    class Meta:
        model = models.WMSSource

class WMSSourceAdmin(admin.ModelAdmin):
    """WMS source admin. Show a few fields that may be edited regularly
    (layer name, category) and hide the rest in a collapsed section."""

    list_display = ('name',  source_domain, 'connection')
    search_fields = ('name', 'url', 'category__name', 'connection__title')
    list_filter = ('category', )

    fieldsets = (
        (None, {
                'fields': ('name', 'category'),
                }),
        ('Details', {
                'classes': ('collapse',),
                'fields':
                ('url', 'params', 'options', 'description', 'connection'),
                }),
        )
    inlines = [FeatureLineInline]
    form = WMSSourceForm

admin.site.register(models.WMSSource, WMSSourceAdmin)

for model in [models.WMSConnection]:
    admin.site.register(model)
