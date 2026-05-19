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

## 🔍 Hallazgos de Auditoría Conceptual (NotebookLM)

Esta sección registra hallazgos de la auditoría conceptual del motor contra LISR/RLISR/CFF/RMF realizada vía NotebookLM con el documento `05_Logica_Fiscal_Calculadora_v1.md` y fuentes oficiales cargadas. **Estos hallazgos NO siempre se traducen en ediciones de código** — algunos son notas legales que el Arquitecto usa en asesoría directa con clientes.

### H-01 · Comisión inmobiliaria — deducción 100% por un solo enajenante

**Fecha hallazgo:** 19-may-2026
**Fuente:** Auditoría NotebookLM, punto abierto #3 del documento `05`
**Sección del motor afectada:** 3.7 (actualización y división de comisión)

**Resumen del hallazgo:**

La división de la comisión inmobiliaria entre el número de enajenantes — implementada actualmente en el motor — **no proviene del Art. 126 LISR** como mi documento de lógica fiscal v1 indicaba erróneamente. El fundamento correcto es el **Art. 201 RLISR**, que ordena la división proporcional **únicamente cuando no se puedan identificar las deducciones que corresponden a cada copropietario**.

**Cita literal Art. 201 RLISR:**

> "En el caso de que no pudieran identificarse las deducciones que correspondan a cada copropietario, éstas se harán en forma proporcional a los derechos de copropiedad."

**Implicación práctica:**

Si el comprobante fiscal y el flujo de pago identifican a un solo copropietario como pagador real de la comisión inmobiliaria, **ese enajenante puede deducir el 100% de la comisión** — la división proporcional es subsidiaria, no obligatoria.

**Aplicación en escenarios de exención mixta (caso de oro EA):**

Cuando dos enajenantes venden y uno aplica exención por casa habitación (Art. 93-XIX) y el otro no, asignar el 100% de la comisión al **enajenante no-exentante** reduce su utilidad gravable y por tanto su ISR. El enajenante exentante no se ve afectado (su ISR sigue siendo $0 por la exención). El ahorro puede ser parcial o llegar al **ISR total = $0** cuando la comisión total iguala o supera la utilidad bruta del no-exentante.

**Condición matemática para llegar a ISR = $0:**

```
comisión_total ≥ (precio_venta / 2) − (costo_actualizado / 2)
```

O dicho más simple: comisión total ≥ utilidad bruta de un enajenante.

**Decisión del Arquitecto (19-may-2026):**

**Calculadora NO se modifica.** El motor mantiene división proporcional como default (postura conservadora SAT-friendly). La asesoría sobre esta optimización se hace **manualmente por El Arquitecto** en el cálculo cliente por cliente cuando aplique.

**Acción operativa para El Arquitecto:**

Cuando un cliente presente caso de **dos enajenantes con exención mixta**:
1. Correr la calculadora con la configuración estándar (división proporcional)
2. Verificar si la comisión, asignada 100% al no-exentante, mata su ISR
3. Calcular manualmente el escenario con asignación concentrada
4. Asesorar al cliente para que la factura se emita a nombre del no-exentante y el flujo de pago sea consistente
5. Conservar comprobantes para defender la deducción concentrada ante SAT

**Requisitos documentales para defender la deducción concentrada:**

- Factura CFDI de la comisión emitida exclusivamente a nombre del enajenante pagador
- Comprobante de pago bancario que muestre el flujo desde la cuenta del enajenante pagador
- Consistencia del nombre en cláusula del contrato de servicios inmobiliarios
- Planeación pre-cierre (no se puede retro-aplicar después de la operación)

**Cuándo NO usar esta estrategia:**

- Cuando ambos enajenantes exentan: irrelevante (ambos ISR = 0 sin importar comisión)
- Cuando ninguno exenta: la optimización es marginal (~5-15% ahorro), evaluar caso a caso
- Cuando la factura ya fue emitida a nombre de ambos: no se puede modificar retroactivamente

**Tareas pendientes derivadas:**

- ~~T-13~~ Modificación del motor para soportar asignación manual de deducciones por enajenante — **descartada** por decisión del Arquitecto (19-may-2026)
- T-14 (futura) Actualización de `05_Logica_Fiscal_Calculadora_v1.md` a v1.1 con cita correcta Art. 201 RLISR

### H-02 · Restricción temporal de 3 años para exención casa habitación

