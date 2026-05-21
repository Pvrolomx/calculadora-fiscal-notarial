export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 's-maxage=1800, stale-while-revalidate');

    try {
        const token = process.env.BANXICO_TOKEN;
        if (!token) throw new Error('BANXICO_TOKEN no configurado');

        const url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno';
        const response = await fetch(url, {
            headers: { 'Bmx-Token': token, 'Accept': 'application/json' }
        });

        if (!response.ok) throw new Error('Banxico API error: ' + response.status);

        const data = await response.json();
        const dato = data.bmx?.series?.[0]?.datos?.[0];

        if (dato?.dato) {
            return res.status(200).json({
                tc: parseFloat(dato.dato),
                fecha: dato.fecha,
                fuente: 'Banxico FIX',
                serie: 'SF43718'
            });
        }
        throw new Error('Sin datos de Banxico');

    } catch (error) {
        return res.status(200).json({
            tc: null,
            fuente: 'error',
            error: error.message
        });
    }
}
