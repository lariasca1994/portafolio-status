-- ============================================================
-- Portfolio Status — creación del usuario/esquema en Oracle
-- ============================================================
-- Dónde correr esto: Oracle Cloud > tu Autonomous Database > Database Actions > SQL
-- (o SQL Developer, conectado con el usuario ADMIN de esa base).
--
-- Paso 1: conectado como ADMIN, crea el usuario nuevo.
-- Cambia la clave por una tuya (mínimo 12 caracteres, con mayúscula,
-- minúscula, número y símbolo — Oracle la exige así).
-- ============================================================

CREATE USER PORTFOLIO_STATUS IDENTIFIED BY "CAMBIA_ESTA_CLAVE_123!";

GRANT CONNECT, RESOURCE TO PORTFOLIO_STATUS;
GRANT UNLIMITED TABLESPACE TO PORTFOLIO_STATUS;
GRANT CREATE SESSION TO PORTFOLIO_STATUS;

-- ============================================================
-- Paso 2: cierra la sesión de ADMIN y conéctate de nuevo, esta vez
-- como PORTFOLIO_STATUS (con la clave que pusiste arriba). Desde
-- ahí corre lo de abajo — así la tabla queda directamente en su
-- propio esquema, separado del de PRPagos.
-- ============================================================

CREATE TABLE CHECKS_LOG (
    ID           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    PROYECTO     VARCHAR2(80)  NOT NULL,   -- slug del proyecto, ej: 'colombiatech2'
    URL          VARCHAR2(300) NOT NULL,
    STATUS_CODE  NUMBER,                   -- código HTTP que respondió (200, 500, etc.)
    TIEMPO_MS    NUMBER,                   -- cuánto se demoró en responder
    DISPONIBLE   NUMBER(1)     NOT NULL,   -- 1 = respondió bien, 0 = falló
    CHECKED_AT   TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

-- Índice para que las consultas por proyecto + fecha sean rápidas
-- (son las que usa el dashboard para pintar el historial de cada tarjeta).
CREATE INDEX IDX_CHECKS_PROY_FECHA ON CHECKS_LOG (PROYECTO, CHECKED_AT);

-- ============================================================
-- Paso 3 (opcional pero recomendado): borrar chequeos viejos para
-- no llenar el espacio gratis de la base. Esto borra todo lo de
-- hace más de 30 días — puedes correrlo a mano de vez en cuando,
-- o programarlo con un DBMS_SCHEDULER más adelante.
-- ============================================================
-- DELETE FROM CHECKS_LOG WHERE CHECKED_AT < SYSTIMESTAMP - 30;
-- COMMIT;