**Fecha hallazgo:** 19-may-2026
**Fuente:** Auditoría NotebookLM adicional A-01 (derivada del punto abierto #9 del documento `05`)
**Sección del motor afectada:** 3.10 (exención casa habitación Art. 93-XIX LISR)

**Resumen del hallazgo:**

El Art. 93 fracción XIX inciso a) LISR establece literalmente que la exención de casa habitación **solo aplica si el contribuyente no enajenó otra casa habitación con exención en los 3 años inmediatos anteriores**. El motor calcula la exención sin validar esta restricción, lo cual puede generar cálculos optimistas que el notario o el SAT después rechacen.

**Cita literal Art. 93 fracción XIX inciso a) LISR:**

> "La exención prevista en este inciso será aplicable siempre que durante los tres años inmediatos anteriores a la fecha de enajenación de que se trate el contribuyente no hubiere enajenado otra casa habitación por la que hubiera obtenido la exención prevista en este inciso."

**Hallazgos sub-derivados de NotebookLM:**

1. **Cero excepciones al plazo.** No hay supuestos de fuerza mayor, divorcio, ni traslado laboral que liberen al contribuyente. Postura conservadora respaldada por ausencia de excepción normativa.

2. **El notario tiene obligación legal de consultar al SAT.** El Art. 93 LISR ordena al fedatario verificar en el portal SAT y dejar constancia en la escritura. Si no consulta, asume responsabilidad solidaria.

3. **Discrepancia ley vs RMF.** El Art. 93 LISR dice "cinco años" (residuo histórico). La regla 3.11.4 RMF armoniza a "tres años" para fines operativos del notario. La regla operativa correcta es 3 años.

4. **Doble vía de acreditación.** El contribuyente manifiesta bajo protesta + el notario consulta el portal SAT + se imprime el resultado en la escritura. Las dos vías deben cumplirse.

5. **Sanción por aplicación indebida (Art. 21 + Art. 76 CFF):** ISR omitido + actualización + recargos sobre total + **multa del 55% al 75% de las contribuciones omitidas**. En operaciones típicas, la sanción total puede llegar a 2-3x el ISR que se intentó evitar.

**Decisión del Arquitecto (19-may-2026):**

**Opción D — Documentación H-02 + warning visual al motor.** La calculadora se modifica para agregar un warning informativo (no bloqueante) que aparezca cuando el usuario active la exención. El cálculo no cambia. El warning educa al usuario y blinda legalmente a EA.

**Acción operativa para El Arquitecto:**

Cuando un cliente presente caso de **exención por casa habitación**:
1. Preguntar directamente: "¿Ha vendido otra casa habitación con exención en los últimos 3 años?"
2. Si la respuesta es sí o ambigua → la exención NO aplica, recalcular sin exención
3. Si la respuesta es no → asesorar para que la manifestación bajo protesta esté correctamente preparada antes del cierre notarial
4. Coordinar con el notario para asegurar que la consulta SAT se haga y conste en escritura
5. Documentar todo en el expediente del cliente

**Tareas pendientes derivadas:**

- T-15 Modificación motor — agregar warning visual no-bloqueante al activar exención (mini-HO para Senior)
- T-16 Actualizar `05_Logica_Fiscal_Calculadora_v1.md` a v1.1 — agregar referencia a H-02 en sección 3.10 y en limitaciones §7

---

## 🔲 Tareas pendientes

| ID | Tarea | Disparador |
|---|---|---|
| T-10 | Actualización mensual `const UDIS` — valores 2026 (jun en adelante) | Día 10 de cada mes; Banxico API SP68257 |
| T-11 | Verificar endpoint `/api/inpc` en producción (posible bug 404 igual que `/api/udi`) | Próxima sesión |
| T-12 | Rebuild de endpoints `/api/udi` y `/api/inpc` en backend Vercel | Decisión del Arquitecto |
| T-14 | Actualizar `05_Logica_Fiscal_Calculadora_v1.md` a v1.1 — corregir cita Art. 126→Art. 201 RLISR en sección 3.7; agregar nota del hallazgo H-01 | Próxima sesión de auditoría NotebookLM |
| T-15 | Agregar warning visual no-bloqueante de 3 años en modal de exención casa habitación | HO al Senior, prioridad alta |
| T-16 | Actualizar `05_Logica_Fiscal_Calculadora_v1.md` a v1.1 — agregar H-02 en sección 3.10 y limitaciones §7 | Próxima sesión de auditoría NotebookLM |

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
