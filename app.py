# -*- coding: utf-8 -*-
# ============================================================
#  CALCULADORA DE ÁREA DE ZONA PET PARA CONJUNTOS RESIDENCIALES
#  Versión web en Streamlit
#  Autora: Anny Piñeros Pedroza
#
#  Problema: no existe una norma que indique cuánta área de
#  zona pet necesita un conjunto según su número de viviendas.
#  Este programa estima cuántos perros tendrá el conjunto,
#  cuántos usarán la zona al mismo tiempo y qué área se
#  requiere, a partir de encuestas a familias multiespecie.
# ============================================================

import math

import streamlit as st

# ---------- CONSTANTES (datos base del estudio) ----------
# Promedios de las encuestas Torres 20 de Julio y Fontibón Reservado
PORC_MASCOTA = 0.40       # 40% de los hogares tiene mascota
PORC_PERRO = 0.575        # 57,5% de esos hogares tiene perro
TASA_PERROS = 1.295       # promedio de perros por hogar con perro

# Criterios de uso de la zona pet
PORC_AFORO = 0.34         # 34% de los perros salen en horario pico
TURNOS = 6                # el uso se reparte en 6 turnos

# Área por perro: promedio de Ma x Fc de la tabla de coeficientes
# (8.75 + 8.75 + 10 + 11.25 + 8.75) / 5 = 9.5 m²
M2_POR_PERRO = 9.5


