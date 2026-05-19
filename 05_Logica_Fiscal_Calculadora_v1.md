# 05 — Lógica Fiscal · Calculadora ISR Enajenación de Inmuebles

**Producto:** `calculadora-fiscal.expatadvisormx.com`
**Archivo motor:** `isr.html`
**Versión documento:** v1.0 (18/05/2026)
**Propósito:** Documentar en prosa fiscal la lógica del motor de cálculo para auditoría conceptual contra LISR, RLISR, CFF y RMF.
**Audiencia:** NotebookLM como auditor; fiscalistas humanos como revisores.

---

## 1. Alcance del cálculo

La calculadora determina el **Impuesto Sobre la Renta** (ISR) que causa una persona física al **enajenar un bien inmueble** ubicado en territorio nacional. Cubre tres tipos de contribuyente:

1. **Residente fiscal en México** — tributa por tarifa Art. 152 con anualización Art. 124.
2. **Residente en el extranjero sin establecimiento permanente** — puede optar entre las tres opciones del Art. 161 LISR (25% sobre ingreso, 35% sobre ganancia con deducciones, o tarifa Art. 152 con representante).
3. **Contribuyente sin RFC** (turista o extranjero no registrado) — restringido a las dos primeras opciones; pierde el acceso a la tarifa Art. 152.

La calculadora también:
- Aplica la **exención por casa habitación** del Art. 93 fracción XIX LISR cuando procede
- Calcula el **costo mínimo del 10%** del Art. 121 LISR cuando las deducciones actualizadas son insuficientes
- Maneja **enajenaciones con múltiples enajenantes** (copropiedad o sociedad conyugal) conforme al Art. 126
- Determina la **distribución del ISR entre la entidad federativa (5%) y la federación** conforme al Art. 127
- Marca el **IVA** cuando se trata de local comercial

---

## 2. Marco normativo de referencia

| Cuerpo legal | Artículos clave usados |
|---|---|
| **LISR** | 9° (residencia), 93-XIX (exención casa habitación), 120-126 (capítulo enajenación), 124 (actualización), 126 (anualización), 127 (5% estatal), 152 (tarifa anual), 158 (25% extranjero), 160-161 (extranjero ganancia) |
| **RLISR** | Reglas sobre proporcionalidad y depreciación de construcción |
| **CFF** | 9° (residencia fiscal), 17-A (actualización por INPC) |
| **RMF vigente** | Regla 3.15.1 (Anexo 9 — factor Art. 121), Regla 3.17.1 (tarifa Anexo 8), Regla 3.15.4 (retención del notario) |

---

## 3. Algoritmo en lenguaje natural

### 3.1 Determinación de años transcurridos

**Insumo:** fecha de adquisición y fecha de enajenación.

El motor calcula **dos variables de años**:

- **`aniosReales`**: años calendario completos por aniversario. Si la enajenación es antes del aniversario en el año, se resta uno. Puede ser 0 si el inmueble se vende antes del primer aniversario.
- **`aniosDep`**: años para depreciar la construcción. Igual a `aniosReales` con tope superior de 20 años y piso de 0.
- **`anios`**: años para dividir la utilidad gravable (Art. 124 LISR). Igual a `aniosReales` con tope superior de 20 años y **piso forzado de 1**, porque dividir entre cero no es admisible y el Art. 124 no permite anualizar a menos de un año.

**Fundamento:**
- Art. 124 LISR — anualización con tope de 20 años
- Topes y piso son lógica defensiva del motor consistente con la doctrina

### 3.2 Obtención del INPC

**Insumo:** dos fechas (compra y venta).

El motor obtiene dos valores del INPC:

- **`inpcVenta`**: INPC del **mes inmediato anterior** a la fecha de enajenación. Esto es lectura literal del Art. 124 LISR que ordena usar "el mes inmediato anterior a aquél en que se efectúe la enajenación".
- **`inpcCompra`**: INPC del mes de la fecha de adquisición.

