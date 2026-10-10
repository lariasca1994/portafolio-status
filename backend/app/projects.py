"""
Lista de proyectos que este dashboard revisa.

Cada uno tiene: slug (identificador corto, así se guarda en Oracle),
nombre para mostrar, URL real donde vive el proyecto, y su color de
marca (el mismo color que ya se usa en el mockup aprobado, en modo
claro y oscuro) — el frontend lo usa para pintar la barra de historial
de cada tarjeta.

Opcional: "check_url" es la dirección que se revisa cuando no coincide con la
del enlace (p. ej. frontend estático en Vercel y API en Render: se enlaza el
frontend y se revisa el health check de la API, que sí puede caerse).

Opcional: "revisar_horas" (horas de Bogotá) reemplaza la revisión cada pocos
minutos por revisiones a horas fijas. Se usa en los proyectos que escalan a cero
y tienen bases sin servidor con cuota gratuita (Azure Container Apps + Azure SQL):
una visita cada 5 minutos no los deja dormir y agota la cuota a mitad de mes.

Para agregar o quitar un proyecto del dashboard, solo edita esta lista.
"""

# Horas (Bogotá) en que se revisa todo lo que puede dormir: contenedores que escalan a
# cero (Azure, Cloud Run), Lambdas, backends gratuitos de Render y sus bases (Azure SQL,
# Neon, OCI). Cuatro revisiones al día dejan dormir cada servicio el resto del tiempo:
#   Render ≈ 15 min despierto por revisión → ≈ 31 h/mes por servicio (de 750 h gratis)
#   Azure Container Apps ≈ 6 min por revisión → ≈ 12 h/mes por app
#   Neon / Azure SQL: las rutas revisadas no tocan la base o la despiertan pocos minutos
# Lo estático (Vercel) no duerme ni cuesta: se sigue revisando cada pocos minutos.
HORAS_DORMIDOS = [8, 12, 16, 20]

PROJECTS = [
    {
        "slug": "colombiatech2",
        "name": "ColombiaTech2",
        "url": "https://colombia-tech2.vercel.app",
        "color_light": "#12a454",
        "color_dark": "#22c55e",
    },
    {
        "slug": "prpagos",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "PRPagos",
        "url": "https://prpagos-web-1087929107584.southamerica-east1.run.app",
        "color_light": "#c1452c",
        "color_dark": "#e2734f",
    },
    {
        "slug": "reservas-corferias",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "reservas-corferias",
        "url": "https://reservas-corferias.blueocean-86680030.eastus.azurecontainerapps.io",
        # /up responde sin tocar la base: despierta solo el contenedor.
        "check_url": "https://reservas-corferias.blueocean-86680030.eastus.azurecontainerapps.io/up",
        "color_light": "#0078d4",
        "color_dark": "#3b9ef0",
    },
    {
        "slug": "gestor-incidentes-ti",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "GestorIncidentesTI",
        "url": "https://gestorincidentesti.livelywater-fe29fe0b.australiaeast.azurecontainerapps.io",
        "color_light": "#0891b2",
        "color_dark": "#22d3ee",
    },
    {
        "slug": "gestor-casos-qa",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "gestor-casos-qa",
        "url": "https://immxew65sfxj7nubwzlszdimfi0qegzc.lambda-url.us-east-1.on.aws",
        "color_light": "#0d9488",
        "color_dark": "#2dd4bf",
    },
    {
        "slug": "taskflow",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "TaskFlow",
        "url": "https://taskflow-812302804238.us-central1.run.app",
        "color_light": "#0e6b45",
        "color_dark": "#4c9a73",
    },
    {
        "slug": "calidad-afiliaciones",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "Calidad-Afiliaciones",
        "url": "https://calidad-afiliaciones.blueocean-86680030.eastus.azurecontainerapps.io",
        "color_light": "#f2960c",
        "color_dark": "#fdba3d",
    },
    {
        "slug": "verificador-api",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "Verificador API",
        "url": "https://eofvlnitsiuodup4eywdcenxwu0adgbz.lambda-url.us-east-1.on.aws",
        "color_light": "#336791",
        "color_dark": "#5b8fbf",
    },
    {
        "slug": "motor-horarios-oci",
        "revisar_horas": HORAS_DORMIDOS,
        "name": "Motor de Horarios",
        "url": "https://motor-horarios-oci.vercel.app",
        "check_url": "https://motor-horarios-oci-1.onrender.com/health/db",
        "color_light": "#00758f",
        "color_dark": "#5cc6de",
    },
    {
        # Se revisa la interfaz en Vercel (estática): consultar la API cada pocos
        # minutos impediría que su contenedor y sus bases se pausen sin uso. La API y
        # el login con MFA los cubren las corridas E2E de qa-evidencia.
        "slug": "qalabspbvi",
        "name": "QALabSPBVI",
        "url": "https://qalabspbvi.vercel.app",
        "color_light": "#b7791f",
        "color_dark": "#f5b301",
    },
    {
        # Se revisa la interfaz estática en Vercel: consultar la API (Render, gratis)
        # cada pocos minutos no la dejaría dormir. La API la cubre qa-evidencia.
        "slug": "syspulse",
        "name": "SysPulse",
        "url": "https://syspulse.vercel.app",
        "color_light": "#0b3a7e",
        "color_dark": "#00a9e0",
    },
]

PROJECTS_BY_SLUG = {p["slug"]: p for p in PROJECTS}
