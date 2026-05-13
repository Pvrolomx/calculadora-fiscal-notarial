#!/usr/bin/env python3
"""
=============================================================
TEST HARNESS — Calculadora ISR Enajenación
Replica la lógica EXACTA de calculadora-fiscal.expatadvisormx.com
=============================================================
CÓMO AGREGAR CASOS:
  Agrega un dict a la lista CASOS al final del archivo.
  Campos obligatorios: fecha_venta, fecha_compra, precio_venta, precio_compra
  Campos opcionales: pct_terreno (def 20), mejoras, fecha_mejoras,
                     comision, extranjero, casa_habitacion, num_enajenantes,
                     num_exentan, local_comercial, descripcion
=============================================================
"""

from datetime import date, datetime
from typing import Optional

# ============================================================
# TABLA INPC (Base 2da quincena julio 2018 = 100) — igual que la app
# ============================================================
INPC = {
    '2018-01': 98.795,  '2018-02': 99.1714, '2018-03': 99.4922, '2018-04': 99.1548,
    '2018-05': 98.9941, '2018-06': 99.3765, '2018-07': 99.909,  '2018-08': 100.492,
    '2018-09': 100.917, '2018-10': 101.44,  '2018-11': 102.303, '2018-12': 103.02,
    '2019-01': 103.108, '2019-02': 103.079, '2019-03': 103.476, '2019-04': 103.531,
    '2019-05': 103.233, '2019-06': 103.299, '2019-07': 103.687, '2019-08': 103.67,
    '2019-09': 103.942, '2019-10': 104.503, '2019-11': 105.346, '2019-12': 105.934,
    '2020-01': 106.447, '2020-02': 106.889, '2020-03': 106.838, '2020-04': 105.755,
    '2020-05': 106.162, '2020-06': 106.743, '2020-07': 107.444, '2020-08': 107.867,
    '2020-09': 108.114, '2020-10': 108.774, '2020-11': 108.856, '2020-12': 109.271,
    '2021-01': 110.21,  '2021-02': 110.907, '2021-03': 111.824, '2021-04': 112.19,
    '2021-05': 112.419, '2021-06': 113.018, '2021-07': 113.682, '2021-08': 113.899,
    '2021-09': 114.601, '2021-10': 115.561, '2021-11': 116.884, '2021-12': 117.308,
    '2022-01': 118.002, '2022-02': 118.981, '2022-03': 120.159, '2022-04': 120.809,
    '2022-05': 121.022, '2022-06': 122.044, '2022-07': 122.948, '2022-08': 123.803,
    '2022-09': 124.571, '2022-10': 125.276, '2022-11': 125.997, '2022-12': 126.478,
    '2023-01': 127.336, '2023-02': 128.046, '2023-03': 128.389, '2023-04': 128.363,
    '2023-05': 128.084, '2023-06': 128.214, '2023-07': 128.832, '2023-08': 129.545,
    '2023-09': 130.12,  '2023-10': 130.609, '2023-11': 131.445, '2023-12': 132.373,
    '2024-01': 133.555, '2024-02': 133.681, '2024-03': 134.065, '2024-04': 134.336,
    '2024-05': 134.087, '2024-06': 134.594, '2024-07': 136.003, '2024-08': 136.013,
    '2024-09': 136.08,  '2024-10': 136.828, '2024-11': 137.424, '2024-12': 137.949,
    '2025-01': 138.343, '2025-02': 138.726, '2025-03': 139.161, '2025-04': 139.62,
    '2025-05': 140.012, '2025-06': 140.405, '2025-07': 140.78,  '2025-08': 140.867,
    '2025-09': 141.197, '2025-10': 141.708, '2025-11': 142.645, '2025-12': 143.042,
    # 2026 — INPC publicado por INEGI (fuente: inegi.org.mx)
    '2026-01': 144.243, '2026-02': 144.628, '2026-03': 145.071, '2026-04': 145.831,
    '2026-05': 145.831, '2026-06': 145.831, '2026-07': 145.831, '2026-08': 145.831,
    '2026-09': 145.831, '2026-10': 145.831, '2026-11': 145.831, '2026-12': 145.831,
}

# ============================================================
# TABLA UDIs
# ============================================================
UDIS = {
    '2024-12': 8.465213, '2025-01': 8.497, '2025-02': 8.529, '2025-03': 8.561,
    '2025-04': 8.594, '2025-05': 8.627, '2025-06': 8.661, '2025-07': 8.695,
    '2025-08': 8.730, '2025-09': 8.765, '2025-10': 8.800, '2025-11': 8.836,
    '2025-12': 8.872, '2026-01': 8.908, '2026-02': 8.945, '2026-03': 8.982,
    '2026-04': 9.020, '2026-05': 9.058, '2026-06': 9.096, '2026-07': 9.135,
}
EXENCION_UDIS = 700_000