**Fundamento:**
- Art. 124 LISR — mes inmediato anterior para el numerador del factor
- Art. 17-A CFF — definición del factor de actualización

**Factor de actualización:** `factorINPC = inpcVenta / inpcCompra`

### 3.3 Separación terreno / construcción

**Insumo:** porcentajes terreno/construcción (default 20/80 si no se especifica).

El motor separa el precio de adquisición:

- **`precioTerrenoCompra`** = `precioCompra × pctTerreno`
- **`precioConstruccionCompra`** = `precioCompra × pctConstruccion`

**Fundamento:**
- Art. 123 LISR — el terreno y la construcción se actualizan por separado porque la construcción se deprecia y el terreno no
- El default 20/80 corresponde a la práctica notarial común; ciertos estados o tipos de inmueble pueden requerir un avalúo formal

### 3.4 Actualización del terreno

`terrenoActualizado = precioTerrenoCompra × factorINPC`

**Fundamento:**
- Art. 124 LISR — el terreno se actualiza pero no se deprecia

### 3.5 Depreciación + actualización de la construcción

El motor aplica **3% anual de depreciación con tope del 80%**:

```
pctDepreciacion = min(aniosDep × 3, 80) / 100
construccionDepreciada = precioConstruccionCompra × (1 - pctDepreciacion)
construccionActualizada = construccionDepreciada × factorINPC
```

**Fundamento:**
- Art. 124 LISR — depreciación de la construcción a razón del 3% anual
- Tope del 80% — la construcción nunca puede depreciarse a cero, conserva un valor residual del 20%

### 3.6 Actualización de mejoras (opcional)

Si el usuario ingresa gastos por mejoras y una fecha:

```
inpcMejoras = INPC del mes de las mejoras
factorMejoras = inpcVenta / inpcMejoras
mejorasActualizadas = gastosMejoras × factorMejoras
```

Si no se proporciona fecha, se toman a valor nominal sin actualización.

**Fundamento:**
- Art. 124 LISR — las mejoras se actualizan desde la fecha en que se realizó la inversión
- Comprobante fiscal (factura) es requisito para acreditar el gasto

### 3.7 Actualización de la comisión

La comisión inmobiliaria se actualiza con INPC y se **divide entre el número de enajenantes**:

```
inpcEnajDirecto = INPC del mes de enajenación
inpcComision = INPC del mes en que se pagó la comisión
factorComision = inpcEnajDirecto / inpcComision
comisionActualizada = (comision / numEnajenantes) × factorComision
```

**Fundamento:**
- Art. 121 LISR — la comisión es un gasto deducible (gasto necesario para la enajenación)
- Art. 124 LISR — se actualiza por INPC desde la fecha de pago
- Art. 126 LISR — al haber múltiples enajenantes, cada uno deduce su proporción

### 3.8 Total de deducciones (escenario normal)

`totalDeducciones = terrenoActualizado + construccionActualizada + mejorasActualizadas + comisionActualizada`

### 3.9 Costo mínimo del 10% (Art. 121 LISR)

Si la suma de **terreno actualizado + construcción actualizada** es menor al **10% del precio de venta**, el motor sustituye esos dos componentes por el costo mínimo:

```
costoMinimo = precioVenta × 0.10
usaCostoMinimo = (terrenoActualizado + construccionActualizada) < costoMinimo
si usaCostoMinimo:
    totalDeducciones = costoMinimo + mejorasActualizadas + comisionActualizada
```

**Fundamento:**
- Art. 121 LISR — establece la opción del costo mínimo cuando las deducciones son menores al 10% del precio de venta
- La regla 3.15.1 RMF y su Anexo 9 desarrollan el procedimiento

**Punto de auditoría:** Verificar que el motor aplique el costo mínimo solo cuando es benéfico al contribuyente (siempre que terreno+construcción actualizados < 10% precio venta).

### 3.10 Exención por casa habitación (Art. 93-XIX LISR)

