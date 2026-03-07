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


def _normalize_name(full_name: str) -> str:
    return " ".join((full_name or "").strip().split())


def _split_name_into_lines(pdf: FPDF, text: str, max_width: float) -> list[str]:
    words = [w for w in text.split(" ") if w]
    if len(words) <= 1:
        return [text]

    best: tuple[float, list[str]] | None = None
    for i in range(1, len(words)):
        left = " ".join(words[:i])
        right = " ".join(words[i:])
        worst = max(pdf.get_string_width(left), pdf.get_string_width(right))
        if worst <= max_width and (best is None or worst < best[0]):
            best = (worst, [left, right])

    if best is not None:
        return best[1]

    best = None
    for i in range(1, len(words)):
        left = " ".join(words[:i])
        right = " ".join(words[i:])
        worst = max(pdf.get_string_width(left), pdf.get_string_width(right))
        if best is None or worst < best[0]:
            best = (worst, [left, right])
    return best[1] if best else [text]


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
    normalized_name = _normalize_name(full_name)
    name_size = _fit_font_size(pdf, normalized_name, max_name_width, settings.cert_name_start_size)
    pdf.set_font("Times", "B", size=name_size)

    lines = [normalized_name]
    # If it still doesn't fit at the minimum, split into 2 lines and re-fit.
    if pdf.get_string_width(normalized_name) > max_name_width and name_size <= 12:
        lines = _split_name_into_lines(pdf, normalized_name, max_name_width)
        widest_line = max(lines, key=lambda s: pdf.get_string_width(s))
        name_size = _fit_font_size(pdf, widest_line, max_name_width, settings.cert_name_start_size)
        pdf.set_font("Times", "B", size=name_size)

    # fpdf2 usa coordenadas com origem no topo-esquerdo (y cresce para baixo).
    y_from_bottom = page_h * settings.cert_name_y + settings.cert_name_dy_px
    y_center = page_h - y_from_bottom

    line_gap = max(6, int(name_size * 0.35))
    line_step = name_size + line_gap
    start_y = y_center - (line_step * (len(lines) - 1)) / 2

    pdf.set_text_color(26, 26, 26)
    for idx, line in enumerate(lines):
        line_width = pdf.get_string_width(line)
        x = (page_w - line_width) / 2
        y = start_y + idx * line_step
        pdf.text(x=x, y=y, txt=line)

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
