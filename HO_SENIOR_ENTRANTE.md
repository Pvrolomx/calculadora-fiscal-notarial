# HO — BIENVENIDA SENIOR ENTRANTE · CALCULADORA FISCAL
**Para:** Próximo Senior (instancia nueva)
**De:** CD06 Senior (saliente)
**Fecha:** 27/06/2026
**Proyecto:** calculadora-fiscal.expatadvisormx.com
**Metodología:** COLMENA v1.1 — actualizada con CC como ejecutor

---

## 👋 NOTA PARA CD07

Si eres CD07 — ya ejecutaste bajo este proyecto como Junior. Conoces el patrón: anclas exactas, diff completo sin `...`, validación Playwright antes del push, escalación a CD04 cuando toca el motor. Ese criterio ya está en ti.

Este HO te da el contexto completo para operar como **Senior**. El cambio principal es uno solo: **ya no ejecutas tú — CC ejecuta. Tú revisas el diff y das el ✅.**

El ✅ antes del push es tuyo y es inviolable. Bienvenido al otro lado de la mesa. 🐝

---

## 🎯 TU ROL

Eres el nuevo Senior de la Calculadora Fiscal. La cadena de mando es:

**El Arquitecto (Rolo) → CD04 Supervisor → Senior (tú) → CC (ejecutor)**

Claude Code reemplaza al Junior humano para ejecución. Tú te concentras en criterio, revisión de diffs y el ✅. El ✅ antes del push es tuyo y es inviolable — sea quien sea el ejecutor.

**Lo que NO cambia con CC:**
- Motor fiscal (`calcularISR()`) y tablas embebidas → requieren autorización CD04 antes de que CC toque esa zona
- El diff completo llega a ti antes del push — sin `...`, sin abreviaciones
- Verificación independiente tuya tras el push (git fetch + grep en origin)
- Cierre en `MANTENIMIENTO.md` con criterio fiscal documentado

---

## 📦 REPOSITORIO

| Campo | Valor |
|---|---|
| GitHub | https://github.com/Pvrolomx/calculadora-fiscal-notarial |
| PAT | Solicítalo a Rolo — rotar periódicamente |
| Rama | `main` → deploy automático a Vercel |
| URL live | https://calculadora-fiscal.expatadvisormx.com |
| PROHIBIDO | Cualquier rama distinta a `main` |

---

## 🏗️ ESTADO ACTUAL DEL PROYECTO (27/06/2026)

| Archivo | Estado | Notas |
|---|---|---|
| `isr.html` | ✅ Motor calibrado | 88 IDs, 7 funciones motor, 373 UDIS |
| `calcpro.html` | ✅ Funcional | ISTP JAL integrado, paste habilitado |
| `index.html` | ✅ Portada 2 tarjetas | ISR + ISABI, logo pendiente |
| `api/tc.js` | ✅ Endpoint TC vivo | Banxico FIX SF43718 |
| `isabi.html` | ✅ Viva | Solo accesible por URL directa |
| `iva.html` | ⛔ | No tocar bajo ninguna circunstancia |

**Último SHA en producción:** `b050247`

---

## ⚙️ REGLAS ABSOLUTAS

1. **NUNCA tocar `calcularISR()` sin autorización CD04** — aunque CC lo pida, aunque parezca trivial
2. **NUNCA tocar tablas embebidas sin autorización CD04** — INPC, UDIS, TABLA_ISR_*
3. **NUNCA pushear sin ✅ tuyo explícito** — ni CC, ni nadie
4. **SIEMPRE diff completo antes del ✅** — sin `...`
5. **SIEMPRE verificación independiente post-push** — git fetch + grep en origin
6. **SIEMPRE cerrar en MANTENIMIENTO.md** con criterio fiscal si aplica

---

## 🤖 PROTOCOLO CC COMO EJECUTOR

### Prompt estándar para cada sesión CC

```
Tienes permiso para ejecutar sin pedirme autorización:
- git clone, git fetch, git pull, git diff, git log, git status
- grep, cat, find, wc — cualquier comando de solo lectura
- node --version, node --check
- Verificar disponibilidad de Playwright y browsers instalados
- Localizar módulos npm globales y locales
- Ejecutar scripts de validación con Playwright/Node
- git add, git commit, git push — SOLO después de recibir mi ✅ explícito

Antes de modificar cualquier archivo: detente y muéstrame el diff.
Antes de hacer push: espera mi ✅ explícito.
```

### Ciclo estándar con CC

1. Rolo o tú identifican la tarea
2. Si toca motor → escalar a CD04 primero
3. Tú armas el HO para CC con anclas exactas y validaciones
4. CC aplica, valida, reporta diff + resultados
5. Tú revisas — ✅ o corrección
6. CC pushea
7. Tú verificas en origin
8. Cierras MANTENIMIENTO.md

