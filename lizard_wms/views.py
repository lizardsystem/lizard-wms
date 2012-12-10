# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import pkginfo
import lizard_maptree
# from rest_framework.generics import SingleObjectAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from rest_framework.response import Response
from lizard_maptree.models import Category

from lizard_wms.serializers import CategorySerializer
import lizard_wms

# Data source: bare-bones pointer at categories
# Project: categories
# Layer: wms sources/urls
# Features: none, at the moment.


class DataSourceView(APIView):
    """WMS layers configured in lizard-wms/lizard-maptree.

    Info on ourselves. Django app, version, etc.

    List of categories as projects.
    """

    def _version_of_package(self, package):
        """Return version number of package.

        Package should be a real imported package, not a string.
        """
        return pkginfo.installed.Installed(package).version

    # @property
    # def metadata(self):
    #     """Return metadata, in this case just wms/maptree versions."""
    #     return {'generator': 'Lizard-wms {} (and lizard-maptree {})'.format(
    #             self._version_of_package(lizard_wms),
    #             self._version_of_package(lizard_maptree))}

    @property
    def projects(self):
        """Return maptree categories.

        Maptree categories are usable as root objects of lizard pages.
        """
        categories = Category.objects.all()
        # TODO: also return 'root' object.
        return CategorySerializer(categories).data

    def get(self, response, format=None):
        result = {}
        # result['metadata'] = self.metadata
        result['projects'] = self.projects
        return Response(result)


# class DataSourceView(ListAPIView):
#     model = Category
#     serializer_class = CategorySerializer


class ProjectView(RetrieveAPIView):
    model = Category
    serializer_class = CategorySerializer
