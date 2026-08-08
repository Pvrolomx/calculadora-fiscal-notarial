# TICKETS — Calculadora Fiscal Notarial · origen: cotejo expediente Veneros (07-ago-2026)

**Reportado por:** sesión CC (expediente Veneros Salvador) · **Para:** Senior mantenedor
**Origen:** cotejo de `isr.html` contra 4 cálculos independientes del contador **Adán Meza** (Depto. 204, Los Veneros). 2 de 4 escenarios coincidieron dentro de 0.3%; estos dos tickets explican las divergencias de fondo.

---

## 🔴 TICKET 1 — BUG: las mejoras a la construcción NO se deprecian (CRÍTICO)

**Severidad:** alta — subestima el ISR cuando la operación incluye mejoras/ampliaciones.

**Ubicación:** `isr.html`, líneas ~1530-1536.

**Comportamiento actual (bug):**
```js
let mejorasActualizadas = mejoras;
if (mejoras > 0 && fechaMejoras) {
    const inpcMejoras = await getINPCAsync(fechaMejoras);
    const factorMejoras = inpcVenta / inpcMejoras;
    mejorasActualizadas = mejoras * factorMejoras;   // ← solo actualiza por INPC; NO deprecia
}
```

**Por qué está mal:** las inversiones en **construcciones, mejoras y ampliaciones** (Art. 121, fr. II LISR) se tratan como construcción: se **deprecian 3% anual** desde que se terminaron, además de actualizarse por INPC (Art. 124 LISR; RLISR Art. 205 — *"tomando en consideración la antigüedad que el citado avalúo reporte"*). La construcción original SÍ se deprecia en la calc (líneas 1522-1523); las mejoras no. Es una asimetría sin sustento legal.

**Fix propuesto** (replica la lógica de depreciación de la construcción, con la fecha propia de la mejora):
```js
let mejorasActualizadas = mejoras;
if (mejoras > 0 && fechaMejoras) {
    // Depreciación 3%/año desde la terminación de la mejora (Art. 121-II / 124 LISR)
    const dMej = new Date(fechaMejoras);
    let aniosMej = dVenta.getFullYear() - dMej.getFullYear();
    const anivMej = new Date(dVenta.getFullYear(), dMej.getMonth(), dMej.getDate());
    if (dVenta < anivMej) aniosMej--;
    const depMej = Math.min(Math.max(0, aniosMej) * 3, 80) / 100;   // 3%/año, tope 80%
    const inpcMejoras = await getINPCAsync(fechaMejoras);
    const factorMejoras = inpcVenta / inpcMejoras;
    mejorasActualizadas = mejoras * (1 - depMej) * factorMejoras;
}
```

**Caso de validación — Veneros esc. 4 (Exentando + Mejoras):**
- Inputs: mejoras $21,452,588.96, fecha 2021-02-10, venta 2026-08-07 (INPC mejoras 110.907, INPC venta 145.831 en tabla actual).
- Depreciación esperada: 5 años × 3% = **15%**.

| | mejoras actualizadas | ISR total (esc. 4) |
|---|---|---|
| Actual (bug, sin depreciar) | $28,207,890.40 | $1,503,353.10 |
| **Corregido (con depreciación)** | **$23,976,706.84** | **$2,509,610.93** |
| Cotejo Adán Meza (sí deprecia) | $23,860,105.76 | $1,713,669.62 * |

\* La calc corregida y Adán coinciden en depreciar; la diferencia restante entre ambos ($2.5M vs $1.7M) es porque **Adán no prorrateó las mejoras por el % gravable de la exención** y la calc sí lo hace — y ese prorrateo de nuestra calc es el correcto (Art. 93 fr. XIX inciso a: *"considerando las deducciones en la proporción que resulte de dividir el excedente entre el monto de la contraprestación"*). O sea: **con este fix, la calc queda MÁS correcta que el cálculo externo.**