### Lo que CC hace bien vs. lo que sigue siendo tuyo

| CC | Senior (tú) |
|---|---|
| Aplicar str_replace | Revisar el diff |
| Correr Playwright | Interpretar los resultados |
| Contar ocurrencias | Verificar que no haya referencias colgantes |
| Push | Dar el ✅ |
| Renombrar variables | Decidir si el criterio fiscal es correcto |

---

## 🧪 CASO DE VALIDACIÓN OBLIGATORIO

Cada vez que CC toque `isr.html`, valida este caso:

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
| Tipo enajenante | Nacional |
| Casa habitación | ✅ |
| Aplica exención | ❌ |

**ISR esperado: $25,275.35**

⚠️ Este valor fue recalibrado en T-24. El $66,034.06 anterior estaba calibrado con un bug de doble división de comisión ya corregido.

---

## 🔑 IDs CLAVE DEL FORMULARIO

| Campo | ID |
|---|---|
| Fecha adquisición | `fechaCompra` |
| Precio adquisición | `precioCompra` (money — blur) |
| Fecha enajenación | `fechaVenta` |
| Precio enajenación | `precioVenta` (money — blur) |
| % Terreno | `pctTerreno` |
| % Construcción | `pctConstruccion` |
| Comisión | `comision` (money — blur) |
| Fecha comisión | `fechaComision` |
| Enajenantes | `numEnajenantes` |
| Estado | `entidadFederativa` (select, "jalisco" minúsculas) |
| Tipo enajenante | `tipoEnajenante` (select: nacional/residente/extranjero) |
| Casa habitación | `esCasaHabitacion` (checkbox) |
| Aplica exención | `aplicaExencion` (checkbox) |
| Num. exentan | `numExentan` |
| Gastos adquisición | `.gastos-adq-row .gasto-monto` (dinámico) |
| Mejoras | `mejoras` (money — blur) |
| Fecha mejoras | `fechaMejoras` |
| ISR final | `resIsrFinal` |
| Factor INPC | `resFactor` |
| Total deducciones | `resTotalDeduc` |
| Utilidad | `resUtilidad` |
| ISR federal | `resIsrFed` |

---

## 🏛️ ESTADO DEL MOTOR

- **88 IDs** en `isr.html`
- **7 funciones motor:** `calcularISR`, `getTablaISR`, `getINPC`, `getUDI`, `getUDIAsync`, `getINPCAsync`, `calcularISRTablas`
- **373 claves UDIS** (1995–2026)
- **`TABLA_ISR_2026`** alineada Anexo 8 RMF 2026
- **Endpoint live:** `/api/tc` → Banxico FIX SF43718, token en env var `BANXICO_TOKEN`
- **Dropdown tipo enajenante:** Nacional / Residente con RFC / Extranjero sin RFC
- **Dos bloques de deducciones:** gastos adquisición (dinámico, 4 conceptos Art.121-III) + mejoras (campo simple con fecha propia)

---

## ⚖️ CRITERIO FISCAL ACUMULADO (no repetir debates cerrados)

| Tema | Criterio | Base legal | Tarea |
|---|---|---|---|
| Comisión — factor INPC | Mes **anterior** a la enajenación | Art. 121 último párrafo — Fr. III y IV | T-47 |
| ISTP/ISABI de adquisición | **Deducible** para el enajenante | Art. 121-III "impuestos por escrituras de adquisición" | T-46 |
| ISTP/ISABI de la venta actual | **NO deducible** para el enajenante (lo paga el comprador) | — | T-46 |
| Exención casa habitación | Solo residentes fiscales — **no** extranjeros sin RFC | Art. 93-XIX LISR | T-42/T-44 |
| Avalúo de adquisición | Deducible — **perito autorizado**, no bancario | Art. 121-III | T-46 |
| Honorarios notario | Deducibles **sin IVA** | Art. 121-III | T-43 |
| Predial | **NO deducible** | No está en Art. 121 | Consulta sesión |
| Pérdida fiscal anterior | Deducible en 10 años, solo vs. ganancias inmobiliarias | Art. 122 | No implementado |
| Factor INPC — precisión | Motor usa precisión completa JS (~1.186119...) vs. notarios que truncan a 4 decimales (1.1861) | Decisión Arquitecto: mantener precisión completa | H-06/T-33 |
| Pérdida vs. exención | Mensajes distintos — pérdida ≠ exención | `hayExencionCompleta = pctGravable === 0` | T-45 |

---

## 📋 HALLAZGOS PENDIENTES (auditoría CC — 27/06/2026)

Estos hallazgos fueron identificados por CC en auditoría de `isr.html` y `calcpro.html`. No están corregidos:

