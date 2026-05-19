# MANTENIMIENTO — Calculadora Fiscal Notarial

**Producto:** `calculadora-fiscal.expatadvisormx.com`
**Repositorio:** `Pvrolomx/calculadora-fiscal-notarial`
**Versión protocolo:** v1.0 (18/05/2026)
**Mantenedor responsable:** Senior asignado · Autorización de edición de tablas embebidas: El Arquitecto

---

## 🎯 Propósito

Esta calculadora depende de datos fiscales oficiales que cambian con calendario fiscal mexicano: tablas ISR (Anexo 8 RMF), tabla de actualización Art. 121 (Anexo 9 RMF), INPC mensual (INEGI), UDIs (Banxico), tasas estatales del 5% cedular y, eventualmente, reformas a LISR.

Sin un protocolo de mantenimiento explícito, las tablas embebidas se desactualizan en silencio y la calculadora pierde fidelidad fiscal sin que nadie lo note hasta que alguien audita contra DOF.

Este documento define **qué revisar, cuándo, contra qué fuente, y quién** para mantener la calculadora alineada con la regulación vigente.

---

## ⚠️ Regla fundamental

> Las tablas embebidas (`INPC`, `UDIS`, `TABLA_ISR_2020`, `TABLA_ISR_2023`, `TABLA_ISR_2026`, etc.) son **intocables sin autorización explícita del Arquitecto**.
>
> Este protocolo **NO autoriza ediciones automáticas**. Define cuándo escalar al Arquitecto con la justificación documentada (delta vs DOF, fuente oficial citada, caso de validación corrido).

El flujo correcto siempre es: detectar desalineación → preparar reporte de auditoría → escalar al Arquitecto → recibir autorización explícita → briefear al Junior con la edición específica → validar contra caso obligatorio → push.

---

## 📅 Los cuatro hitos

### 🟢 HITO 1 — Auditoría de Cierre de Año (1ª semana de enero)

**Disparador:** publicación de la nueva RMF en DOF.
**Fecha histórica de publicación:** 28 de diciembre del año anterior (RMF 2024 → 27-dic-2023, RMF 2025 → 30-dic-2024, RMF 2026 → 28-dic-2025).

**Qué se revisa:**

1. **Nueva tarifa anual ISR (Anexo 8 RMF, sección C.II — Art. 152 LISR)**
   Comparar contra `TABLA_ISR_2026` (y agregar `TABLA_ISR_2027` cuando aplique).
   Fuente: `https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos[AÑO]/rmf/anexos/Anexo-8-RMF-[AÑO]_DOF-[FECHA].pdf`

2. **Lógica de selección `getTablaISR(year)`**
   Agregar el ramal del nuevo año si la tabla anterior dejó de aplicar. Patrón actual:
   ```js
   if (year <= 2022) return TABLA_ISR_2020;
   if (year <= 2025) return TABLA_ISR_2023;
   return TABLA_ISR_2026;
   ```

3. **Tasas estatales del 5% cedular** — revisar si algún estado modificó su tasa (raro, pero ha pasado en Jalisco, Nayarit y Quintana Roo en años anteriores).

4. **Nueva tasa de recargos LIF** — para `isabi.html` si la usa.

**Quién:** Senior detecta y escala → Arquitecto autoriza → Junior edita.

**Tiempo estimado:** 2–3 horas (auditoría + edición + validación).

**Entregable:** commit `fix(isr): alinear TABLA_ISR_[AÑO] con Anexo 8 RMF [AÑO] (DOF [fecha])` o equivalente.

**Referencia histórica:** la primera auditoría formal contra Anexo 8 ocurrió el 18-mayo-2026 — encontró 10/11 tramos desalineados en `TABLA_ISR_2026` (commit `610b987`). El protocolo nace de esa lección: si se hubiera hecho en enero, el error no habría vivido 5 meses.

---

### 🟡 HITO 2 — Auditoría de Cierre Fiscal (abril–mayo)

**Disparador:** publicación del Anexo 9 RMF (Art. 121 LISR — opción de actualización de deducciones).
**Fecha histórica de publicación:** marzo-abril del año en curso. RMF 2025 → 7-abr-2025. El Anexo 9 sale **siempre después** del resto de la RMF porque requiere el INPC consolidado del año anterior.

**Qué se revisa:**

1. **Tabla del Anexo 9 (factor de actualización Art. 121)**
   Si la calculadora usa una tabla embebida para el costo mínimo Art. 121 (10% sobre precio de venta), validar contra el Anexo 9 oficial.
   Fuente: `https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos[AÑO]/rmf/anexos/Anexo9_RMF[AÑO]-DOF-[FECHA].pdf`