Aplica únicamente si:
- El enajenante es **residente fiscal en México** (no extranjero)
- El inmueble es **casa habitación**
- El contribuyente **opta por aplicar la exención**
- Hay **uno o más enajenantes que califican** para exentar

**Cálculo del monto exento:**

```
exencionTotal = 700,000 UDIs × valor UDI a fecha de venta × numExentan
```

**Donde:**
- **700,000 UDIs** es el umbral del Art. 93-XIX LISR
- El **valor de la UDI** a la fecha de venta lo determina Banxico
- **`numExentan`** = cantidad de enajenantes que aplican la exención (uno por inmueble en su vida cada 3 años, salvo excepciones)

**Aplicación al cálculo (metodología Nuvigant):**

```
si precioVenta > exencionTotal:
    pctGravable = (precioVenta − exencionTotal) / precioVenta
    precioGravable = precioVenta × pctGravable
    deduccionesGravables = totalDeducciones × pctGravable
si precioVenta ≤ exencionTotal:
    todo exento → ISR = 0
```

**Fundamento:**
- Art. 93 fracción XIX inciso a) LISR — exención de casa habitación hasta 700,000 UDIs
- Aplicación proporcional sobre precio y deducciones — criterio Nuvigant que evita sobre-deducción cuando hay exención parcial
- Resolución Miscelánea — regla 3.11.x (años) sobre frecuencia de la exención

**Punto crítico para auditoría:** la exención **no aplica a extranjeros**. El motor lo bloquea explícitamente con la condición `!esExtranjero`. Esto es consistente con la doctrina pero conviene confirmarlo.

### 3.11 Caso de enajenantes mixtos (Art. 93 LISR)

Si la calculadora detecta que algunos enajenantes aplican exención y otros no (`numExentan > 0 && numExentan < numEnajenantes`), abre un **modal de decisión** y pausa el cálculo. Esto es defensivo: el caso mixto requiere intervención del usuario para definir cómo proceder (con o sin exención agregada).

**Fundamento:**
- Art. 93 fracción XIX LISR — la exención es individual por enajenante
- Art. 126 LISR — cálculo por enajenante

### 3.12 Utilidad gravable

`utilidadGravable = precioGravable − deduccionesGravables`

Si el resultado es ≤ 0, se marca **pérdida fiscal** y el ISR base es 0 (sin perjuicio del cálculo del 25% sobre ingreso para extranjeros, ver siguiente sección).

**Fundamento:**
- Arts. 121-124 LISR — determinación de la ganancia

### 3.13 Cálculo del ISR — residente

**Por enajenante (Art. 126 LISR):**

```
utilidadPorEnajenante = utilidadGravable / numEnajenantes
utilidadAnual = utilidadPorEnajenante / anios
isrAnual = aplicar tarifa Art. 152 a utilidadAnual
isrPorEnajenante = isrAnual × anios
isrTotal = isrPorEnajenante × numEnajenantes
```

**Fundamento:**
- Art. 124 LISR — anualización dividiendo entre años
- Art. 126 LISR — cálculo por cada enajenante
- Art. 152 LISR — tarifa progresiva anual (publicada en Anexo 8 RMF cada año)

**Selección de tarifa Art. 152:** el motor usa `getTablaISR(fechaVenta)` que selecciona:
- Hasta 2022: `TABLA_ISR_2020`
- 2023-2025: `TABLA_ISR_2023`
- 2026 en adelante: `TABLA_ISR_2026` (alineada con Anexo 8 RMF 2026 desde 18-may-2026)

### 3.14 Distribución entre estado y federación

**Por enajenante (Art. 127 LISR):**

```
isrEstadoPorEnajenante = min(utilidadPorEnajenante × 0.05, isrPorEnajenante)
isrEstado = isrEstadoPorEnajenante × numEnajenantes
isrFederacion = isrTotal − isrEstado
```