# ============================================================
# TABLAS ISR (idénticas a la app)
# ============================================================
TABLA_ISR_2020 = [
    (0.01,       6942.20,    0.00,     1.92),
    (6942.21,    58922.16,   133.28,   6.40),
    (58922.17,   103550.44,  3460.01,  10.88),
    (103550.45,  120372.83,  8315.57,  16.00),
    (120372.84,  144119.23,  11007.14, 17.92),
    (144119.24,  290667.75,  15262.49, 21.36),
    (290667.76,  458132.29,  46565.26, 23.52),
    (458132.30,  874650.00,  85952.92, 30.00),
    (874650.01,  1166200.00, 210908.23,32.00),
    (1166200.01, 3498600.00, 304204.21,34.00),
    (3498600.01, float('inf'),1097220.21,35.00),
]
TABLA_ISR_2023 = [
    (0.01,       8952.49,    0,        1.92),
    (8952.50,    75984.55,   171.88,   6.40),
    (75984.56,   133536.07,  4461.94,  10.88),
    (133536.08,  155229.80,  10723.55, 16.00),
    (155229.81,  185852.57,  14194.54, 17.92),
    (185852.58,  374837.88,  19682.13, 21.36),
    (374837.89,  590795.99,  60049.40, 23.52),
    (590796.00,  1127926.84, 110842.74,30.00),
    (1127926.85, 1503902.46, 271981.99,32.00),
    (1503902.47, 4511707.37, 392294.17,34.00),
    (4511707.38, float('inf'),1414947.85,35.00),
]
TABLA_ISR_2026 = [
    (0.01,       10135.11,   0,        1.92),
    (10135.12,   86015.21,   194.59,   6.40),
    (86015.22,   151171.32,  5050.95,  10.88),
    (151171.33,  175729.53,  12138.78, 16.00),
    (175729.54,  210394.93,  16068.10, 17.92),
    (210394.94,  424319.74,  22280.25, 21.36),
    (424319.75,  668859.54,  67949.21, 23.52),
    (668859.55,  1276729.11, 125458.11,30.00),
    (1276729.12, 1702305.47, 307819.18,32.00),
    (1702305.48, 5106916.42, 443998.60,34.00),
    (5106916.43, float('inf'),1601546.35,35.00),
]

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def get_inpc(fecha_str: str, mes_anterior: bool = False) -> float:
    """Replica getINPCAsync — devuelve INPC del mes (o mes anterior per Art.124)"""
    d = datetime.strptime(fecha_str, '%Y-%m-%d')
    if mes_anterior:
        # Mes anterior al de la venta
        m = d.month - 1
        y = d.year
        if m == 0:
            m = 12
            y -= 1
        key = f'{y}-{m:02d}'
    else:
        key = f'{d.year}-{d.month:02d}'
    # Fallback a dic 2025 si no existe (igual que la app con 2024-12)
    return INPC.get(key, INPC.get('2025-12', 143.042))

def get_udi(fecha_str: str) -> float:
    d = datetime.strptime(fecha_str, '%Y-%m-%d')
    key = f'{d.year}-{d.month:02d}'
    return UDIS.get(key, UDIS.get('2026-05', 9.058))

def get_tabla_isr(fecha_venta: str):
    year = datetime.strptime(fecha_venta, '%Y-%m-%d').year
    if year <= 2022: return TABLA_ISR_2020
    if year <= 2025: return TABLA_ISR_2023
    return TABLA_ISR_2026

def calcular_isr_tablas(utilidad_anual: float, fecha_venta: str) -> float:
    """Replica calcularISRTablas"""
    if utilidad_anual <= 0:
        return 0.0
    tabla = get_tabla_isr(fecha_venta)
    for (li, ls, cuota, tasa) in tabla:
        if li <= utilidad_anual <= ls:
            return cuota + (utilidad_anual - li) * (tasa / 100)
    return 0.0

def calcular_anios_reales(fecha_venta: str, fecha_compra: str) -> int:
    """Años reales transcurridos por aniversario — SIN forzar mínimo 1.
    Usado para depreciación: si < 1 año real = 0% depreciación."""
    dv = datetime.strptime(fecha_venta, '%Y-%m-%d')
    dc = datetime.strptime(fecha_compra, '%Y-%m-%d')
    anios = dv.year - dc.year
    aniversario = datetime(dv.year, dc.month, dc.day)
    if dv < aniversario:
        anios -= 1
    return max(0, min(anios, 20))

