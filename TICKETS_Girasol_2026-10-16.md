# TICKETS — Calculadora Fiscal Notarial · origen: expediente Girasol Murphy (16-oct-2026)

**Reportado por:** sesión CC (expediente Girasol Sur 1109-1110) · **Para:** Senior mantenedor
**Autorización:** los tickets 2 y 3 tocan la tabla `INPC` embebida o la lógica del factor → **requieren autorización explícita del Arquitecto** (MANTENIMIENTO.md, regla fundamental).
**Origen:** recálculo del ISR de tres vendedores extranjeros (venta 16-oct-2026, Art. 160 LISR, sin RFC) en `isr.html` en producción. Los hallazgos se verificaron en el navegador contra el sitio desplegado; no se modificó código.

---

## 🔴 TICKET 1 — `/api/inpc` no existe: el INPC nunca se consulta en vivo

**Severidad:** alta — es la causa raíz de que el INPC quede congelado entre actualizaciones manuales de la tabla.

**Hallazgo:** `fetchINPC()` (`isr.html` ~línea 1330) llama a `/api/inpc?year=&month=` y espera `{ success, valor }`. En el repo `api/` solo existen `tc.js` y `udi.js`. En producción, `fetchINPC(2026, 4|8|9)` devuelve `null` → siempre cae a la tabla local. Es el mismo caso que T-56 (`/api/udi` no existía).

**Fix propuesto:** crear `api/inpc.js` replicando el patrón de `api/udi.js`:
- Mismo `BANXICO_TOKEN`, CORS y `Cache-Control`.
- Banxico SIE REST, serie del **INPC general base 2Q-jul-2018 = 100**. ⚠️ **Confirmar la clave de serie antes de codificar** (candidata: `SP1`). Cotejar el valor devuelto contra la tabla embebida, por ejemplo `2026-07` = **145.169**. Si no coincide al centavo, la serie es otra.
- Pedir el dato **mensual** del mes solicitado (`/datos/AAAA-MM-01/AAAA-MM-01`), **no** `/datos/oportuno`.
- Responder `{ success: true, valor, fecha, fuente: 'Banxico SIE', serie }`. Si el mes aún no está publicado, devolver `success: false` para que el frontend caiga a la tabla.

**Validación:**

| Mes | Esperado (Banxico CP154, fuente INEGI, consultado 16-oct-2026) |
|---|---|
| 2026-07 | 145.169 |
| 2026-08 | 145.462 |
| 2026-09 | 146.075 |

Correr la suite y el golden set con el endpoint activo.

---

## 🟡 TICKET 2 — Tabla INPC: agosto y septiembre 2026 siguen en arrastre de julio

**Severidad:** media. Requiere autorización del Arquitecto.

**Hallazgo:** `INPC['2026-08']` e `INPC['2026-09']` = 145.169 (arrastre de julio); `INPC_VERIFICADO_HASTA = '2026-07'`. INEGI ya publicó:
- `'2026-08': 145.462`
- `'2026-09': 146.075`

Fuente: Banxico SIE, cuadro CP154, "Precios al Consumidor (INPC)". El mismo cuadro da julio = 145.169, igual que la tabla actual, lo que confirma la base.

**Fix:** actualizar ambos meses y `INPC_VERIFICADO_HASTA → '2026-09'`; dejar oct-dic en arrastre. Recalcular los `esperado` del golden set que dependan de esos meses (ver la advertencia de MANTENIMIENTO.md sobre T-60).

**Impacto medido (venta 16-oct-2026):** factor de un caso de compra en mar-2016 = 1.6146 (tabla) vs **1.6247** (real); ISR al 35% s/ganancia $147,383.18 vs **$146,930.54**.

---

## 🟡 TICKET 3 — El factor de actualización puede quedar menor a 1

**Severidad:** media — sobreestima el ISR cuando el INPC de venta es menor al de compra (compras recientes).

**Ubicación:** `isr.html` ~línea 1516: `const factorINPC = inpcVenta / inpcCompra;` (sin piso).

**Por qué está mal:** Art. 17-A CFF: cuando el factor de actualización resulte menor a 1, **se considerará 1**.

**Caso que lo disparó:** compra 2026-05-13, venta 2026-10-16. Con la tabla actual, el INPC de venta (sep, arrastre 145.169) quedó por debajo del de compra y dio un factor de **0.9975** (deducciones $232,805.88; ISR 35% $28,539.22). Con piso en 1: deducciones **$233,380.00** e ISR **$28,338.28**.

**Fix:** `const factorINPC = Math.max(1, inpcVenta / inpcCompra);`. Revisar si los factores de mejoras (`factorMejoras`) y de comisión requieren el mismo piso.

---

## 🟡 TICKET 4 — Fechas de compra fuera de la tabla INPC se rellenan en silencio con dic-2025

**Severidad:** media — el resultado puede quedar correcto por casualidad, pero el PDF imprime índices falsos.

**Hallazgo:** la tabla `INPC` empieza en `2000-01`. `getINPC()` y `getINPCAsync()` devuelven `INPC[key] || INPC['2025-12']`. Con compra en **1989-08-05**, la calc usó INPC de compra **143.0420** (dic-2025) y un factor de **1.0149**, y así lo imprimió en el PDF. En ese caso el ISR no cambió porque rigió el costo mínimo del 10% (Art. 121), pero un usuario lee un INPC y un factor sin sentido.

**Fix (cualquiera de dos):**
- (a) Extender la tabla hacia atrás (INEGI publica el INPC base 2018 desde 1969), **o**
- (b) Si la clave no existe: no usar fallback. Mostrar un aviso visible ("INPC de compra no disponible para AAAA-MM") e imprimirlo así en el PDF. Si aplica el costo mínimo del 10%, decirlo explícitamente en lugar del factor.

---

## 🟢 TICKET 5 — PDF: caracteres Unicode que Helvetica de jsPDF no soporta

**Severidad:** baja (cosmética, pero sale en el documento que se entrega).

**Ubicación:** `generarPDF()`:
- `txt('(−) Total deducciones', …)` (~línea 2438) — el signo menos Unicode `−` (U+2212).
- `txt('✅ Mejor opción', …)` (~línea 2459) — emoji.

**Síntoma:** en el PDF salen `(") T o t a l  d e d u c c i o n e s` y `' M e j o r  o p c i ó n` (glifo basura y letras espaciadas, porque jsPDF codifica la cadena como UTF-16).

**Fix:** usar el guion ASCII `(-) Total deducciones` y quitar el emoji (`Mejor opción`). Revisar el resto de `generarPDF()` en busca de otros caracteres fuera de WinAnsi.

**Relacionado (menor):** cuando aplica el costo mínimo del 10%, la pantalla cambia la etiqueta a "Costo mínimo deducible (10% Art.121 LISR)", pero el PDF sigue imprimiendo "Terreno actualizado". Usar la misma etiqueta dinámica en el PDF.

---

### Caso integral de validación (después de los tickets 1-3)

Extranjero sin RFC, 1 enajenante, venta 2026-10-16, compra 2006-03-16 a $253,331.00, venta $2,280,575.25 (USD 123,321 × 18.4930), 20/80 terreno/construcción:
- INPC venta **146.0750** (sep-2026), INPC compra 60.7725, factor **2.4036**.
- Deducciones **$316,636.13**.
- 25% s/ingreso **$570,143.81** ← mejor opción.
- 35% s/ganancia $687,378.69.