2. **Tabla `INPC` embebida — 12 meses del año anterior consolidados**
   Verificar que la tabla `INPC` en `isr.html` tiene los 12 meses completos del año recién cerrado. Fuente primaria: `https://www.inegi.org.mx/temas/inpc/`. Backup Banxico: `https://www.banxico.org.mx/SieInternet/...idCuadro=CP154`.

3. **Caso de validación obligatorio** — re-correr el caso del HO para confirmar que la calculadora sigue dando ~$66,036 (rango $65,500–$66,500) después de las posibles ediciones de los puntos 1 y 2.

4. **Modificaciones RMF acumuladas Q1** — leer las 2-3 primeras versiones modificatorias del año por si tocaron Capítulo 3 (regla 3.15.x — enajenación de inmuebles).
   Fuente: `https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce[AÑO].html`

**Quién:** Senior auditoría. Si hay edición de tabla → escala al Arquitecto.

**Tiempo estimado:** 1–2 horas si no hay cambios; 2–4 horas si hay ediciones.

---

### 🔵 HITO 3 — Monitoreo INPC Mensual (día 11 de cada mes)

**Disparador:** publicación del INPC del mes anterior por INEGI (día 10 hábil del mes siguiente).

**Qué se revisa:**

- Confirmar que la tabla `INPC` embebida en `isr.html` (línea ~737) tiene el último mes publicado.
- Si falta, agregarlo en una sola edición de una línea.

**Quién:** Junior. Es trabajo mecánico.

**Tiempo estimado:** 5–10 minutos.

**Nota de automatización:** este hito es candidato natural para automatización. Un script que descargue el INPC desde INEGI cada día 11 y abra un PR si la tabla está desactualizada eliminaría la fricción humana. Pendiente como T-futuro.

---

### 🔴 HITO 4 — Vigilancia Reactiva (Reforma Fiscal)

**Disparador:** Reforma fiscal en el Congreso. Calendario típico:

- **Septiembre:** Ejecutivo presenta el Paquete Económico
- **Octubre–noviembre:** discusión en Cámara de Diputados y Senado
- **Diciembre:** publicación de la reforma en DOF (si se aprueba)
- **1° de enero del año siguiente:** entrada en vigor

**Qué se revisa cuando ocurra:**

- Cambios estructurales a LISR Arts. 120-126 (enajenación de inmuebles — corazón de la calculadora)
- Cambios a Art. 152 (tarifa anual)
- Cambios a Art. 161 (extranjeros — opción 35% sobre ganancia)
- Cambios a Art. 93 fracción XIX (exención casa habitación)
- Cambios a Art. 121 (costo mínimo 10%)
- Cambios a Art. 158 (extranjeros — opción 25% sobre ingreso)

**Quién:** El Arquitecto decide qué auditar; Senior implementa.

**Tiempo estimado:** variable según magnitud del cambio. Una reforma estructural puede implicar reescribir parcialmente `calcularISR()` — y eso, por regla absoluta, escala automáticamente al Arquitecto.

---

## 📋 Checklist rápido — uso operativo

Cuando arranques un mantenimiento, sigue este orden:

- [ ] Identificar el hito que aplica (1, 2, 3 o 4)
- [ ] Descargar la fuente oficial DOF/SAT/INEGI/Banxico correspondiente
- [ ] Extraer los valores y comparar contra los embebidos en `isr.html`
- [ ] Generar reporte de auditoría con delta, fuente citada, y casos afectados
- [ ] Si hay desalineación → escalar al Arquitecto con el reporte
- [ ] Recibir autorización explícita antes de cualquier edición
- [ ] Briefear al Junior con HO detallado (incluye los valores oficiales completos)
- [ ] Validar contra caso obligatorio post-edición
- [ ] Commit con mensaje que cite la fuente DOF y fecha
- [ ] Reportar al Arquitecto como documento (SHA, diff, validación, conteos de preservación)

---

## 🗂️ Fuentes oficiales — referencia rápida