**Fundamento:**
- Art. 127 LISR — pago provisional del 5% al estado de la entidad federativa donde se ubica el inmueble
- El `min()` con `isrPorEnajenante` evita que el estado se lleve más del ISR causado (cuando la utilidad es muy pequeña y el 5% supera el ISR base)

### 3.15 Cálculo del ISR — extranjero

El extranjero tiene **tres opciones** (Art. 161 LISR) y el motor elige automáticamente la menor:

| Opción | Fórmula | Cuándo aplica |
|---|---|---|
| **A — 25% sobre ingreso** | `isr25 = precioVenta × 0.25` | Sin deducciones; aplicable sin representante |
| **B — 35% sobre ganancia** | `isr35 = utilidadGravable × 0.35` | Con deducciones actualizadas |
| **C — Tarifa Art. 152** | `isrTablas = calcularISRTablas(utilidadAnual) × anios` | Solo si tiene representante legal y RFC |

**Restricciones del motor:**
- Si el extranjero está marcado como **sin RFC**, la opción C se excluye del comparativo (solo compara A vs B)
- Si hay **pérdida fiscal** (utilidad ≤ 0):
  - Opción A: el 25% se calcula igual sobre el ingreso (puede generar ISR aún con pérdida)
  - Opción B: cae a 0 (no hay ganancia que gravar)
  - El motor elige Opción B (= 0) como la mejor cuando hay pérdida

**Distribución estado/federación:** para extranjeros, **todo el ISR va a la federación**, nada al estado.

**Fundamento:**
- Art. 158 LISR — 25% sobre ingreso para no residentes
- Art. 161 LISR — opción del 35% sobre ganancia para no residentes con representante
- Art. 161 LISR — opción de tarifa Art. 152 para no residentes con representante y RFC

**Punto crítico para auditoría:** el motor asume que la presencia de RFC habilita la opción C. Conviene verificar si el SAT exige adicionalmente que el representante esté formalmente designado y si el RFC debe ser provisional o definitivo.

### 3.16 IVA (Art. 9 LIVA)

Si el inmueble es **local comercial**, el motor calcula:

`iva = precioVenta × 0.16`

**Fundamento:**
- Art. 9 fracción II LIVA — la enajenación de construcciones destinadas a casa habitación está exenta; las que NO son casa habitación (locales comerciales, oficinas, etc.) sí causan IVA al 16%
- El motor lo reporta como información, no como parte del ISR

---

## 4. Tablas embebidas — fuentes de verdad

| Tabla | Ubicación en `isr.html` | Fuente oficial | Última auditoría |
|---|---|---|---|
| `INPC` | Línea ~793 | INEGI — `https://www.inegi.org.mx/temas/inpc/` | Mensual (Hito 3) |
| `UDIS` | Línea ~950 | Banxico SIE CP150 | Por verificar |
| `TABLA_ISR_2020` | Línea ~892 | Anexo 8 RMF años aplicables | Por verificar |
| `TABLA_ISR_2023` | Línea ~907 | Anexo 8 RMF años aplicables | Por verificar |
| `TABLA_ISR_2026` | Línea ~922 | Anexo 8 RMF 2026 (DOF 28-dic-2025) | ✅ 18-may-2026 — commit `610b987` |

**Protocolo de mantenimiento:** ver `MANTENIMIENTO.md` en la raíz del repo. Cuatro hitos anuales con responsables y fuentes.

---

## 5. Puntos abiertos para auditoría conceptual

Estas son las preguntas que NotebookLM debería poder responder con las fuentes oficiales cargadas. Si encuentra una respuesta que contradiga la implementación, escalar al Senior:

1. **Mes anterior para INPC venta** — ¿el motor usa correctamente el **mes inmediato anterior** según Art. 124 LISR? El motor lo hace vía `getINPCAsync(fechaVenta, true)` donde el flag `true` activa "mes anterior". Verificar fidelidad.

