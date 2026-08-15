# FISCALIZACIÓN — Golden set de regresión · Calculadora ISR

**Propósito:** validar el motor de `isr.html` después de cada cambio, corriéndolo contra un conjunto de casos con **resultado esperado verificado contra fuente independiente** (no contra la propia app). Correr esto ANTES y DESPUÉS de tocar el motor o las tablas.

**Última corrida:** 14-ago-2026 → **7/7 casos coinciden al centavo.** Motor validado; fix de depreciación de mejoras (T1) correcto; INPC jul-2026 actualizado a valor REAL INEGI **145.169** (antes estimado 145.131) — esperados recalculados.

---

## Cómo correr (repetible)

1. Servir la app localmente (evita snapshot estático; los `/api` fallan pero `usarTablaLocal` está activo por default):
   ```
   node -e "const http=require('http'),fs=require('fs'),path=require('path');const root=process.cwd();http.createServer((q,r)=>{let u=q.url.split('?')[0];if(u==='/')u='/isr.html';fs.readFile(path.join(root,u),(e,d)=>e?(r.writeHead(404),r.end()):r.end(d))}).listen(8899)"
   ```
   (correr dentro de `calculadora-fiscal-notarial/`)
2. Abrir `http://localhost:8899/isr.html` en un navegador con consola / o vía browser MCP.
3. Pegar el snippet de `FISCALIZACION_golden_set.json` → para cada caso: setear inputs, `await calcularISR(true)`, leer `resIsrTotal` (residente) o `resMejorOpcion` (extranjero), comparar contra `esperado`.
4. Un caso PASA si `|obtenido − esperado| < $1`.

> **Los `esperado` dependen del INPC de venta vigente.** Si se actualiza la tabla INPC/UDI, recalcular los esperados (el oráculo de referencia está reproducido en el motor validado, ver más abajo). En la corrida del 14-ago se usó INPC venta (jul-2026) = **145.169** (REAL INEGI, antes estimado 145.131), INPC compra (oct-2010) = 73.9689, INPC mejoras (feb-2021) = 110.907, UDI = 8.841.

---

## Los 7 casos (esperados verificados)

| # | Caso | Qué prueba | Esperado (INPC 145.169) | Estado 14-ago |
|---|---|---|---|---|
| 1 | Extranjero sin RFC | Art. 160: elige la MENOR (25% s/bruto) | $12,375,000.00 | ✅ |
| 2 | Residente con RFC | tarifa Art. 152, sin exención | $10,859,795.79 | ✅ |
| 3 | Exentando | prorrateo exención (Art. 93 fr. XIX) | $9,249,339.89 | ✅ |
| 4 | **Exent. + mejoras** | **fix T1: deprecia (Art.124) + prorratea** | $2,552,083.75 | ✅ |
| 5 | Con RFC + mejoras | mejoras sin exención | $3,077,855.75 | ✅ |
| 6 | Exención total (borde) | precio < 700k UDIS → todo exento | $0.00 | ✅ |
| 7 | Mejoras sin fecha (borde) | regresión: no rompe sin fecha (nominal) | $9,159,795.79 | ✅ |

Inputs completos de cada caso en `FISCALIZACION_golden_set.json`.

---

## Fundamento de los esperados (por qué son los correctos)

Verificado por: debate adversarial multiagente + contraste con CX (Codex) + cotejo contra Nuvigant y contador externo (Adán Meza) + lectura directa de fuente. Puntos clave:
- **Mejoras SÍ se deprecian** 3%/año desde su terminación (Art. 124 fr. II LISR: "las mejoras o adaptaciones que implican inversiones deducibles deberán sujetarse al mismo tratamiento") + actualización INPC.
- **Todas las deducciones se prorratean** por el % gravable bajo exención parcial (Art. 93 fr. XIX inciso a: "las deducciones en la proporción que resulte de dividir el excedente entre el monto de la contraprestación").
- **Sin RFC:** la app elige la opción menor entre 25% s/bruto y 35% s/ganancia (Art. 160). *(Nota jurídica: el 35% con deducciones puede ser el óptimo real y no requiere representante en escritura pública — ver expediente Veneros; la app hoy elige la menor entre 25/35, no computa el 35% con mejoras deducibles. Revisar si se quiere afinar.)*

---

## Pendientes de tabla (T2, requieren autorización del Arquitecto)
- **UDI:** la tabla `UDIS` llega a 2026-05 (8.841); `getUDI` cae a fallback para jun/jul/ago 2026. Actualizar contra Banxico SIE. Afecta la exención en centésimas.
- INPC: jun-2026 = 145.131 y jul-2026 = 145.169 son valores REALES INEGI; ago-dic arrastran 145.169 (estimado) hasta publicación. Verificar contra INEGI al cierre de cada mes.
