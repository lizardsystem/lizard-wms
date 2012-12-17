# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import json

# from rest_framework.reverse import reverse
# from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from lizard_maptree.models import Category
from rest_framework.generics import GenericAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
import lizard_maptree
import pkginfo

from lizard_wms.serializers import CategorySerializer
import lizard_wms

# Data source: bare-bones pointer at categories
# Project: categories
# Layer: wms sources/urls
# Features: none, at the moment.

DEFAULT_HEADING_LEVEL = 1


class DataSourceView(GenericAPIView):
    """WMS layers configured in lizard-wms/lizard-maptree.

    Info on ourselves. Django app, version, etc.

    List of categories as projects.
    """

    def _version_of_package(self, package):
        """Return version number of package.

        Package should be a real imported package, not a string.
        """
        return pkginfo.installed.Installed(package).version

    @property
    def projects(self):
        """Return maptree categories.

        Maptree categories are usable as root objects of lizard pages.
        """
        categories = Category.objects.all()
        # TODO: also return 'root' object.
        return CategorySerializer(categories,
                                  context=self.get_serializer_context()).data

    @property
    def data(self):
        """Return metadata about ourselves."""
        return {'generator': 'Lizard-wms {} (and lizard-maptree {})'.format(
                self._version_of_package(lizard_wms),
                self._version_of_package(lizard_maptree))}

    def get(self, response, format=None):
        result = {}
        result['about_ourselves'] = self.data
        result['projects'] = self.projects
        return Response(result)


class Heading(object):
    """Wrapper/interface for heading objects in a Project/menu."""
    # TODO: move elsewhere.
    menu_type = 'heading'

    def __init__(self,
                 name=None,
                 description=None,
                 # edit_link=None,
                 heading_level=None,
                 extra_data=None,
                 klass=None):
        self.name = name
        self.description = description
        self.heading_level = heading_level or DEFAULT_HEADING_LEVEL
        # self.edit_link = edit_link
        self.extra_data = extra_data
        self.klass = klass

    def to_api(self):
        result = {}
        for attr in ['name',
                     'description',
                     'heading_level',
                     'extra_data',
                     'klass',
                     'menu_type']:
            value = getattr(self, attr)
            if value is None:
                continue
            result[attr] = value
        return result


class WorkspaceAcceptable(object):
    """Wrapper/interface for layer/acceptable objects in a Project/menu."""
    # TODO: move elsewhere.
    menu_type = 'workspace_acceptable'

    def __init__(self,
                 name=None,
                 description=None,
                 # edit_link=None,
                 wms_url=None,
                 wms_params=None,
                 wms_options=None,
                 ):
        self.name = name
        self.description = description
        self.wms_url = wms_url
        self.wms_params = wms_params
        self.wms_options = wms_options

    def to_api(self):
        result = {}
        for attr in ['name',
                     'description',
                     'wms_url',
                     'wms_params',
                     'wms_options',
                     ]:
            value = getattr(self, attr)
            if value is None:
                continue
            result[attr] = value
        return result


class ProjectView(GenericAPIView):
    """Structure of a lizard-wms category with its layers.

    Lizard-wms (actually, lizard-maptree) provides categories into which WMS
    layers are grouped. Categories can be nested.

    """
    ROOT_SLUG = 'root'

    def _get_tree(self,
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
            row = Heading(name=category.name,
                          heading_level=heading_level,
                          description=category.description)
            result.append(row.to_api())
            # Continue deeper into the tree.
            self._get_tree(parent=category,
                           heading_level=heading_level + 1,
                           result=result)
        # Append workspace-acceptables.
        if parent is not None:
            result += [self._wms_source_to_api(wms_source)
                       for wms_source in parent.wmssource_set.all()]
        return result

    def _wms_source_to_api(self, wms_source):
        return WorkspaceAcceptable(
            name=wms_source.name,
            description=wms_source.name,
            wms_url=wms_source.url,
            wms_params=wms_source._params,  # Real jsonfield.
            # ^^^ Misses layers.
            wms_options=wms_source.options,  # TODO: turn into dict.
            ).to_api()

    @property
    def tree(self):
        if self.slug == self.ROOT_SLUG:
            start_category = get_object_or_404(Category, slug=None)
        else:
            start_category = get_object_or_404(Category, slug=self.slug)

        return self._get_tree(
            get_object_or_404(start_category, slug=self.slug))

    def get(self, response, slug=None, format=None):
        self.slug = slug
        result = {}
        result['menu'] = self.tree
        return Response(result)