**Nota:** el prorrateo de la exención sobre las deducciones (metodología Nuvigant) ya es correcto y NO debe tocarse. Este ticket es SOLO la depreciación de las mejoras.

---

## 🟡 TICKET 2 — Tablas INPC y UDI congeladas en mayo 2026

**Severidad:** media — impacto < 0.3% en el total, pero afecta fidelidad para fechas de venta jun-2026 en adelante. **Requiere autorización del Arquitecto** (tablas intocables).

**INPC** (`isr.html` ~1046-1048): de `2026-04` a `2026-12` todos están en **145.831** (placeholder repetido). Falta el INPC real publicado por INEGI de may/jun/jul 2026.
- Delta observado: cálculo externo (Adán) usó **145.131** como INPC de venta ~ago-2026 vs. nuestro placeholder **145.831**. Verificar el valor real contra INEGI/DOF y sustituir los meses reales.

**UDI** (`isr.html` ~1244-1245): la tabla `UDIS` llega a `2026-05` = **8.841000**; `getUDI()` cae a fallback 8.841 para fechas posteriores. Faltan jun/jul/ago 2026.
- Delta observado: cálculo externo usó **8.796571**; verificar el valor real ago-2026 contra Banxico SIE (CP150 / SP68257).

**Fuentes:** INEGI (INPC mensual) · Banxico API SIE (UDI, valor del día 10 de cada mes, Art. 124 LISR).

**Impacto en Veneros:** explica las divergencias de 0.18% (esc. 2 "con RFC") y 0.27% (esc. 3 "exentando") entre la calc y Adán. No cambia conclusiones, pero para el follow-up de números al cliente conviene la tabla al día.

---

## Resumen del cotejo (los 4 escenarios)

| Escenario | isr.html (actual) | Adán Meza | Δ | Diagnóstico |
|---|---|---|---|---|
| 1. Sin RFC | $12,375,000 (elige 25%) | $13,261,183 (usó 35%) | −886k | Criterio de opción, no bug: la calc elige la MENOR (óptima) |
| 2. Con RFC | $10,841,788 | $10,860,939 | −0.18% | INPC venta (Ticket 2) |
| 3. Exentando | $9,233,584 | $9,258,434 | −0.27% | INPC venta + UDI (Ticket 2) |
| 4. Exent. + Mejoras | $1,503,353 | $1,713,670 | −12.3% | **Ticket 1** (depreciación mejoras) |

El motor base está validado (esc. 2-3 < 0.3%, consistente con el cotejo previo vs Nuvigant 0.21%). El Ticket 1 es el único hallazgo de fondo.

---

## 🟡 TICKET T-59 — Check de frescura de índices (feature, pedido Rolo 08-ago)

**Objetivo:** que al usar la app se avise si los índices podrían estar desactualizados, sin bloquear ni alterar el cálculo. Requiere **autorización del Arquitecto** para editar `isr.html`.

**Diseño (limpio, no depende de detectar placeholders):** dos constantes de "última verificación contra fuente" que el mantenedor actualiza en cada Hito 3, y un check que compara contra el mes que la operación realmente necesita. Como la tabla INPC tiene meses-placeholder, NO sirve mirar "el último mes de la tabla"; sí sirve una marca explícita de hasta dónde se verificó.

