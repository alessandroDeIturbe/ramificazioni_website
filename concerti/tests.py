import datetime
import io
import json
import re
import tempfile

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from PIL import Image

from .imaging import strip_exif
from .models import Brano, Concerto, Partecipazione, Persona, Sede


def _jpeg_gps():
    ex = Image.Exif()
    ex[0x0112] = 6  # orientamento
    ex[0x8825] = {1: "N", 2: (45.0, 28.0, 0.0)}  # GPS IFD
    b = io.BytesIO()
    Image.new("RGB", (40, 20), "red").save(b, "JPEG", exif=ex)
    return b.getvalue()


class StripExifTest(SimpleTestCase):
    def test_helper_e_command(self):
        src = _jpeg_gps()
        assert Image.open(io.BytesIO(src)).getexif().get_ifd(0x8825)
        out = Image.open(io.BytesIO(strip_exif(src)))
        self.assertEqual(out.format, "JPEG")
        self.assertEqual(len(out.getexif()), 0)
        self.assertEqual(out.size, (20, 40))  # orientamento applicato
        self.assertIsNone(strip_exif(strip_exif(src)))  # gia' pulita
        with tempfile.TemporaryDirectory() as d:
            open(f"{d}/a.jpg", "wb").write(src)
            call_command("strip_exif", root=d, dry_run=True)
            self.assertEqual(open(f"{d}/a.jpg", "rb").read(), src)
            call_command("strip_exif", root=d)
            self.assertEqual(len(Image.open(f"{d}/a.jpg").getexif()), 0)


class PreviewStaffOnlyTest(SimpleTestCase):
    """L'host di anteprima rimanda al login chi non e' staff; gli altri host passano."""

    def _get(self, host, path, staff):
        from types import SimpleNamespace

        from django.test import RequestFactory, override_settings

        from .middleware import PreviewStaffOnlyMiddleware

        request = RequestFactory().get(path, HTTP_HOST=host)
        request.user = SimpleNamespace(is_staff=staff)
        with override_settings(PREVIEW_HOST="anteprima.test", ALLOWED_HOSTS=["*"]):
            return PreviewStaffOnlyMiddleware(lambda r: "ok")(request)

    def test_anteprima(self):
        self.assertEqual(self._get("anteprima.test", "/it/", False).status_code, 302)
        self.assertEqual(self._get("anteprima.test", "/it/", True), "ok")
        self.assertEqual(self._get("anteprima.test", "/admin/login/", False), "ok")
        self.assertEqual(self._get("anteprima.test", "/static/a.css", False), "ok")
        self.assertEqual(self._get("ramificazioni.ch", "/it/", False), "ok")


class SeoTest(TestCase):
    """robots.txt, sitemap i18n (solo pubblicati), canonical/hreflang, JSON-LD sicuro."""

    @classmethod
    def setUpTestData(cls):
        sede = Sede.objects.create(nome="Sala </script><b>x</b>", indirizzo="Via 1 & 2, Lugano")
        cls.c = Concerto.objects.create(
            numero_edizione=1, stagione="2025/26", data=datetime.date(2026, 3, 12),
            ora=datetime.time(20, 30), sede=sede, pubblicato=True,
        )
        Brano.objects.create(concerto=cls.c, compositore="A </script>", titolo="T1")
        p = Persona.objects.create(nome="Interprete Uno", ruolo="interprete")
        Partecipazione.objects.create(concerto=cls.c, persona=p)
        cls.bozza = Concerto.objects.create(
            numero_edizione=2, stagione="2025/26", data=datetime.date(2026, 4, 1), sede=sede
        )
        cls.senza_sede = Concerto.objects.create(
            numero_edizione=3, stagione="2025/26", data=datetime.date(2026, 5, 1), pubblicato=True
        )

    @staticmethod
    def _jsonld(html):
        blocchi = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        return [json.loads(b) for b in blocchi]

    def test_robots(self):
        r = self.client.get("/robots.txt")
        self.assertEqual(r["Content-Type"], "text/plain")
        self.assertContains(r, "Disallow: /admin/")
        self.assertContains(r, "Sitemap: http://testserver/sitemap.xml")

    def test_sitemap(self):
        body = self.client.get("/sitemap.xml").content.decode()
        for lang in ("it", "de", "fr", "en"):
            self.assertIn(f"<loc>https://testserver/{lang}/events/{self.c.slug}/</loc>", body)
            self.assertIn(f"<loc>https://testserver/{lang}/stagioni/2025/26/</loc>", body)
            self.assertIn(f"<loc>https://testserver/{lang}/archivio/</loc>", body)
        self.assertIn(f'hreflang="en" href="https://testserver/en/events/{self.c.slug}/"', body)
        self.assertNotIn('hreflang="x-default"', body)  # x-default solo nell'HTML
        self.assertNotIn(self.bozza.slug, body)
        self.assertNotIn("/contributors/", body)

    def test_canonical_hreflang(self):
        html = self.client.get(f"/de/events/{self.c.slug}/?utm=x").content.decode()
        self.assertIn(f'<link rel="canonical" href="http://testserver/de/events/{self.c.slug}/">', html)
        for lang in ("it", "de", "fr", "en"):
            self.assertIn(f'hreflang="{lang}" href="http://testserver/{lang}/events/{self.c.slug}/"', html)
        self.assertIn(f'hreflang="x-default" href="http://testserver/it/events/{self.c.slug}/"', html)
        stagione = self.client.get("/en/stagioni/2025/26/").content.decode()
        self.assertIn('hreflang="fr" href="http://testserver/fr/stagioni/2025/26/"', stagione)

    def test_jsonld_music_event(self):
        html = self.client.get(f"/it/events/{self.c.slug}/").content.decode()
        (ev,) = self._jsonld(html)  # un solo blocco: il </script> nei dati non lo spezza
        self.assertEqual(ev["@type"], "MusicEvent")
        self.assertEqual(ev["startDate"], "2026-03-12T20:30:00+01:00")
        self.assertEqual(ev["location"]["name"], "Sala </script><b>x</b>")
        self.assertEqual(ev["performer"], [{"@type": "Person", "name": "Interprete Uno"}])
        self.assertEqual(ev["workPerformed"][0]["composer"]["name"], "A </script>")
        self.assertEqual(ev["url"], f"http://testserver/it/events/{self.c.slug}/")

    def test_jsonld_solo_pubblicati_con_sede(self):
        self.assertEqual(self.client.get(f"/it/events/{self.bozza.slug}/").status_code, 404)
        html = self.client.get(f"/it/events/{self.senza_sede.slug}/").content.decode()
        self.assertEqual(self._jsonld(html), [])

    def test_jsonld_organization_home(self):
        (org,) = self._jsonld(self.client.get("/fr/").content.decode())
        self.assertEqual(org["@type"], "Organization")
        self.assertEqual(org["url"], "http://testserver/")
