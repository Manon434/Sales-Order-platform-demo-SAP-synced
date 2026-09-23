import json
import os
import base64
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
SAP_BASE_URL = os.getenv('SAP_BASE_URL', 'http://203.112.143.241:8000').rstrip('/')
SAP_CLIENT = os.getenv('SAP_CLIENT', '100')
SAP_TIMEOUT = int(os.getenv('SAP_TIMEOUT', '30'))
SAP_USER = os.getenv('SAP_USER', '')
SAP_PASSWORD = os.getenv('SAP_PASSWORD', '')
SAP_TOKEN = os.getenv('SAP_TOKEN', '')


def auth_headers():
    headers = {'Accept': 'application/json'}
    if SAP_TOKEN:
        headers['Authorization'] = f'Bearer {SAP_TOKEN}'
    elif SAP_USER and SAP_PASSWORD:
        token = base64.b64encode(f'{SAP_USER}:{SAP_PASSWORD}'.encode()).decode()
        headers['Authorization'] = f'Basic {token}'
    return headers


def fetch_sap(path, params=None):
    params = dict(params or {})
    params.setdefault('sap-client', SAP_CLIENT)
    url = f'{SAP_BASE_URL}{path}?{urlencode(params)}'
    req = Request(url, headers=auth_headers(), method='GET')
    try:
        with urlopen(req, timeout=SAP_TIMEOUT) as response:
            body = response.read().decode('utf-8', errors='replace')
            data = json.loads(body)
            return data, response.status
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        try:
            detail = json.loads(body)
        except Exception:
            detail = body[:1000]
        raise RuntimeError(f'SAP HTTP {exc.code}: {detail}')
    except URLError as exc:
        raise RuntimeError(f'SAP connection failed: {exc.reason}')
    except TimeoutError:
        raise RuntimeError('SAP request timed out')
    except json.JSONDecodeError:
        raise RuntimeError('SAP returned invalid JSON')


class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        raw = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == '/api/sap/health':
                data, status = fetch_sap('/zso_aprd/SOA')
                self._send_json({'ok': True, 'status': status, 'sap': True, 'sampleCount': len(data) if isinstance(data, list) else None})
                return

            if parsed.path == '/api/sap/orders':
                employee = query.get('employee', [''])[0].strip().upper()
                if employee not in {'E0003', 'E0006'}:
                    self._send_json({'error': 'employee must be E0003 or E0006'}, 400)
                    return
                data, status = fetch_sap('/zso_apr/SO', {'ZNAME11': employee})
                self._send_json(data, status)
                return

            if parsed.path == '/api/sap/approvals':
                data, status = fetch_sap('/zso_aprd/SOA')
                self._send_json(data, status)
                return

            return super().do_GET()
        except Exception as exc:
            self._send_json({'error': str(exc)}, 502)

    def log_message(self, fmt, *args):
        print(f'[SERVER] {self.address_string()} - {fmt % args}')


if __name__ == '__main__':
    print('GreenPaper Sales Order Management - Live SAP Proxy')
    print(f'Web app: http://localhost:{PORT}')
    print(f'SAP base: {SAP_BASE_URL}')
    print('SAP endpoints: E0003, E0006, SOA')
    print('Automatic browser synchronization: every 15 minutes')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
