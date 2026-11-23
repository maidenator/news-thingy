from django.core.management.base import BaseCommand

from news.services import fetch_all_outlets


class Command(BaseCommand):
    help = 'Fetch the latest articles from configured Philippine newsroom RSS feeds.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=3,
            help='Maximum number of stories to fetch per outlet (default: 3).',
        )
        parser.add_argument(
            '--outlet',
            type=str,
            default=None,
            help='Optional outlet slug to fetch from a single newsroom.',
        )

    def handle(self, *args, **options):
        result = fetch_all_outlets(
            limit_per_outlet=max(1, options['limit']),
            outlet_slug=options['outlet'],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Checked {result['checked']} outlet(s); imported {result['created']} new article(s)."
            )
        )
        for err in result['errors']:
            self.stderr.write(self.style.WARNING(f'Skipped: {err}'))