# ---------- FUNCIONES DE APOYO (solo visualización) ----------
def formato_numero(valor, decimales=2):
    """Escribe el número con formato colombiano: 1.234,56"""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def dibujar_planta(perros, area):
    """Devuelve un SVG con la planta de la zona pet y un punto por perro."""
    # Lienzo y rectángulo de la planta (proporción de referencia 3:2)
    ancho_svg, alto_svg = 600, 430
    x0, y0 = 70, 30
    ancho_rect, alto_rect = 480, 320

    # Medidas de referencia en metros para las cotas
    if area > 0:
        lado_largo = math.sqrt(area * 1.5)
        lado_corto = area / lado_largo
    else:
        lado_largo = lado_corto = 0

    partes = [
        f'<svg viewBox="0 0 {ancho_svg} {alto_svg}" width="100%" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Planta de la zona pet con {perros} perros en simultáneo" '
        'style="color:inherit;font-family:\'Barlow Condensed\',\'Arial Narrow\',sans-serif">',
        '<defs><pattern id="piso" width="14" height="14" patternUnits="userSpaceOnUse" '
        'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="14" '
        'stroke="#6E9B5A" stroke-opacity="0.25" stroke-width="1.5"/></pattern></defs>',
        # Piso de la zona pet
        f'<rect x="{x0}" y="{y0}" width="{ancho_rect}" height="{alto_rect}" '
        'fill="#6E9B5A" fill-opacity="0.12"/>',
        f'<rect x="{x0}" y="{y0}" width="{ancho_rect}" height="{alto_rect}" fill="url(#piso)"/>',
        # Muro perimetral
        f'<rect x="{x0}" y="{y0}" width="{ancho_rect}" height="{alto_rect}" fill="none" '
        'stroke="currentColor" stroke-width="5"/>',
        # Acceso (vano en el muro inferior)
        f'<line x1="{x0 + 40}" y1="{y0 + alto_rect}" x2="{x0 + 90}" y2="{y0 + alto_rect}" '
        'stroke="#6E9B5A" stroke-opacity="0.6" stroke-width="7"/>',
        f'<path d="M {x0 + 40} {y0 + alto_rect} A 50 50 0 0 1 {x0 + 90} {y0 + alto_rect - 50}" '
        'fill="none" stroke="currentColor" stroke-opacity="0.45" stroke-width="1"/>',
        f'<line x1="{x0 + 90}" y1="{y0 + alto_rect}" x2="{x0 + 90}" y2="{y0 + alto_rect - 50}" '
        'stroke="currentColor" stroke-opacity="0.45" stroke-width="1"/>',
    ]

    # Puntos: uno por cada perro en simultáneo, repartidos en filas
    if perros > 0:
        columnas = math.ceil(math.sqrt(perros * ancho_rect / alto_rect))
        filas = math.ceil(perros / columnas)
        paso_x = ancho_rect / columnas
        paso_y = alto_rect / filas
        radio = max(3, min(paso_x, paso_y) * 0.28)
        radio = min(radio, 22)
        dibujados = 0
        for fila in range(filas):
            en_fila = min(columnas, perros - dibujados)
            margen = (ancho_rect - en_fila * paso_x) / 2  # centra la última fila
            for col in range(en_fila):
                cx = x0 + margen + paso_x * (col + 0.5)
                cy = y0 + paso_y * (fila + 0.5)
                partes.append(
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radio:.1f}" fill="#E3A21A" '
                    'stroke="currentColor" stroke-width="1.2"/>'
                )
                dibujados += 1

    # Cotas (líneas de dimensión con marcas a 45°, como en un plano)
    y_cota = y0 + alto_rect + 38
    x_cota = x0 - 34
    tick = 6
    partes += [
        # Cota horizontal
        f'<line x1="{x0}" y1="{y_cota}" x2="{x0 + ancho_rect}" y2="{y_cota}" '
        'stroke="currentColor" stroke-width="1"/>',
        f'<line x1="{x0}" y1="{y0 + alto_rect + 10}" x2="{x0}" y2="{y_cota + 8}" '
        'stroke="currentColor" stroke-width="0.8"/>',
        f'<line x1="{x0 + ancho_rect}" y1="{y0 + alto_rect + 10}" x2="{x0 + ancho_rect}" '
        f'y2="{y_cota + 8}" stroke="currentColor" stroke-width="0.8"/>',
        f'<line x1="{x0 - tick}" y1="{y_cota + tick}" x2="{x0 + tick}" y2="{y_cota - tick}" '
        'stroke="currentColor" stroke-width="1.6"/>',
        f'<line x1="{x0 + ancho_rect - tick}" y1="{y_cota + tick}" x2="{x0 + ancho_rect + tick}" '
        f'y2="{y_cota - tick}" stroke="currentColor" stroke-width="1.6"/>',
        f'<text x="{x0 + ancho_rect / 2}" y="{y_cota - 8}" text-anchor="middle" '
        f'font-size="17" fill="currentColor">{formato_numero(lado_largo)} m</text>',
        # Cota vertical
        f'<line x1="{x_cota}" y1="{y0}" x2="{x_cota}" y2="{y0 + alto_rect}" '
        'stroke="currentColor" stroke-width="1"/>',
        f'<line x1="{x0 - 10}" y1="{y0}" x2="{x_cota - 8}" y2="{y0}" '
        'stroke="currentColor" stroke-width="0.8"/>',
        f'<line x1="{x0 - 10}" y1="{y0 + alto_rect}" x2="{x_cota - 8}" y2="{y0 + alto_rect}" '
        'stroke="currentColor" stroke-width="0.8"/>',
        f'<line x1="{x_cota - tick}" y1="{y0 + tick}" x2="{x_cota + tick}" y2="{y0 - tick}" '
        'stroke="currentColor" stroke-width="1.6"/>',
        f'<line x1="{x_cota - tick}" y1="{y0 + alto_rect + tick}" x2="{x_cota + tick}" '
        f'y2="{y0 + alto_rect - tick}" stroke="currentColor" stroke-width="1.6"/>',
        f'<text x="{x_cota - 9}" y="{y0 + alto_rect / 2}" text-anchor="middle" font-size="17" '
        f'fill="currentColor" transform="rotate(-90 {x_cota - 9} {y0 + alto_rect / 2})">'
        f'{formato_numero(lado_corto)} m</text>',
        "</svg>",
    ]
    return "".join(partes)


# ---------- CONFIGURACIÓN DE LA PÁGINA ----------
st.set_page_config(
    page_title="Calculadora de zona pet",
    page_icon="🐾",
    layout="wide",
)

st.markdown(
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');"
    ".zp-titulo{font-family:'Barlow Condensed','Arial Narrow',sans-serif;font-weight:700;"
    "font-size:2.6rem;line-height:1.05;margin:0 0 .2rem 0;}"
    ".zp-sub{opacity:.7;margin:0 0 1.2rem 0;max-width:60ch;}"
    ".zp-area{font-family:'Barlow Condensed','Arial Narrow',sans-serif;font-weight:700;"
    "font-size:clamp(4rem,9vw,7.5rem);line-height:.9;letter-spacing:-.01em;}"
    ".zp-area small{font-size:.38em;font-weight:600;margin-left:.15em;}"
    ".zp-etiqueta{opacity:.7;font-size:1rem;margin-top:.6rem;}"
    ".zp-dato{font-size:1rem;margin-top:1.4rem;line-height:1.6;}"
    ".zp-punto{display:inline-block;width:.8em;height:.8em;border-radius:50%;"
    "background:#E3A21A;border:1px solid currentColor;vertical-align:-.05em;margin-right:.35em;}"
    ".zp-cadena{display:flex;flex-wrap:wrap;align-items:stretch;gap:.4rem;margin-top:.5rem;}"
    ".zp-paso{flex:1 1 120px;border-left:3px solid #6E9B5A;padding:.3rem .8rem;}"
    ".zp-paso b{display:block;font-family:'Barlow Condensed','Arial Narrow',sans-serif;"
    "font-size:2.2rem;font-weight:600;line-height:1.1;}"
    ".zp-paso span{font-size:.9rem;opacity:.75;}"
    ".zp-final{border-left-color:#E3A21A;}"
    ".zp-sep{align-self:center;font-size:1.8rem;opacity:.45;}"
    "@media (max-width:640px){.zp-sep{display:none;}}"
    "</style>",
    unsafe_allow_html=True,
)

