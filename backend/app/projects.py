"""
Lista de proyectos que este dashboard revisa.

Cada uno tiene: slug (identificador corto, así se guarda en Oracle),
nombre para mostrar, URL real donde vive el proyecto, y su color de
marca (el mismo color que ya se usa en el mockup aprobado, en modo
claro y oscuro) — el frontend lo usa para pintar la barra de historial
de cada tarjeta.

Para agregar o quitar un proyecto del dashboard, solo edita esta lista.
"""

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
        "name": "PRPagos",
        "url": "https://prpagos-web-1087929107584.southamerica-east1.run.app",
        "color_light": "#c1452c",
        "color_dark": "#e2734f",
    },
    {
        "slug": "reservas-corferias",
        "name": "reservas-corferias",
        "url": "https://reservas-corferias.blueocean-86680030.eastus.azurecontainerapps.io",
        "color_light": "#0078d4",
        "color_dark": "#3b9ef0",
    },
    {
        "slug": "gestor-incidentes-ti",
        "name": "GestorIncidentesTI",
        "url": "https://gestorincidentesti.livelywater-fe29fe0b.australiaeast.azurecontainerapps.io",
        "color_light": "#0891b2",
        "color_dark": "#22d3ee",
    },
    {
        "slug": "gestor-casos-qa",
        "name": "gestor-casos-qa",
        "url": "https://immxew65sfxj7nubwzlszdimfi0qegzc.lambda-url.us-east-1.on.aws",
        "color_light": "#0d9488",
        "color_dark": "#2dd4bf",
    },
    {
        "slug": "taskflow",
        "name": "TaskFlow",
        "url": "https://taskflow-812302804238.us-central1.run.app",
        "color_light": "#0e6b45",
        "color_dark": "#4c9a73",
    },
    {
        "slug": "calidad-afiliaciones",
        "name": "Calidad-Afiliaciones",
        "url": "https://calidad-afiliaciones.blueocean-86680030.eastus.azurecontainerapps.io",
        "color_light": "#f2960c",
        "color_dark": "#fdba3d",
    },
    {
        "slug": "verificador-api",
        "name": "Verificador API",
        "url": "https://eofvlnitsiuodup4eywdcenxwu0adgbz.lambda-url.us-east-1.on.aws",
        "color_light": "#336791",
        "color_dark": "#5b8fbf",
    },
]

PROJECTS_BY_SLUG = {p["slug"]: p for p in PROJECTS}