def calcular_anios(fecha_venta: str, fecha_compra: str) -> int:
    """Años para dividir utilidad Art.124 — mínimo 1, máximo 20."""
    return max(1, calcular_anios_reales(fecha_venta, fecha_compra))

# ============================================================
# FUNCIÓN PRINCIPAL DE CÁLCULO
# ============================================================
def calcular(caso: dict) -> dict:
    fv = caso['fecha_venta']
    fc = caso['fecha_compra']
    precio_venta  = caso['precio_venta']
    precio_compra = caso['precio_compra']
    pct_terreno   = caso.get('pct_terreno', 20) / 100
    pct_constr    = 1 - pct_terreno
    mejoras       = caso.get('mejoras', 0)
    fecha_mejoras = caso.get('fecha_mejoras', '')
    comision       = caso.get('comision', 0)
    fecha_comision = caso.get('fecha_comision', fv)  # default = fecha enajenación
    extranjero     = caso.get('extranjero', False)
    casa_hab      = caso.get('casa_habitacion', False)
    aplica_ex     = caso.get('aplica_exencion', False)
    num_enaj      = caso.get('num_enajenantes', 1)
    num_exentan   = caso.get('num_exentan', 0)
    local_com     = caso.get('local_comercial', False)

    anios        = calcular_anios(fv, fc)         # para dividir utilidad (min 1)
    anios_dep    = calcular_anios_reales(fv, fc)  # para depreciación (puede ser 0)

    # INPC — Art.124: mes ANTERIOR a la venta
    inpc_venta  = get_inpc(fv, mes_anterior=True)
    inpc_compra = get_inpc(fc)
    factor_inpc = inpc_venta / inpc_compra

    # Costo adquisición desglosado
    terreno_compra = precio_compra * pct_terreno
    constr_compra  = precio_compra * pct_constr

    # Terreno: solo actualización
    terreno_act = terreno_compra * factor_inpc

    # Construcción: depreciación 3%/año máx 80% + actualización
    # Usa años REALES (sin forzar mínimo 1) — si < 1 año = 0% depreciación
    pct_dep = min(anios_dep * 3, 80) / 100
    constr_dep = constr_compra * (1 - pct_dep)
    constr_act = constr_dep * factor_inpc

    # Mejoras actualizadas
    mejoras_act = mejoras
    if mejoras > 0 and fecha_mejoras:
        inpc_mej = get_inpc(fecha_mejoras)
        factor_mej = inpc_venta / inpc_mej
        mejoras_act = mejoras * factor_mej

    # Comisión actualizada con INPC desde su fecha de pago hasta mes enajenación
    # Usa INPC del mes de enajenación (no mes anterior) — Art.121 LISR
    inpc_enaj_directo = get_inpc(fv, mes_anterior=False)
    comision_act = comision
    if comision > 0:
        inpc_com = get_inpc(fecha_comision, mes_anterior=False)
        factor_com = inpc_enaj_directo / inpc_com
        comision_act = comision * factor_com

    # Total deducciones
    total_ded = terreno_act + constr_act + mejoras_act + comision_act

    # Costo mínimo 10% Art.121 LISR
    costo_min = precio_venta * 0.10
    usa_costo_min = (terreno_act + constr_act) < costo_min
    if usa_costo_min:
        total_ded = costo_min + mejoras_act + comision_act

    # Exención casa habitación — Metodología Nuvigant
    exencion_total = 0
    pct_gravable   = 1.0
    precio_grav    = precio_venta
    deduc_grav     = total_ded

    if aplica_ex and not extranjero and num_exentan > 0:
        udi_venta = get_udi(fv)
        exencion_total = EXENCION_UDIS * udi_venta * num_exentan
        if precio_venta > exencion_total:
            pct_gravable = (precio_venta - exencion_total) / precio_venta
            precio_grav  = precio_venta * pct_gravable
            deduc_grav   = total_ded * pct_gravable
        else:
            pct_gravable = 0
            precio_grav  = 0
            deduc_grav   = 0

    # Utilidad gravable
    utilidad_grav = max(0, precio_grav - deduc_grav)
    hay_perdida   = (precio_grav - deduc_grav) <= 0

    # ---- ISR ----
    isr_total = isr_estado = isr_fed = 0
    isr25 = isr35 = isr_tablas = 0
    mejor_opcion = ''

    if extranjero:
        if hay_perdida:
            isr_total = 0
            mejor_opcion = '35% s/Ganancia (pérdida = $0)'
        else:
            isr25 = precio_venta * 0.25
            isr35 = utilidad_grav * 0.35
            util_anual_ext = utilidad_grav / anios
            isr_anual_ext  = calcular_isr_tablas(util_anual_ext, fv)
            isr_tablas     = isr_anual_ext * anios
            opciones = [
                (isr25,    '25% s/Ingreso'),
                (isr35,    '35% s/Ganancia'),
                (isr_tablas, 'Tablas Art.152'),
            ]
            mejor = min(opciones, key=lambda x: x[0])
            isr_total    = mejor[0]
            mejor_opcion = mejor[1]
            isr_fed   = isr_total
            isr_estado = 0

    elif not hay_perdida:
        util_por_enaj  = utilidad_grav / num_enaj
        util_anual     = util_por_enaj / anios
        isr_anual      = calcular_isr_tablas(util_anual, fv)
        isr_por_enaj   = isr_anual * anios
        isr_total      = isr_por_enaj * num_enaj
        isr_estado_pxe = min(util_por_enaj * 0.05, isr_por_enaj)
        isr_estado     = isr_estado_pxe * num_enaj
        isr_fed        = isr_total - isr_estado

    iva = precio_venta * 0.16 if local_com else 0

    return {
        'anios': anios,
        'anios_dep': anios_dep,
        'inpc_venta':  inpc_venta,
        'inpc_compra': inpc_compra,
        'factor_inpc': factor_inpc,
        'terreno_act': terreno_act,
        'constr_act':  constr_act,
        'mejoras_act': mejoras_act,
        'comision_act': comision_act,
        'total_ded':   total_ded,
        'usa_costo_min': usa_costo_min,
        'exencion':    exencion_total,
        'pct_gravable': pct_gravable,
        'utilidad':    utilidad_grav,
        'hay_perdida': hay_perdida,
        'isr_federal': isr_fed,
        'isr_estado':  isr_estado,
        'isr_total':   isr_total,
        'isr25':       isr25,
        'isr35':       isr35,
        'isr_tablas':  isr_tablas,
        'mejor_opcion': mejor_opcion,
        'iva':         iva,
    }