| Recurso | URL canónica |
|---|---|
| Portal SAT — Normatividad RMF/RGCE | `https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce[AÑO].html` |
| RMF anual (PDF) | `.../documentos[AÑO]/rmf/rmf/RMF_[AÑO]-DOF-[FECHA].pdf` |
| Anexo 8 (Tarifas ISR) | `.../documentos[AÑO]/rmf/anexos/Anexo-8-RMF-[AÑO]_DOF-[FECHA].pdf` |
| Anexo 9 (Tabla Art. 121) | `.../documentos[AÑO]/rmf/anexos/Anexo9_RMF[AÑO]-DOF-[FECHA].pdf` |
| INPC INEGI (tema completo) | `https://www.inegi.org.mx/temas/inpc/` |
| INPC INEGI (serie mensual descargable) | `https://www.inegi.org.mx/app/indicesdeprecios/Estructura.aspx?idEstructura=112001700030` |
| INPC Banxico SIE (backup) | `https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=8&accion=consultarCuadro&idCuadro=CP154` |
| DOF (búsqueda de publicaciones) | `https://dof.gob.mx/` |

---

## 🧪 Caso de validación obligatorio

Toda edición de tablas o motor **debe validarse contra este caso** antes del push:

| Campo | Valor |
|---|---|
| Fecha adquisición | 26/07/2022 |
| Precio adquisición | $3,485,000 |
| Fecha enajenación | 15/05/2026 |
| Precio enajenación | $5,087,500 |
| % Terreno/Construcción | 20/80 |
| Comisión | $814,000 |
| Enajenantes | 2 |
| Estado | Jalisco |
| Casa habitación | ✅ |
| Aplica exención | ❌ |

**ISR esperado:** ~$66,036.04 — **rango aceptable:** $65,500–$66,500.

**Validación correcta:** motor JS en browser (Playwright headless o manual). El archivo `test_isr.py` del repo **NO es el árbitro** — es un aproximado independiente que puede divergir del motor real.

**Fuera de rango → NO push → escalar al Senior o al Arquitecto según corresponda.**

---

## 📓 Bitácora de mantenimientos

Cada mantenimiento ejecutado deja registro aquí (en orden cronológico inverso, más reciente arriba):

| Fecha | Hito | Edición | Commit | Responsable |
|---|---|---|---|---|
| 19-may-2026 | Hito retroactivo | Reemplazo total `const UDIS` — 373 valores canónicos Banxico API SP68257/CP150, may-1995→may-2026, 6 decimales; corrige 2021-04 (6.772368→6.773632) | `f4b0ab7` | CD04 Senior + CD05 Junior |
| 18-may-2026 | Hito retroactivo | `const UDIS` histórico 2020-2023 — 48 valores canónicos día 10, Banxico SIE CP150 vía ikiwi | `cae8314` | CD04 Senior + CD05 Junior |
| 18-may-2026 | Hito retroactivo | Corrección `const UDIS` — valores canónicos Banxico SIE CP150 2024-2026 (fix bug crítico exención Art. 93-XIX LISR inflada ~16×) | `e587f21` | CD03 Supervisor + CD04 Senior |
| 18-may-2026 | Hito 1 (retroactivo) | Corrección `TABLA_ISR_2026` — 10/11 tramos alineados con Anexo 8 RMF 2026 (DOF 28-dic-2025) | `610b987` | CD03 Senior + Junior |

---

## 🔲 Tareas pendientes

| ID | Tarea | Disparador |
|---|---|---|
| T-10 | Actualización mensual `const UDIS` — valores 2026 (jun en adelante) | Día 10 de cada mes; Banxico API SP68257 |
| T-11 | Verificar endpoint `/api/inpc` en producción (posible bug 404 igual que `/api/udi`) | Próxima sesión |
| T-12 | Rebuild de endpoints `/api/udi` y `/api/inpc` en backend Vercel | Decisión del Arquitecto |

---

## 🔄 Evolución de este protocolo

Este documento es **versión v1.0** y nació de la auditoría del 18-mayo-2026. Patrones a observar en los próximos meses:

- ¿Los hitos 1 y 2 funcionan como están definidos, o necesitan ajuste de fechas?
- ¿El Hito 3 mensual se queda como manual o se automatiza?
- ¿Aparece patrón suficiente para escalar al protocolo a nivel ecosistema EA (PoderGen, AdminGen, OfertaGen, etc.) vía `canal/MANTENIMIENTO/CALENDARIO_EA.md`?

Cualquier modificación a este protocolo requiere visto bueno del Arquitecto y se documenta como nueva versión (v1.1, v1.2...) con changelog al pie.

---

*Documento redactado por CD03 Senior · revisado y aprobado por El Arquitecto · 18/05/2026*
*Calculadora Fiscal Notarial · Protocolo de Mantenimiento Anual v1.0*

🐝
