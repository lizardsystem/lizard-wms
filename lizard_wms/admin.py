"""Configuration of the admin interface"""
import urlparse
import urllib2
import logging

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.db import models as django_models
from django.utils.translation import ugettext as _

from lizard_maptree.models import Category
from lizard_wms import models

logger = logging.getLogger(__name__)


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
    category = CategoryField(queryset=Category.objects.all(),
                             required=False)

    class Meta:
        model = models.WMSSource


class WMSSourceAdmin(admin.ModelAdmin):
    """WMS source admin. Show a few fields that may be edited regularly
    (layer name, category) and hide the rest in a collapsed section."""

    list_display = ('display_name', 'layer_name',  source_domain, 'connection',
                    'enable_search')
    search_fields = ('display_name', 'layer_name', 'url', 'category__name',
                     'connection__title')
    list_filter = ('category', )
    actions = ['update_bounding_box', 'initialize_bounding_box']

    def update_bounding_box(self, request, queryset, force=True):
        num_updated = 0
        num_failed = 0
        for wms_source in queryset:
            try:
                if wms_source.update_bounding_box(force=force):
                    wms_source.save()
                    num_updated += 1
                else:
                    num_failed += 1
            except Exception, e:
                msg = ("Something went wrong when updating %s. " +
                       "Look at %s directly. %s")
                msg = msg % (wms_source.layer_name,
                             wms_source.capabilities_url(),
                             e)
                logger.exception(msg)
                messages.error(request, msg)
        if num_failed > 0:
            messages.error(
                request, "Failed to load/update %s bounding boxes." % (
                    num_failed))
        self.message_user(request,
                          "Loaded/updated %s bounding boxes." % (num_updated))

    update_bounding_box.short_description = _("Update all bounding boxes")

    def initialize_bounding_box(self, request, queryset):
        self.update_bounding_box(request, queryset, force=False)

    initialize_bounding_box.short_description = _(
        "Set the not-yet-set bounding boxes")

    def save_model(self, request, layer_instance, form, change):
        # Update the bounding box if it has not been set.
        if not layer_instance.update_bounding_box(force=False):
            messages.error(request, "Error updating bounding box.")
        layer_instance.save()
        if layer_instance.bbox:
            inlines = layer_instance.featureline_set
            if len(inlines.all()) < 1:
                layer_instance.get_feature_info()
                self.message_user(request, "Loaded/updated feature info.")

    fieldsets = (
        (None, {'fields': ('display_name', 'layer_name', 'category')}),
        ('Details',
         {'classes': ('collapse',),
          'fields': ('url', '_params', 'options', 'description',
                     'metadata', 'connection', 'legend_url', 'bbox',
                     'show_legend', 'enable_search'),
          }),
    )
    inlines = [FeatureLineInline]
    form = WMSSourceForm


class SourceInline(admin.TabularInline):
    model = models.WMSSource
    fields = ('display_name', 'layer_name', 'options', 'category',
              'index')
    extra = 0
    formfield_overrides = {
        django_models.TextField: {
            'widget': forms.Textarea(attrs={'rows': '3', 'cols': '50'})
        }
    }
    ordering = ('display_name',)


class WMSConnectionForm(forms.ModelForm):
    category = CategoryField(queryset=Category.objects.all(),
                             required=False)

    class Meta:
        model = models.WMSConnection


class WMSConnectionAdmin(admin.ModelAdmin):

    list_display = ('slug', 'title', 'url')
    actions = ['reload']
    form = WMSConnectionForm
    inlines = [SourceInline]

    def reload(self, request, queryset):
        num_fetched_updated = 0
        num_deleted = 0
        for wms_connection in queryset:
            try:
                fetched = wms_connection.fetch()
                num_fetched_updated += len(fetched)
                deleted = wms_connection.delete_layers(keep_layers=fetched)
                num_deleted += deleted
            except AttributeError, e:
                msg = ("Probably an error message instead of a proper WMS " +
                       "response from the url: look at %s directly. " +
                       "Or the server doesn't support WMS 1.1.1. %s")
                msg = msg % (wms_connection.capabilities_url(), e)
                logger.exception(msg)
                messages.error(request, msg)
            except urllib2.HTTPError, e:
                logger.exception(e)
                msg = "URL not found? Network error? Look at %s directly. %s"
                messages.error(
                    request,
                    msg % (wms_connection.url, e))

        self.message_user(
            request,
            "Loaded/updated %s WMS sources, deleted %s." % (
                num_fetched_updated, num_deleted))

    reload.short_description = (
        "Reload WMS connections and update their WMS sources.")


class FilterPageAdminForm(forms.ModelForm):

    class Meta:
        model = models.FilterPage

    def __init__(self, *args, **kwargs):
        super(FilterPageAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['available_filters'].queryset = (
                models.FeatureLine.objects.filter(
                    wms_layer=self.instance.wms_source))
        except models.WMSSource.DoesNotExist:
            pass


class FilterPageAdmin(admin.ModelAdmin):
    form = FilterPageAdminForm
    list_display = ('slug', 'name', 'wms_source')
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('available_filters',)


admin.site.register(models.WMSSource, WMSSourceAdmin)
admin.site.register(models.WMSConnection, WMSConnectionAdmin)
admin.site.register(models.FilterPage, FilterPageAdmin)
