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

        // CRITERIO DIA 10 (Art. 124 LISR) — el mismo que documenta la tabla UDIS de isr.html.
        // Se pide la ventana 10→14 y se toma el PRIMER dato disponible: si el 10 cae en
        // sabado/domingo o inhabil y Banxico no publica ese dia, devuelve el siguiente dia
        // publicado, replicando la regla "sab/dom → lunes siguiente" de la tabla local.
        // NO se usa /datos/oportuno: eso da el ultimo dato disponible, no el del mes pedido.
        const mm    = String(month).padStart(2, '0');
        const desde = year + '-' + mm + '-10';
        const hasta = year + '-' + mm + '-14';
        const url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SP68257/datos/'
                  + desde + '/' + hasta;

        const response = await fetch(url, {
            headers: { 'Bmx-Token': token, 'Accept': 'application/json' }
        });

        if (!response.ok) throw new Error('Banxico API error: ' + response.status);

        const data = await response.json();
        const dato = data.bmx?.series?.[0]?.datos?.[0];

        if (dato?.dato) {
            const valor = parseFloat(dato.dato);
            if (!Number.isFinite(valor) || valor <= 0) {
                throw new Error('Dato no numerico de Banxico: ' + dato.dato);
            }
            return res.status(200).json({
                success: true,
                valor: valor,
                fecha: dato.fecha,
                fuente: 'Banxico UDI',
                serie: 'SP68257'
            });
        }
        throw new Error('Sin datos de Banxico para ' + desde + '..' + hasta);

    } catch (error) {
        // Mismo patron que /api/tc: responder 200 con success:false para que el cliente
        // caiga al fallback local sin tratarlo como error de red y sin romper el calculo.
        return res.status(200).json({
            success: false,
            valor: null,
            fuente: 'error',
            error: error.message
        });
    }
}