**Código propuesto** (agregar cerca de las constantes de tablas):
```js
// Última verificación contra fuente oficial — ACTUALIZAR en cada Hito 3
const INPC_VERIFICADO_HASTA = '2026-07'; // INEGI
const UDI_VERIFICADO_HASTA  = '2026-05'; // Banxico SIE
```
Función (llamar al final de `calcularISR`, o en el `onchange` de `fechaVenta`):
```js
function checkFrescuraIndices(fechaVenta) {
  const el = document.getElementById('avisoFrescura');
  if (!el || !fechaVenta) return;
  const d = new Date(fechaVenta);
  // INPC usa el mes ANTERIOR a la venta (Art. 124); UDI usa el mes de la venta
  const ant = new Date(d.getFullYear(), d.getMonth() - 1, 1);
  const kINPC = ant.getFullYear() + '-' + String(ant.getMonth() + 1).padStart(2, '0');
  const kUDI  = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
  const av = [];
  if (kINPC > INPC_VERIFICADO_HASTA) av.push('INPC de ' + kINPC + ' (verificado a ' + INPC_VERIFICADO_HASTA + ')');
  if (kUDI  > UDI_VERIFICADO_HASTA)  av.push('UDI de ' + kUDI + ' (verificado a ' + UDI_VERIFICADO_HASTA + ')');
  if (av.length) {
    el.textContent = '⚠️ Índices posiblemente no vigentes: ' + av.join('; ') + '. Verificar contra INEGI/Banxico antes de usar el resultado como definitivo.';
    el.style.display = 'block';
  } else {
    el.style.display = 'none';
  }
}
```
HTML del banner (cerca de los resultados, oculto por default):
```html
<div id="avisoFrescura" style="display:none;background:#fef3c7;border-left:3px solid #d97706;color:#92400e;padding:.6rem .9rem;border-radius:4px;font-size:.85rem;margin:.5rem 0;"></div>
```
Comparación de strings `'YYYY-MM'` es lexicográfica y funciona directo. **No toca ninguna cifra** — solo muestra/oculta un aviso.

**Mantenimiento:** en cada Hito 3, al actualizar la tabla INPC/UDI, subir también `INPC_VERIFICADO_HASTA` / `UDI_VERIFICADO_HASTA`. Así el aviso se apaga solo cuando los datos están al día.

**Caso de prueba:** con `UDI_VERIFICADO_HASTA='2026-05'` y fecha de venta 07/08/2026 → debe mostrar el aviso de UDI (ago-2026 > may-2026). Con fecha ≤ may-2026 → sin aviso.

### Pasos de aplicación (para el mantenedor)

1. **Constantes:** pegar las dos `const … VERIFICADO_HASTA` junto a `VALOR_UDI` / `EXENCION_UDIS` (~línea 1106). **Antes de fijar los valores iniciales, verificar cuál es el último mes REAL** (no placeholder) en `INPC` y `UDIS`. Hoy: la tabla `INPC` trae 2026-06 y 2026-07 en 145.131 — confirmar contra INEGI si jul-2026 es real o repite a jun; poner la marca en el último mes efectivamente verificado. `UDIS` llega a 2026-05 (8.841) → `UDI_VERIFICADO_HASTA='2026-05'`.
2. **Función `checkFrescuraIndices`:** pegarla cerca de `getUDI` / `getINPC` (~líneas 1248-1288).
3. **Banner:** pegar el `<div id="avisoFrescura">` dentro del bloque de resultados (cerca de `#resultados`), oculto por default.
4. **Llamada:** al final de `calcularISR`, después de pintar los resultados (~línea 1704), agregar `checkFrescuraIndices(fechaVenta);` (usa la variable `fechaVenta` ya parseada en la función).
5. **Validar — OBLIGATORIO:**
   - Correr el **golden set de 7 casos** (`FISCALIZACION_golden_set.md`) → deben seguir dando 7/7 al centavo. El check NO toca cifras; si alguna se movió, hay un error de integración.
   - Probar el aviso: fecha de venta 07/08/2026 → banner de UDI visible; fecha ≤ 05/2026 → sin banner.
6. **Commit** citando T-59 y actualizar su fila en `MANTENIMIENTO.md` a CERRADO.
7. **Mantenimiento continuo:** en cada Hito 3, al actualizar `INPC`/`UDIS`, subir también las dos marcas `…_VERIFICADO_HASTA`. Ese es el mecanismo que apaga el aviso cuando los datos quedan al día.

**Alcance:** feature no-bloqueante, cero cambios al motor. No requiere tocar tablas (salvo, aparte, el pendiente de actualizar la UDI a ago-2026, que es el T-10 / Hito 3).
