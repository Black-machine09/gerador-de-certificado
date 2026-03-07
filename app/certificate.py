from __future__ import annotations

import os
from datetime import datetime

from fpdf import FPDF

from .settings import Settings


def _template_path() -> str | None:
    base = os.path.join(os.getcwd(), "assets")
    jpg = os.path.join(base, "template.jpg")
    png = os.path.join(base, "template.png")
    if os.path.exists(jpg):
        return jpg
    if os.path.exists(png):
        return png
    return None


def _fit_font_size(pdf: FPDF, text: str, max_width: float, start_size: int) -> int:
    size = start_size
    while size > 12:
        pdf.set_font("Times", "B", size=size)
        width = pdf.get_string_width(text)
        if width <= max_width:
            return size
        size -= 1
    return size


def _format_date_pt(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y")


def generate_certificate_pdf(*, full_name: str, certificate_id: str, settings: Settings) -> bytes:
    pdf = FPDF(orientation="L", unit="pt", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    page_w, page_h = pdf.w, pdf.h

    template = _template_path()
    if template:
        # JPEG normalmente funciona sem Pillow. Para PNG pode precisar de Pillow.
        pdf.image(template, x=0, y=0, w=page_w, h=page_h)
    else:
        # Fallback simples (sem imagem)
        pdf.set_draw_color(31, 56, 115)
        pdf.set_line_width(3)
        pdf.rect(18, 18, page_w - 36, page_h - 36)
        pdf.set_draw_color(179, 153, 77)
        pdf.set_line_width(1)
        pdf.rect(30, 30, page_w - 60, page_h - 60)

    max_name_width = page_w * settings.cert_name_max_width_ratio
    name_size = _fit_font_size(pdf, full_name, max_name_width, settings.cert_name_start_size)
    pdf.set_font("Times", "B", size=name_size)
    name_width = pdf.get_string_width(full_name)

    x = (page_w - name_width) / 2
    # fpdf2 usa coordenadas com origem no topo-esquerdo (y cresce para baixo).
    y_from_bottom = page_h * settings.cert_name_y + settings.cert_name_dy_px
    y = page_h - y_from_bottom
    pdf.set_text_color(26, 26, 26)
    pdf.text(x=x, y=y, txt=full_name)

    issued_at = _format_date_pt(datetime.now())
    # Evitar caracteres fora de latin-1 nos core fonts (ex.: "•")
    meta = f"Emitido em {issued_at} - ID {certificate_id}"
    meta_size = 10
    pdf.set_font("Helvetica", size=meta_size)
    meta_width = pdf.get_string_width(meta)
    pdf.set_text_color(64, 64, 64)
    pdf.text(x=page_w - meta_width - 28, y=page_h - 26, txt=meta)

    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin-1", errors="ignore")
    return bytes(out)
