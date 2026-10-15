# 📘 Manual de usuario · Portfolio Status

Guía para leer el panel y usar las insignias: qué muestra cada dato, qué información se maneja y
qué protege la plataforma. Para la parte técnica vuelve al [README](../README.md).

**Panel:** [frontend-nine-topaz-99.vercel.app](https://frontend-nine-topaz-99.vercel.app/) ·
**API:** [portafolio-status.onrender.com](https://portafolio-status.onrender.com/)

## Contenido

1. [Proyecto: objetivos y alcances](#1-proyecto-objetivos-y-alcances)
2. [Glosario](#2-glosario)
3. [Plataformas, base de datos y servicios](#3-plataformas-base-de-datos-y-servicios)
4. [Paso a paso](#4-paso-a-paso)
5. [Seguridad: tu información protegida](#5-seguridad-tu-información-protegida)
6. [Agradecimientos](#6-agradecimientos)

---

## 1. Proyecto: objetivos y alcances

### Objetivo

Cada pocos minutos, el backend visita la dirección de cada proyecto del portafolio, anota si
respondió y en cuánto tiempo, y guarda el historial. El panel lo muestra en tarjetas, y las
insignias en vivo lo llevan a los README de GitHub.

### Alcance: qué necesitas y qué esperar

- El panel es **público**: no pide cuenta ni datos.
- Se actualiza solo cada 60 segundos; no hace falta recargar.

## 2. Glosario

Palabras técnicas que aparecen en este manual, explicadas en lenguaje simple.

| Término | Qué significa |
|---|---|
| **API** | Puerta de entrada de un programa para que otros programas le pidan o le envíen datos. |
| **Arranque en frío** | Los servidores gratuitos se apagan sin uso; la primera visita tarda unos segundos mientras vuelven a encenderse. |
| **Backend** | La parte de la aplicación que trabaja "detrás": procesa lo que envías y habla con la base de datos. |
| **Base de datos** | Lugar donde la aplicación guarda la información de forma ordenada y permanente. |
| **Cifrado / TLS / HTTPS** | Protección que codifica la información mientras viaja, para que nadie en el camino pueda leerla. |
| **Cookie** | Pequeño dato que el navegador guarda para recordar tu sesión en ese sitio. |
| **Frontend** | La parte de la aplicación que ves y usas en el navegador. |
| **Insignia (badge)** | Pequeña imagen que muestra un estado en vivo, por ejemplo en un README de GitHub. |
| **Modo mantenimiento** | Pantalla que aparece cuando el servicio o su base de datos no responden; se recupera sola cuando vuelven. |
| **Métricas** | Medidas de un equipo como uso de CPU, memoria, disco o red. |
| **Navegador** | Programa con el que abres páginas web: Chrome, Edge, Firefox, Safari. |
| **Nube** | Servidores de una empresa (Amazon, Microsoft, Google, Oracle…) donde la aplicación funciona sin depender de un computador propio. |
| **Prueba E2E** | Prueba que recorre la aplicación de punta a punta como lo haría una persona real. |
| **Tema claro / oscuro** | Combinación de colores de la interfaz; puedes elegir la clara o la oscura. |
| **Uptime / disponibilidad** | Porcentaje del tiempo en que un servicio estuvo funcionando. |
| **Variables de entorno / secretos** | Claves y contraseñas internas de la aplicación, guardadas fuera del código para que no queden expuestas. |

## 3. Plataformas, base de datos y servicios

Qué servicio de nube, base de datos o API usa el proyecto y para qué sirve cada uno.

| Plataforma | Tipo | Qué hace en el proyecto |
|---|---|---|
| ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black) | Nube | Corre el backend FastAPI como servicio Docker: el monitor que revisa los proyectos y la API que expone el estado y las insignias. |
| ![Oracle DB](https://img.shields.io/badge/Oracle_DB-F80000?style=for-the-badge&logo=oracle&logoColor=white) | Base de datos | Oracle Autonomous Database guarda cada revisión, en un esquema propio (`PORTFOLIO_STATUS`) separado del de cualquier otro proyecto. |
| ![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white) | Nube | Sirve el dashboard React. |
| ![qa-evidencia](https://img.shields.io/badge/qa--evidencia-2EAD33?style=for-the-badge&logo=playwright&logoColor=white) | Pruebas automatizadas | API de resultados (en AWS) que alimenta las insignias de última prueba E2E. |

## 4. Paso a paso

### 4.1 Leer el panel

![Panel de estado de los proyectos](img/manual/01-panel.png)

| Elemento | Qué significa |
|---|---|
| Contador superior | Cuántos proyectos funcionan ahora y hace cuánto fue la última revisión |
| Punto y etiqueta de estado | **Funcionando** (verde), **Lento** o **No responde** (ámbar) |
| Responde en | Cuánto tardó la página en cargar en la última revisión; entre menos, mejor |
| Funcionando esta semana | Porcentaje de revisiones de los últimos 7 días en que respondió bien |
| Barras | Historial reciente, de "hace 7 días" a "ahora". El color es el del proyecto; las barras resaltadas marcan revisiones lentas o fallidas |
| Tarjeta | Al pulsarla abre la demo del proyecto |
| Claro / Oscuro | Cambia el tema |

La página completa, con todas las tarjetas:

![Panel completo](img/manual/02-panel-completo.png)

### 4.2 Usar las insignias

Cada insignia es una imagen SVG que se puede poner en cualquier README:

| Insignia | URL |
|---|---|
| Resumen del portafolio | `https://portafolio-status.onrender.com/api/status/badge.svg` |
| Última corrida E2E del portafolio | `https://portafolio-status.onrender.com/api/status/qa-badge.svg` |
| Estado de un proyecto | `https://portafolio-status.onrender.com/api/status/{slug}/badge.svg` |
| Última prueba E2E de un proyecto | `https://portafolio-status.onrender.com/api/status/{slug}/qa-badge.svg` |

Ejemplo en Markdown:

```markdown
![Estado](https://portafolio-status.onrender.com/api/status/taskflow/badge.svg)
```

### 4.3 Preguntas frecuentes

**¿Por qué un proyecto aparece "Lento" o "No responde" y luego se recupera?** Varios proyectos usan
planes gratuitos que se duermen sin uso; la primera visita los despierta y tarda más.

**¿Puedo agregar mi proyecto?** El monitoreo cubre solo los proyectos de este portafolio
(`backend/app/projects.py`).

**¿Qué significa la pantalla "Estamos en mantenimiento"?** El servicio o su base de datos no están respondiendo en ese momento. No se perdió nada: el historial de disponibilidad siguen guardados, y ninguna acción quedó a medias (si no viste la confirmación, no se guardó). La pantalla se actualiza sola y vuelve a la normalidad apenas el servicio responda; también puedes reintentar más tarde.

## 5. Seguridad: tu información protegida

Tu confianza es lo primero: la plataforma solo pide los datos necesarios para funcionar, los protege y no los comparte con terceros. Esto es lo que se guarda y cómo se protege.

### Qué datos se guardan y dónde

| Dato | Origen | Dónde se guarda | Datos personales |
|---|---|---|---|
| Resultado de cada revisión (código HTTP, milisegundos, fecha) | El monitor del backend | Oracle Autonomous Database | Ninguno |
| Fecha y resultado de las pruebas E2E | Publicados por qa-evidencia | Se consultan, no se guardan aquí | Ninguno |
| Lista de proyectos | `backend/app/projects.py` | Código fuente | Ninguno |

Las visitas al panel no se registran ni usan cookies de seguimiento.

### Cómo se protege tu información

Comprobado en el código del proyecto (`backend/app/main.py`, `config.py`, `database.py`):

- **API de solo lectura:** no expone ninguna ruta que cree, modifique o borre datos; las revisiones
  las hace el propio backend.
- **Sin datos personales:** solo se guardan métricas de disponibilidad de URLs públicas.
- **Conexión a Oracle con Wallet (TLS mutuo):** el wallet viaja como secreto codificado en una
  variable de entorno de Render y se descomprime en un directorio temporal al arrancar; nunca
  está en el repositorio.
- **Secretos en variables de entorno**, nunca en el código.

## 6. Agradecimientos

A mi familia, por su apoyo incondicional, su paciencia y por creer en cada proyecto incluso cuando apenas era una idea. Este trabajo también es de ustedes.

Y a ti, que usas esta plataforma: cada prueba, comentario y sugerencia ayuda a que siga mejorando.
