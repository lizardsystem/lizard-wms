# Copyright 2011 Nelen & Schuurmans

import sys
from optparse import make_option

from owslib.wms import WebMapService

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_wms import models


class Command(BaseCommand):
    help = "Make layers for all layers found in a configured WMS server."

    option_list = BaseCommand.option_list + (
        make_option('--slug',
                    help='slug of the WMSConnection that you want to update',
                    type='str',
                    default=None),
        make_option('--all',
                    action='store_true',
                    help='update all WMSConnection',
                    default=False),
        make_option('--flush',
                    action='store_true',
                    help='flush all WMSSources (before doing an update)',
                    default=False),
        )

    def handle(self, *args, **options):
        slug = options['slug']
        if (slug and
            models.WMSConnection.objects.filter(slug=slug).count() == 0):
            print "Slug %s: not found." % slug
            sys.exit(1)

        fetch_all = options['all']
        if any(options.iterkeys()) == False:
            print "Pass an argument."
            sys.exit(2)

        # Delete all objects depending on --all or --name.
        if options['flush']:
            if slug:
                qs_kwargs = {'connection__slug': slug}
            else:
                qs_kwargs = {'connection__isnull': False}
            models.WMSSource.objects.filter(**qs_kwargs).delete()
            if not slug and not fetch_all:
                sys.exit(0)

        connections = models.WMSConnection.objects.all()
        if slug and not fetch_all:
            connections = connections.filter(slug=slug)
        map(self.fetch_wms, connections)

    @transaction.commit_on_success
    def fetch_wms(self, connection):
        wms = WebMapService(connection.url)
        connection.save()

        for name, layer in wms.contents.iteritems():
            if layer.layers:
                #Meta layer, don't use
                continue

            kwargs = {'connection': connection,
                      'name': name}
            layer_instance, created = \
                models.WMSSource.objects.get_or_create(**kwargs)

            layer_style = layer.styles.values()
            # Not all layers have a description/legend.
            if len(layer_style):
                layer_instance.description = '<img src="%s" alt="%s" />' % (
                    layer_style[0]['legend'],
                    layer_style[0]['title'])
            else:
                layer_instance.description = None

            for attribute in ('url', 'options'):
                attr_value = getattr(connection, attribute)
                setattr(layer_instance, attribute, attr_value)
            layer_instance.category = connection.category.all()
            layer_instance.params = connection.params % layer.name
            layer_instance.save()
