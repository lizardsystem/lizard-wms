# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

# from rest_framework.reverse import reverse
# from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from lizard_maptree.models import Category
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import lizard_structure.views
import lizard_structure.items

from lizard_wms.serializers import CategorySerializer

# Data source: bare-bones pointer at categories
# Project: categories
# Layer: wms sources/urls
# Features: none, at the moment.

DEFAULT_HEADING_LEVEL = 1


class DataSourceView(lizard_structure.views.DataSourceView):
    # Potentially rename this as "Projects".

    def projects(self):
        """Return maptree categories.

        Maptree categories are usable as root objects of lizard pages.
        """
        categories = Category.objects.all()
        # TODO: also return 'root' object.
        return CategorySerializer(categories,
                                  context=self.get_serializer_context()).data


class ProjectView(GenericAPIView):
    """Structure of a lizard-wms category with its layers.

    Lizard-wms (actually, lizard-maptree) provides categories into which WMS
    layers are grouped. Categories can be nested.

    """
    ROOT_SLUG = 'root'

    def tree(self,
             parent=None,
             heading_level=DEFAULT_HEADING_LEVEL,
             result=None):
        """
        Make tree for homepage using categories and WMS sources.
        """
        if result is None:
            result = []
        sub_categories = Category.objects.filter(parent=parent)
        for category in sub_categories:
            # Append sub categories as headings
            row = lizard_structure.items.HeadingItem(
                name=category.name,
                heading_level=heading_level,
                description=category.description)
            result.append(row.to_api())
            # Continue deeper into the tree.
            self.tree(parent=category,
                           heading_level=heading_level + 1,
                           result=result)
        # Append workspace-acceptables.
        if parent is not None:
            result += [self._wms_source_to_api(wms_source)
                       for wms_source in parent.wmssource_set.all()]
        return result

    def _wms_source_to_api(self, wms_source):
        return lizard_structure.items.LayerItem(
            name=wms_source.name,
            description=wms_source.name,
            wms_url=wms_source.url,
            wms_params=wms_source._params,  # Real jsonfield.
            # ^^^ Misses layers.
            wms_options=wms_source.options,  # TODO: turn into dict.
            ).to_api()

    def about_ourselves(self):
        """Return metadata about ourselves."""
        return CategorySerializer(self.category,
                                  context=self.get_serializer_context()).data

    def get(self, response, slug=None, format=None):
        self.slug = slug
        self.category = get_object_or_404(Category, slug=self.slug)
        # ^^^ This doesn't work with the non-existing root category.
        result = {}
        result['about_ourselves'] = self.about_ourselves()
        result['menu'] = self.tree(parent=self.category)
        return Response(result)
