from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from concerti.imaging import strip_exif

EXT = {".jpg", ".jpeg", ".png", ".webp"}


class Command(BaseCommand):
    help = "Rimuove EXIF/XMP dalle immagini in MEDIA_ROOT (o --root)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--root", default=str(settings.MEDIA_ROOT))

    def handle(self, *args, dry_run, root, **opts):
        n = 0
        for p in Path(root).rglob("*"):
            if p.suffix.lower() not in EXT or not p.is_file():
                continue
            clean = strip_exif(p.read_bytes())
            if clean is None:
                continue
            n += 1
            self.stdout.write(f"{'[dry-run] ' if dry_run else ''}{p}")
            if not dry_run:
                p.write_bytes(clean)
        self.stdout.write(f"{n} file {'da ripulire' if dry_run else 'ripuliti'}")