| # | Hallazgo | Severidad | Estado |
|---|---|---|---|
| #4 | `resGastos` muestra solo mejoras, omite gastos adquisición (T-46 introdujo el split pero no actualizó el display) | 🔴 Alta | Pendiente T-48 |
| #5 | Costo mínimo 10% — filas terreno/construcción no cuadran con el total cuando aplica | 🟠 Media | Pendiente |
| #8 | `VALOR_UDI` fallback desfasado (8.465213 no coincide con tabla) | 🟡 Menor | Pendiente |
| #9 | INPC 2026 aplanado (145.831 para todos los meses futuros) — sin marcar como estimado | 🟡 Menor | Pendiente INEGI ~24-jul |
| #16 | CalcPro `.fiscal-btn:hover` color azul residual (paleta anterior a T-36) | 🟢 Cosmético | Pendiente |
| #17 | CalcPro `rgba(201,162,39,...)` dorado hardcodeado mezclado con `--accent` verde | 🟢 Cosmético | Pendiente |
| #11 | Meta tags PWA corruptos en `isr.html` (comillas rotas, typos) | 🟢 Cosmético | Pendiente |

**Hallazgos descartados o resueltos:**
- #1/#10 — `entidadFederativa` decorativo en cálculo: correcto para práctica EA
- #2 — desglose utilidad anual con múltiples enajenantes: presentación, no afecta ISR
- #3 — INPC comisión: **resuelto en T-47**
- #6 — etiqueta PDF "por enajenante": menor, pendiente revisión futura
- #14 — Nacional y Residente idénticos en cálculo: diseño intencional

---

## 📊 ÁRBITROS EXTERNOS DISPONIBLES

| Caso | Motor externo | ISR esperado | Notas |
|---|---|---|---|
| V Marina DP 707 — residente sin comisión | PDF Adán Meza + Nuviogant | $107,109.49 | Factor 1.1861 (truncado) — delta ~$11 por convención de redondeo |
| Castro — extranjero sin RFC | PDF Notarial Castro | $213,528 | Opción 35% s/ganancia |
| Caso canónico | Motor interno | $25,275.35 | Residente, casa habitación, sin exención |

---

## 📋 HISTORIAL RECIENTE RELEVANTE

| SHA | Tarea | Descripción |
|---|---|---|
| `f909d57` | T-24 | Fix doble división comisión — ancla del canónico $25,275.35 |
| `4379883` | T-28 | Endpoint `/api/tc` Banxico |
| `651b050` | T-42 | Dropdown tipo enajenante (Nacional/Residente/Extranjero) |
| `2a00106` | T-44 | Fix esExtranjero para Residente con RFC |
| `7bd443a` | T-45 | Pérdida vs. exención completa — mensajes distintos |
| `9dbe34e` | T-46 | Dos bloques deducciones — gastos adquisición + mejoras |
| `9e32cf0` | T-47 | Fix INPC comisión mes anterior (Art.121-IV) — primer ciclo CC |

---

## 🎓 LECCIONES APRENDIDAS — PÁSALAS A CC

1. **Un valor esperado puede heredar un bug.** El $66,034 estaba calibrado con el bug de comisión. Ancla a fuentes externas.
2. **"Imposible por diseño" es donde se esconden los bugs.** Pruébalo siempre.
3. **"Simple" no significa "sin verificar".** Una línea puede cambiar el signo del factor INPC en todos los cálculos futuros.
4. **El `...` en un diff es donde se esconde el cambio accidental.** Exige siempre el diff completo.
5. **El árbitro de comportamiento es distinto al árbitro de no-regresión.** Que el canónico no cambie no demuestra que el fix hizo lo que dice — necesitas un caso donde el fix SÍ deba producir diferencia.
6. **Primero criterio fiscal, después diseño de UI.** No al revés.
7. **Verifica las premisas del HO antes de aplicar.** CD04 puede estar equivocado — T-46 lo demostró con el ISTP/ISABI.

---

## 🗣️ VOCABULARIO

| Código | Significado |
|---|---|
| HO | Handoff entre duendes |
| EA | Expat Advisor MX |
| GH | GitHub |
| VC | Vercel |
| CC | Claude Code — ejecutor |
| Senior (tú) | Revisas, apruebas, cierras |
| Supervisor | CD04 — autoriza tocar motor |
| El Arquitecto | Rolo — última palabra en todo |

---

## ✅ TU PRIMER PASO

1. Lee este documento completo
2. Haz `git clone https://github.com/Pvrolomx/calculadora-fiscal-notarial.git`
3. Confirma: 88 IDs, 7 funciones motor, 373 UDIS, SHA `b050247` en tope
4. Lee `MANTENIMIENTO.md` — es la memoria viva del proyecto
5. Reporta al Arquitecto que estás listo

Bienvenido a La Colmena. 🐝

---

*HO redactado por CD06 Senior · 27/06/2026*
*Metodología COLMENA v1.1 · Rolo dirige · CD04 escala · Senior revisa · CC ejecuta*
