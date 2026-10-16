import io

from django.db.models.signals import pre_save
from PIL import Image, ImageOps


def strip_exif(data):
    """Bytes ripuliti da EXIF/XMP (orientamento applicato ai pixel), o None se gia' puliti/non immagine."""
    try:
        img = Image.open(io.BytesIO(data))
        fmt = img.format
        if not (img.getexif() or "xmp" in img.info or "XML:com.adobe.xmp" in img.info):
            return None
        out = io.BytesIO()
        # Pillow salva exif/xmp solo se passati esplicitamente: un save semplice li scarta.
        # quality="keep" riusa le quantizzazioni JPEG (nessuna ulteriore perdita di qualita').
        res = ImageOps.exif_transpose(img)
        kw = {}
        if fmt == "JPEG":  # "keep" vale solo se non c'e' stata rotazione (pixel ricodificati: q95)
            kw = {"quality": "keep"} if res.format == "JPEG" else {"quality": 95}
        res.save(out, format=fmt, **kw)
        return out.getvalue()
    except Exception:
        return None  # non e' un'immagine decodificabile: la validazione e' di ImageField


def _strip_on_upload(sender, instance, **kwargs):
    for f in sender._meta.fields:
        ff = getattr(instance, f.name, None) if f.get_internal_type() == "ImageField" else None
        if ff and not ff._committed:  # solo nuovi upload
            ff.file.seek(0)
            clean = strip_exif(ff.file.read())
            ff.file.seek(0)
            if clean is not None:
                from django.core.files.base import ContentFile

                ff.file = ContentFile(clean, name=ff.name)


def connect(*models):
    for m in models:
        pre_save.connect(_strip_on_upload, sender=m, dispatch_uid=f"strip_exif_{m.__name__}")
