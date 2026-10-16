import io
import tempfile

from django.core.management import call_command
from django.test import SimpleTestCase
from PIL import Image

from .imaging import strip_exif


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
