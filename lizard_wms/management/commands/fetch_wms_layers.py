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

        for connection in connections:
            connection.fetch()