# ============================================================
# CASOS DE PRUEBA
# ============================================================
CASOS = [
    # --- CASO 01: Los valores de la imagen ---
    {
        'descripcion': 'CASO 01 — Imagen (Jul2022→May2026, $3.48M→$6.47M)',
        'fecha_venta':  '2026-05-12',
        'fecha_compra': '2022-07-26',
        'precio_venta':  6_475_000,
        'precio_compra': 3_484_982.27,
        'pct_terreno': 20,
    },
    # --- CASO 02: Residente, ganancia pequeña, aplica costo mínimo ---
    {
        'descripcion': 'CASO 02 — Costo mínimo 10% Art.121',
        'fecha_venta':  '2025-06-01',
        'fecha_compra': '2015-03-01',
        'precio_venta':  2_000_000,
        'precio_compra':   100_000,  # Muy bajo → activa costo mínimo
        'pct_terreno': 20,
    },
    # --- CASO 03: Residente con casa habitación exenta (1 enajenante) ---
    {
        'descripcion': 'CASO 03 — Casa habitación exenta 1 enajenante',
        'fecha_venta':  '2026-03-01',
        'fecha_compra': '2020-01-01',
        'precio_venta':  5_000_000,
        'precio_compra': 2_500_000,
        'pct_terreno': 30,
        'aplica_exencion': True,
        'num_enajenantes': 1,
        'num_exentan': 1,
    },
    # --- CASO 04: 2 enajenantes, 2 exentan ---
    {
        'descripcion': 'CASO 04 — 2 enajenantes, ambos exentan',
        'fecha_venta':  '2026-04-01',
        'fecha_compra': '2019-06-01',
        'precio_venta':  12_000_000,
        'precio_compra':  4_000_000,
        'pct_terreno': 25,
        'aplica_exencion': True,
        'num_enajenantes': 2,
        'num_exentan': 2,
    },
    # --- CASO 05: Extranjero, Art.160 ---
    {
        'descripcion': 'CASO 05 — Extranjero Art.160 (3 opciones)',
        'fecha_venta':  '2026-02-01',
        'fecha_compra': '2021-08-01',
        'precio_venta':  4_800_000,
        'precio_compra': 3_200_000,
        'pct_terreno': 20,
        'extranjero': True,
    },
    # --- CASO 06: Extranjero con pérdida ---
    {
        'descripcion': 'CASO 06 — Extranjero con pérdida fiscal',
        'fecha_venta':  '2025-11-01',
        'fecha_compra': '2022-01-01',
        'precio_venta':  1_500_000,
        'precio_compra': 2_800_000,
        'pct_terreno': 20,
        'extranjero': True,
    },
    # --- CASO 07: Con mejoras ---
    {
        'descripcion': 'CASO 07 — Con mejoras ($500k, 2023)',
        'fecha_venta':  '2026-05-01',
        'fecha_compra': '2018-09-01',
        'precio_venta':  8_000_000,
        'precio_compra': 3_500_000,
        'pct_terreno': 20,
        'mejoras': 500_000,
        'fecha_mejoras': '2023-03-01',
    },
    # --- CASO 08: Con comisión inmobiliaria ---
    {
        'descripcion': 'CASO 08 — Con comisión inmobiliaria (3%)',
        'fecha_venta':  '2026-01-15',
        'fecha_compra': '2020-05-01',
        'precio_venta':  3_200_000,
        'precio_compra': 1_800_000,
        'pct_terreno': 20,
        'comision': 96_000,  # 3% de $3.2M
    },
    # --- CASO 09: Compra muy antigua (max depreciación) ---
    {
        'descripcion': 'CASO 09 — Compra 2000, máx depreciación 80%',
        'fecha_venta':  '2025-09-01',
        'fecha_compra': '2000-03-01',
        'precio_venta':  6_000_000,
        'precio_compra':   800_000,
        'pct_terreno': 20,
    },
    # --- CASO 10: Local comercial (IVA) ---
    {
        'descripcion': 'CASO 10 — Local comercial con IVA',
        'fecha_venta':  '2026-04-01',
        'fecha_compra': '2019-01-01',
        'precio_venta':  2_500_000,
        'precio_compra': 1_200_000,
        'pct_terreno': 10,
        'local_comercial': True,
    },
]

