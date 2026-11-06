// Nombre visible de cada proyecto en el tablero. La API (backend) mantiene su propio
// nombre y slug; aquí solo cambia lo que se muestra: cada portal se presenta con un
// nombre que describe lo que hace la aplicación.
const NOMBRES: Record<string, string> = {
  colombiatech2: "Alquiler de vivienda",
  prpagos: "Simulador de pagos",
  "reservas-corferias": "Reservas de recinto ferial",
  "gestor-incidentes-ti": "Gestor de incidentes TI",
  "gestor-casos-qa": "Gestor de casos de prueba QA",
  taskflow: "Gestor de tareas",
  "calidad-afiliaciones": "Calidad de afiliaciones",
  "verificador-api": "Verificador de APIs",
  "motor-horarios-oci": "Coordinador de reuniones",
  qalabspbvi: "Laboratorio de pagos inmediatos",
  syspulse: "Monitoreo e incidentes TI",
  exponexo: "Plataforma de ferias y eventos",
  "lottery-ai": "Analítica y pronósticos de sorteos",
};

export function nombreVisible(slug: string, nombreApi: string): string {
  return NOMBRES[slug] ?? nombreApi;
}