st.markdown('<h1 class="zp-titulo">Calculadora de zona pet</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="zp-sub">Estima el área de zona pet que necesita un conjunto residencial '
    "según su número de viviendas, con base en encuestas a familias multiespecie.</p>",
    unsafe_allow_html=True,
)

# ---------- 1. ENTRADA DE DATOS ----------
col_nombre, col_viviendas = st.columns([2, 1])
with col_nombre:
    nombre_proyecto = st.text_input("Nombre del proyecto", placeholder="Ej.: Torres 20 de Julio")
with col_viviendas:
    viviendas = int(
        st.number_input("Número de viviendas del conjunto", min_value=0, value=200, step=1)
    )

# ---------- 2. PROCESAMIENTO (misma secuencia del programa original) ----------
# Hogares que tienen alguna mascota
hogares_mascota = round(viviendas * PORC_MASCOTA)

# Hogares donde vive al menos un perro
hogares_perro = round(hogares_mascota * PORC_PERRO)

# Total de perros (un hogar puede tener más de uno)
total_perros = round(hogares_perro * TASA_PERROS)

# Perros que estarán al mismo tiempo en la zona
perros_simultaneo = round(total_perros * PORC_AFORO / TURNOS)

# Área total que necesita la zona pet
area_total = perros_simultaneo * M2_POR_PERRO

# ---------- 3. SALIDA DE RESULTADOS ----------
st.divider()
titulo_resultados = f"Resultados · {nombre_proyecto.upper()}" if nombre_proyecto.strip() else "Resultados"
st.subheader(titulo_resultados)

col_planta, col_area = st.columns([3, 2], gap="large")

with col_planta:
    st.markdown(dibujar_planta(perros_simultaneo, area_total), unsafe_allow_html=True)

with col_area:
    perro_texto = "perro" if perros_simultaneo == 1 else "perros"
    st.markdown(
        f'<div class="zp-area">{formato_numero(area_total)}<small>m²</small></div>'
        '<div class="zp-etiqueta">Área requerida para la zona pet</div>'
        f'<div class="zp-dato"><span class="zp-punto"></span>'
        f"{perros_simultaneo} {perro_texto} en simultáneo<br>"
        f"{formato_numero(M2_POR_PERRO, 1)} m² por perro</div>",
        unsafe_allow_html=True,
    )
    if perros_simultaneo == 0:
        st.info(
            "Con este número de viviendas el cálculo no alcanza un perro en simultáneo. "
            "Aumenta el número de viviendas para ver el área requerida."
        )
    st.caption("Las cotas usan una proporción de referencia 3:2 para el mismo área.")

# Cadena de cálculo
st.markdown("#### Cadena de cálculo")
pasos = [
    (viviendas, "viviendas"),
    (hogares_mascota, "hogares con mascota"),
    (hogares_perro, "hogares con perro"),
    (total_perros, "total de perros"),
    (perros_simultaneo, "perros en simultáneo"),
]
bloques = []
for i, (valor, etiqueta) in enumerate(pasos):
    clase = "zp-paso zp-final" if i == len(pasos) - 1 else "zp-paso"
    bloques.append(f'<div class="{clase}"><b>{formato_numero(valor, 0)}</b><span>{etiqueta}</span></div>')
    if i < len(pasos) - 1:
        bloques.append('<div class="zp-sep">›</div>')
st.markdown(f'<div class="zp-cadena">{"".join(bloques)}</div>', unsafe_allow_html=True)

st.caption(
    "Datos base: promedios de las encuestas Torres 20 de Julio y Fontibón Reservado. "
    "40 % de hogares con mascota, 57,5 % de ellos con perro, 1,295 perros por hogar, "
    "34 % de aforo en horario pico repartido en 6 turnos y 9,5 m² por perro."
)
