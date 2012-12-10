# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import unicode_literals

from rest_framework import serializers
from lizard_maptree.models import Category

# from lizard_wms.models import WMSSource


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """Tree-like menu per category. Every category can be a sidebar."""
    url = serializers.HyperlinkedIdentityField(view_name='wms_api_project')

    class Meta:
        model = Category
        fields = ('url', 'name', 'description')
