# Portfolio Status

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![Oracle DB](https://img.shields.io/badge/Oracle_DB-F80000?style=flat&logo=oracle&logoColor=white)
![Render](https://img.shields.io/badge/Render-000000?style=flat&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat&logo=vercel&logoColor=white)

Panel en vivo que revisa automáticamente, cada pocos minutos, si cada uno de
los proyectos del portafolio sigue en línea y qué tan rápido responde — con
historial de disponibilidad y una tarjeta por proyecto, cada una con enlace
directo a su demo.

## Demo en vivo

**Panel:** [frontend-nine-topaz-99.vercel.app](https://frontend-nine-topaz-99.vercel.app/)
**API:** [portafolio-status.onrender.com](https://portafolio-status.onrender.com/)

## Qué hace

- Un backend revisa periódicamente la URL de cada proyecto y guarda el
  resultado (si respondió, con qué código HTTP, y en cuántos milisegundos).
- El frontend muestra una tarjeta por proyecto: su estado actual, el tiempo
  de respuesta, el % de disponibilidad de los últimos 7 días, y un historial
  reciente en forma de barras. Cada tarjeta es un enlace directo al proyecto.
- La lista de proyectos monitoreados está en `backend/app/projects.py`.

## Diagrama de Arquitectura

```mermaid
flowchart TB

    subgraph Clientes["👤 Cliente"]
        Browser["🌐 Navegador Web<br/>Panel de monitoreo"]
    end

    subgraph Vercel["▲ Vercel"]
        subgraph Frontend["Frontend — React 18 · Vite 6 · TypeScript"]
            App["App.tsx<br/>Polling cada 60 s"]
            APIClient["api.ts<br/>fetch()"]
            Card["ProjectCard<br/>Estado · latencia · %"]
            Spark["Sparkline<br/>Historial 7 días"]
            Types["types.ts<br/>Tipos compartidos"]
        end
    end

    subgraph Render["☁️ Render (Docker)"]
        subgraph Backend["Backend — FastAPI + Uvicorn"]
            Main["main.py<br/>Rutas REST"]
            Scheduler["APScheduler<br/>Verificación periódica"]
            Status["status.py<br/>Verificación HTTP"]
            Projects["projects.py<br/>Lista de URLs"]
            HTTPX["httpx<br/>Cliente HTTP"]
            OracleDriver["oracledb<br/>Driver Oracle"]
        end
    end

    subgraph OracleCloud["🗄️ Oracle Cloud"]
        ADB[("Oracle Autonomous Database<br/>Esquema PORTFOLIO_STATUS<br/>Historial · Estado actual")]
    end

    subgraph Externos["🌐 Proyectos del portafolio"]
        P1["Proyecto 1"]
        P2["Proyecto 2"]
        P3["Proyecto N"]
    end

    %% ---- Flujo de datos ----
    Browser -->|HTTPS| App
    App --> APIClient
    App --> Card
    Card --> Spark
    Card --> Types
    APIClient -->|REST API| Main
    Main --> Projects
    Main --> Status
    Scheduler --> Status
    Status --> HTTPX
    HTTPX -->|GET| P1
    HTTPX -->|GET| P2
    HTTPX -->|GET| P3
    Status --> OracleDriver
    OracleDriver -->|TCPS| ADB
    Main --> OracleDriver

    %% ---- Colores de marca (Brand Colors) ----
    classDef react fill:#61DAFB,stroke:#20232A,stroke-width:2px,color:#20232A,rx:12,ry:12;
    classDef typescript fill:#3178C6,stroke:#00273F,stroke-width:2px,color:#FFFFFF,rx:12,ry:12;
    classDef fastapi fill:#009688,stroke:#004D40,stroke-width:2px,color:#FFFFFF,rx:12,ry:12;
    classDef python fill:#3572A5,stroke:#1A3A5C,stroke-width:2px,color:#FFFFFF,rx:12,ry:12;
    classDef oracle fill:#F80000,stroke:#7F0000,stroke-width:2px,color:#FFFFFF;
    classDef vercel fill:#000000,stroke:#333333,stroke-width:2px,color:#FFFFFF,rx:12,ry:12;
    classDef render fill:#8A05FF,stroke:#4A008C,stroke-width:2px,color:#FFFFFF,rx:12,ry:12;
    classDef neutral fill:#F5F5F5,stroke:#CCCCCC,stroke-width:1px,color:#333333,rx:10,ry:10;

    class Browser neutral;
    class App,APIClient,Card,Spark react;
    class Types typescript;
    class Main,Scheduler,Status,Projects fastapi;
    class HTTPX,OracleDriver python;
    class ADB oracle;
    class P1,P2,P3 neutral;

    %% ---- Estilos de subgráficos ----
    style Clientes fill:#FAFAFA,stroke:#DDDDDD,stroke-width:1px,rx:14,ry:14;
    style Vercel fill:#F0F0F0,stroke:#000000,stroke-width:2px,stroke-dasharray:6 4,rx:16,ry:16;
    style Frontend fill:#E1F5FE,stroke:#61DAFB,stroke-width:1px,rx:12,ry:12;
    style Render fill:#F3E8FF,stroke:#8A05FF,stroke-width:2px,stroke-dasharray:6 4,rx:16,ry:16;
    style Backend fill:#E0F2F1,stroke:#009688,stroke-width:1px,rx:12,ry:12;
    style OracleCloud fill:#FFF0F0,stroke:#F80000,stroke-width:2px,stroke-dasharray:6 4,rx:16,ry:16;
    style Externos fill:#FFF8E1,stroke:#FFB300,stroke-width:1px,stroke-dasharray:4 3,rx:14,ry:14;
```

## Estructura

```
portfolio-status/
├── backend/     FastAPI — revisa los proyectos y expone la API
├── frontend/    React + Vite — el panel visual
└── db/          Script SQL para crear el esquema en Oracle
```

## A qué se conecta

- **Base de datos:** Oracle Autonomous Database, en un esquema propio
  (`PORTFOLIO_STATUS`), separado del de cualquier otro proyecto.
- **Backend:** desplegado en Render.
- **Frontend:** desplegado en Vercel.

## Cómo correrlo en local

1. Base de datos: correr `db/001_crear_esquema.sql` en tu Autonomous
   Database (ver los comentarios del archivo).
2. Backend:
```
   cd backend
   cp .env.example .env   # completar con tus datos
   pip install -r requirements.txt
   uvicorn app.main:app --reload
```
3. Frontend:
```
   cd frontend
   cp .env.example .env
   npm install
   npm run dev
```

También se puede levantar todo con `docker compose up` desde la raíz del
repo (requiere tener el wallet de Oracle ya descomprimido en
`backend/wallet/`).

## Despliegue

- **Base de datos:** Oracle Autonomous Database (Always Free).
- **Backend:** Render, como servicio Docker (usa `backend/Dockerfile`); el
  wallet de Oracle se pasa codificado en base64 en la variable de entorno
  `ORACLE_WALLET_B64`, ya que Render no tiene disco persistente.
- **Frontend:** Vercel, con `frontend` como Root Directory y `VITE_API_URL`
  apuntando a la URL del backend en Render.