2. **Depreciación 3% / 80% tope** — ¿el Art. 124 LISR o el RLISR especifican exactamente este patrón, o hay régimenes diferentes para distintos tipos de construcción (habitacional vs comercial)?

3. **División de comisión entre enajenantes** — ¿el Art. 126 LISR ordena dividir la comisión entre enajenantes, o cada enajenante puede deducir el 100% de la comisión que él pagó?

4. **Metodología Nuvigant para exención parcial** — ¿la aplicación proporcional sobre precio y deducciones está respaldada por norma, criterio SAT o solo doctrina/práctica?

5. **Tarifa Art. 152 para extranjeros** — ¿requiere solo RFC y representante, o hay requisitos adicionales (constancia de residencia del país de origen, tratado de doble tributación aplicable, etc.)?

6. **Costo mínimo y mejoras** — cuando se activa el costo mínimo del 10%, las mejoras y comisión siguen sumándose. ¿Esto es correcto o el 10% es exhaustivo de las deducciones?

7. **Pérdida fiscal del extranjero** — ¿la opción 35% en cero está literal en Art. 161 o es interpretación del motor?

8. **IVA en local comercial** — ¿hay supuestos donde un local comercial pueda estar exento (uso mixto con residencia, antigüedad, etc.) que el motor no considere?

9. **Frecuencia de exención casa habitación** — el motor no valida la regla de "una vez cada 3 años" (Art. 93-XIX). ¿Debería?

10. **Conversión USD → MXN** — el motor ofrece convertidor con tipo de cambio Banxico. ¿La fecha del tipo de cambio debe ser la del hecho generador (firma de escritura) o la de pago?

---

## 6. Cómo usar este documento en NotebookLM

**Preguntas tipo que rinden bien con esta fuente cargada:**

- *"¿La lógica de actualización por INPC en la sección 3.2 cumple con el Art. 124 LISR según las fuentes oficiales?"*
- *"¿La depreciación del 3% anual con tope del 80% (sección 3.5) está respaldada por norma vigente?"*
- *"¿Hay algún supuesto del Art. 93-XIX que el algoritmo de la sección 3.10 no esté considerando?"*
- *"¿La fórmula del costo mínimo del 10% (sección 3.9) interpreta correctamente el Art. 121 LISR?"*
- *"¿Es válida la opción de tarifa Art. 152 para extranjero con RFC (sección 3.15) o el Art. 161 exige más requisitos?"*

**Preguntas que NO deben hacerse a NotebookLM:**

- *"¿Cuánto ISR pago en X caso?"* — NotebookLM no ejecuta cálculos. Eso lo resuelve la calculadora en browser.
- *"¿Mi caso particular cumple con la exención?"* — eso requiere análisis fiscal individual, no auditoría conceptual del motor.

---

## 7. Limitaciones documentadas

Esta calculadora **NO cubre**:

- Enajenaciones de **inmuebles afectos a actividad empresarial** (esos van por Capítulo II, no por Capítulo IV)
- **Adjudicación judicial** (régimen distinto)
- **Permuta** (régimen del Art. 14 CFF aplicado a dos enajenaciones simultáneas)
- **Donación** (puede ser ingreso por adquisición, otro capítulo)
- **Herencia y legado** (exento — Art. 93 fracción XXII)
- **Fideicomiso traslativo** (esquema distinto)
- **Régimen de incorporación fiscal** o **RESICO** aplicado a inmuebles de actividad

Para esos casos, la calculadora no es el instrumento correcto y debe redirigirse a un fiscalista.

---

## 8. Bitácora de versiones

| Versión | Fecha | Cambios | Autor |
|---|---|---|---|
| v1.0 | 18/05/2026 | Documento inicial — refleja motor al commit `d6a13b0` | CD03 Senior |

---

*Documento redactado por CD03 Senior · Calculadora Fiscal Notarial · 18/05/2026*
*Fuente: lectura directa de `isr.html` en repo `Pvrolomx/calculadora-fiscal-notarial`*

🐝
