# Copyright 2011 Nelen & Schuurmans

import sys
from optparse import make_option

from django.core.management.base import BaseCommand

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
        )

    def handle(self, *args, **options):
        slug = options['slug']
        if (slug and
            models.WMSConnection.objects.filter(slug=slug).count() == 0):
            print "Slug %s: not found." % slug
            sys.exit(1)

        fetch_all = options['all']

        if not fetch_all and not slug:
            print "Pass an argument."
            sys.exit(2)

        connections = models.WMSConnection.objects.all()
        if slug:
            connections = connections.filter(slug=slug)

        for connection in connections:
            fetched = connection.fetch()
            connection.delete_layers(keep_layers=fetched)
