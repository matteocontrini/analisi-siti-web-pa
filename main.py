import dns.resolver
import requests
import whois

domains = [
    'www.governo.it',
    'www.mise.gov.it',
    'www.mimit.gov.it',
    'nuovatvdigitale.mise.gov.it',
    'www.interno.gov.it',
    'www.prefettura.it',
    'www.esteri.it',
    'www.salute.gov.it',
    'www.aifa.gov.it',
    'www.giustizia.it',
    'www.difesa.it',
    'www.carabinieri.it',
    'poliziapenitenziaria.gov.it',
    'www.poliziadistato.it',
    'www.vigilfuoco.it',
    'www.mef.gov.it',
    'www.italiadomani.gov.it',
    'www.agenziaentrate.gov.it',
    'www.politicheagricole.it',
    'www.mase.gov.it',
    'www.mit.gov.it',
    'www.lavoro.gov.it',
    'www.miur.gov.it',
    'www.mur.gov.it',
    'istruzione.it',
    'www.beniculturali.it',
    'cultura.gov.it',
    'www.ministeroturismo.gov.it',
    'www.funzionepubblica.gov.it',
    'www.sport.governo.it',
    'www.politichegiovanili.gov.it',
    'www.inps.it',
    'www.italia.it',
    'www.infratelitalia.it',
    'bandaultralarga.italia.it',
    'www.impresainungiorno.gov.it',
    'impresa.italia.it',
    'innovazione.gov.it',
    'padigitale2026.gov.it',
    'io.italia.it',
    'www.agid.gov.it',
    'www.anagrafenazionale.interno.it',
    'www.pagopa.gov.it',
    'www.spid.gov.it',
    'www.protezionecivile.it',
    'www.protezionecivile.gov.it',
    'sisma2016.gov.it',
    'www.camera.it',
    'www.senato.it',
    'www.quirinale.it',
    'www.polostrategiconazionale.it',
    'www.finanze.it',
    'connetti.italia.it',
    'www.agcom.it',
    'www.pagopa.it',
    'www.inpa.gov.it',
    'anncsu.gov.it',
    'www.interop.pagopa.it',
    'dati.gov.it',
    'www.csirt.gov.it',
    'www.cartaidentita.interno.gov.it',
    'www.prenotazionicie.interno.gov.it',
    'passaportonline.poliziadistato.it',
    'www.piattaformaunicanazionale.it',
    'www.acn.gov.it',
    'developers.italia.it',
    'www.nic.it',
]

domains += ['www.gov.uk', ]


def main():
    for domain in domains:
        print('-' * len(domain))
        print(domain)
        print('-' * len(domain))

        domain = domain[4:] if domain.startswith('www.') else domain

        outcomes = {
            'http': req(f'http://{domain}'),
            'http+www': req(f'http://www.{domain}'),
            'https': req(f'https://{domain}'),
            'https+www': req(f'https://www.{domain}'),
        }

        for k in ['http', 'http+www']:
            if outcomes[k]['error']:
                print(
                    f'❌ {outcomes[k]["initial_url"]} leads to {outcomes[k]["final_url"]} with error: {outcomes[k]["error"]}')
            elif outcomes[k]['final_https']:
                print(
                    f'✅ {outcomes[k]["initial_url"]} redirects to {outcomes[k]["final_url"]} (HTTPS as expected)')
            else:
                print(
                    f'❌ {outcomes[k]["initial_url"]} does not redirect to HTTPS ({outcomes[k]["final_url"]})')

        for k in ['https', 'https+www']:
            if outcomes[k]['error']:
                print(
                    f'❌ {outcomes[k]["initial_url"]} leads to {outcomes[k]["final_url"]} with error: {outcomes[k]["error"]}')
            elif outcomes[k]['final_https']:
                print(
                    f'✅ {outcomes[k]["initial_url"]} remains HTTPS as expected ({outcomes[k]["final_url"]})')
            else:
                print(
                    f'❌ {outcomes[k]["initial_url"]} redirects to {outcomes[k]["final_url"]} (should not redirect to HTTP)')

        order = ['https+www', 'https', 'http+www', 'http']
        canonical = None
        for k in order:
            if outcomes[k]['error'] is None:
                canonical = k
                break

        ipv6 = None
        try:
            answer = dns.resolver.resolve(domain, 'AAAA')
            addresses = [str(ip) for ip in answer.rrset.items]
            ipv6 = ', '.join(addresses)
        except dns.resolver.NoAnswer:
            pass

        nameserver = None
        try:
            answer = dns.resolver.resolve(domain, 'NS')
            nameservers = [str(ns) for ns in answer.rrset.items]
            nameserver = ', '.join(nameservers)
        except dns.resolver.NoAnswer:
            pass

        whois_info = whois.whois(domain)

        if canonical is None:
            print('⚠️  No canonical')
        else:
            print(f'\n🔍 Using canonical: {canonical}')
            print(f'🖥️  Server: {outcomes[canonical]["server"]}')
            print(f'🔌 Powered by: {outcomes[canonical]["powered_by"]}')
            print(f'🔒️ HSTS: {outcomes[canonical]["hsts"]}')
            print(f'🔒️ CSP: {outcomes[canonical]["csp"]}')
        print(f'🌐 IPv6: {ipv6}')
        print(f'🔧 Nameserver: {nameserver}')
        print(f'🔧 Registrar: {whois_info.registrar_name} / {whois_info.registrar}')

        print()


def req(url: str):
    error = None
    server = None
    hsts = None
    csp = None
    powered_by = None
    try:
        resp = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0'
        }, allow_redirects=True, timeout=15)
        final_url = resp.url
        server = resp.headers.get('Server')
        hsts = resp.headers.get('Strict-Transport-Security')
        csp = resp.headers.get('Content-Security-Policy')
        if not csp:
            csp = '<meta>' if 'content-security-policy' in resp.text.lower() else None
        powered_by = resp.headers.get('X-Powered-By')
    except requests.exceptions.SSLError as e:
        error = 'ssl ' + str(e)
        final_url = e.request.url
    except requests.exceptions.ConnectTimeout as e:
        error = 'timeout'
        final_url = e.request.url
    except requests.exceptions.ReadTimeout as e:
        error = 'read timeout'
        final_url = e.request.url
    except requests.exceptions.ConnectionError as e:
        if '[Errno 8] nodename nor servname ' in str(e):
            error = 'dns'
        else:
            error = 'connection'
        final_url = e.request.url

    return {
        'error': error,
        'initial_url': url,
        'final_url': final_url,
        'final_https': final_url.split(':')[0] == 'https',
        'final_www': final_url.split('/')[2].startswith('www.'),
        'server': server,
        'hsts': hsts,
        'csp': csp,
        'powered_by': powered_by,
    }


if __name__ == '__main__':
    main()