# ============================================================
# RUNNER
# ============================================================
def fmt(n): return f"${n:>14,.2f}"

def run_all():
    print("=" * 80)
    print("  CALCULADORA FISCAL NOTARIAL — SUITE DE PRUEBAS")
    print(f"  Ejecutado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)

    for i, caso in enumerate(CASOS, 1):
        r = calcular(caso)
        desc = caso.get('descripcion', f'Caso {i}')
        print(f"\n{'─'*80}")
        print(f"  {desc}")
        print(f"{'─'*80}")
        print(f"  Fecha venta/compra : {caso['fecha_venta']} / {caso['fecha_compra']}")
        print(f"  Precio venta       : {fmt(caso['precio_venta'])}")
        print(f"  Precio compra      : {fmt(caso['precio_compra'])}")
        print(f"  Años               : {r['anios']}")
        print(f"  INPC venta/compra  : {r['inpc_venta']:.3f} / {r['inpc_compra']:.3f}")
        print(f"  Factor INPC        : {r['factor_inpc']:.6f}")
        if r['usa_costo_min']:
            print(f"  ⚠️  COSTO MÍNIMO 10% Art.121 activado")
        if r['exencion'] > 0:
            print(f"  Exención c.hab     : {fmt(r['exencion'])}  ({r['pct_gravable']*100:.2f}% gravable)")
        print(f"  Terreno actualiz.  : {fmt(r['terreno_act'])}")
        print(f"  Constr. actualiz.  : {fmt(r['constr_act'])}")
        if r['mejoras_act'] > 0:
            print(f"  Mejoras actualiz.  : {fmt(r['mejoras_act'])}")
        print(f"  Total deducciones  : {fmt(r['total_ded'])}")
        print(f"  ── UTILIDAD        : {fmt(r['utilidad'])}")
        if r['hay_perdida']:
            print(f"  ⚠️  PÉRDIDA FISCAL")
        if caso.get('extranjero'):
            print(f"  Opción 25% ingreso : {fmt(r['isr25'])}")
            print(f"  Opción 35% ganancia: {fmt(r['isr35'])}")
            print(f"  Opción Tablas 152  : {fmt(r['isr_tablas'])}")
            print(f"  ✅ Mejor opción    : {r['mejor_opcion']}")
        print(f"  ISR Federal        : {fmt(r['isr_federal'])}")
        print(f"  ISR Estatal (5%)   : {fmt(r['isr_estado'])}")
        print(f"  ══ ISR TOTAL       : {fmt(r['isr_total'])}")
        if r['iva'] > 0:
            print(f"  IVA (16%)          : {fmt(r['iva'])}")

    print(f"\n{'='*80}")
    print(f"  Total casos: {len(CASOS)}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    run_all()
