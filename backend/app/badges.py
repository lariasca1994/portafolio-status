"""Insignias SVG para el README del perfil de GitHub.

Todas comparten el mismo diseño: píldora oscura con borde sutil, un
indicador de color a la izquierda, un texto principal en negrita y un
texto secundario atenuado. GitHub las muestra con <img>, así que no hay
JavaScript: solo SVG con una animación suave en el indicador.
"""

from html import escape

ALTO = 32
FUENTE = "Segoe UI, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"


def _ancho(texto: str, tam: float, negrita: bool = False) -> float:
    # Aproximación del ancho del texto (no hay métricas de fuente en el servidor).
    base = 0.555 if negrita else 0.515
    return sum(tam * (base + 0.06 if c.isupper() or c.isdigit() else base) for c in texto)


def _indicador(x: float, color: str, icono: str, animado: bool) -> str:
    cy = ALTO / 2
    pulso = (
        f'<circle cx="{x}" cy="{cy}" r="5" fill="{color}" opacity=".5">'
        '<animate attributeName="r" values="5;10;5" dur="2.4s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values=".5;0;.5" dur="2.4s" repeatCount="indefinite"/>'
        "</circle>"
        if animado
        else ""
    )
    if icono == "check":
        return (
            f'<circle cx="{x}" cy="{cy}" r="8" fill="{color}"/>'
            f'<path d="M{x - 3.6},{cy + 0.2} l2.5,2.6 l4.8,-5.4" fill="none" stroke="#fff" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    return pulso + f'<circle cx="{x}" cy="{cy}" r="5" fill="{color}"/>'


def insignia(principal: str, secundario: str, color: str, *, icono: str = "punto",
             animado: bool = True, etiqueta: str | None = None) -> str:
    """Devuelve el SVG. `etiqueta` agrega una pastilla de color al final (p. ej. "EN VIVO")."""
    principal_e, secundario_e = escape(principal), escape(secundario)
    x_texto = 34
    w_principal = _ancho(principal, 13, negrita=True)
    x_sep = x_texto + w_principal + 10
    x_sec = x_sep + 10
    w_sec = _ancho(secundario, 12.5) if secundario else 0
    fin = (x_sec + w_sec) if secundario else (x_texto + w_principal)

    pastilla = ""
    if etiqueta:
        w_et = _ancho(etiqueta, 10.5, negrita=True) + 18
        x_et = fin + 12
        pastilla = (
            f'<rect x="{x_et:.1f}" y="7" width="{w_et:.1f}" height="18" rx="9" fill="{color}" fill-opacity=".16" '
            f'stroke="{color}" stroke-opacity=".55"/>'
            f'<text x="{x_et + w_et / 2:.1f}" y="19.6" text-anchor="middle" font-size="10.5" font-weight="700" '
            f'letter-spacing=".6" fill="{color}">{escape(etiqueta)}</text>'
        )
        fin = x_et + w_et

    ancho = round(fin + 14)
    separador = (
        f'<circle cx="{x_sep:.1f}" cy="{ALTO / 2}" r="1.6" fill="#6E7681"/>'
        f'<text x="{x_sec:.1f}" y="20.5" font-size="12.5" fill="#9DA7B3">{secundario_e}</text>'
        if secundario
        else ""
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{ALTO}" viewBox="0 0 {ancho} {ALTO}" role="img" aria-label="{principal_e} {secundario_e}">
  <defs>
    <linearGradient id="fondo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1B2230"/><stop offset="1" stop-color="#0F141C"/>
    </linearGradient>
  </defs>
  <rect x=".75" y=".75" width="{ancho - 1.5}" height="{ALTO - 1.5}" rx="{(ALTO - 1.5) / 2}" fill="url(#fondo)" stroke="#30363D" stroke-width="1.5"/>
  <g font-family="{FUENTE}">
    {_indicador(17, color, icono, animado)}
    <text x="{x_texto}" y="20.5" font-size="13" font-weight="700" fill="#F0F6FC">{principal_e}</text>
    {separador}
    {pastilla}
  </g>
</svg>"""
