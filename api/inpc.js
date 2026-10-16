export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 's-maxage=1800, stale-while-revalidate');

    try {
        const token = process.env.BANXICO_TOKEN;
        if (!token) throw new Error('BANXICO_TOKEN no configurado');

        const year  = parseInt(req.query.year, 10);
        const month = parseInt(req.query.month, 10);
        if (!Number.isInteger(year) || !Number.isInteger(month) || month < 1 || month > 12) {
            throw new Error('Parametros invalidos: year=' + req.query.year + ' month=' + req.query.month);
        }

        // SERIE: SP1 = INPC general (base 2da quincena julio 2018 = 100) en Banxico SIE.
        // (Mismo BANXICO_TOKEN que /api/tc y /api/udi.)
        // CONFIRMAR EN PROD por cotejo: /api/inpc?year=2026&month=7 debe dar 145.169
        // (= INPC['2026-07'] de la tabla embebida). Si no coincide al centavo, la serie
        // es otra -> cambiar 'SP1' aqui. Mientras tanto, success:false hace que el
        // frontend caiga a la tabla local, sin romper el calculo.
        //
        // INPC es MENSUAL: se pide la ventana del mes completo (01..28) y se toma el
        // PRIMER dato. NO se usa /datos/oportuno (daria el ultimo mes publicado, no el
        // mes pedido). Si el mes aun no esta publicado, Banxico no devuelve dato ->
        // success:false -> fallback a tabla.
        const mm    = String(month).padStart(2, '0');
        const desde = year + '-' + mm + '-01';
        const hasta = year + '-' + mm + '-28';
        const url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SP1/datos/'
                  + desde + '/' + hasta;

        const response = await fetch(url, {
            headers: { 'Bmx-Token': token, 'Accept': 'application/json' }
        });

        if (!response.ok) throw new Error('Banxico API error: ' + response.status);

        const data = await response.json();
        const dato = data.bmx?.series?.[0]?.datos?.[0];

        if (dato?.dato) {
            const valor = parseFloat(String(dato.dato).replace(/,/g, ''));
            if (!Number.isFinite(valor) || valor <= 0) {
                throw new Error('Dato no numerico de Banxico: ' + dato.dato);
            }
            return res.status(200).json({
                success: true,
                valor: valor,
                fecha: dato.fecha,
                fuente: 'Banxico SIE',
                serie: 'SP1'
            });
        }
        throw new Error('Sin datos de Banxico para ' + desde + '..' + hasta);

    } catch (error) {
        // Mismo patron que /api/tc y /api/udi: 200 con success:false para que el cliente
        // caiga al fallback de la tabla local sin tratarlo como error de red.
        return res.status(200).json({
            success: false,
            valor: null,
            fuente: 'error',
            error: error.message
        });
    }
}
