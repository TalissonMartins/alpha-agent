import csv
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ..store.rodadas import ultimas

LOGIN = """<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\">
  <title>AlphaAgent</title>
  <style>
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #0c1117; color: #e8e6e3; font-family: sans-serif; }
    form { width: 320px; background: #161d27; border: 1px solid #263140; border-radius: 12px; padding: 28px; }
    h1 span { color: #c4a46a; }
    p { color: #8b93a1; }
    input, button { width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; border: 1px solid #263140; }
    input { background: #0c1117; color: #e8e6e3; }
    button { background: #c4a46a; color: #1a1408; font-weight: 650; }
  </style>
</head>
<body>
  <form id=\"acesso\">
    <h1>Alpha<span>Agent</span></h1>
    <p>Acesso interno. Classificacao, nao ordem.</p>
    <input id=\"chave\" type=\"password\" placeholder=\"Chave de acesso\" required>
    <button type=\"submit\">Entrar</button>
    <p id=\"erro\"></p>
  </form>
  <script>
    document.getElementById('acesso').onsubmit = async (evento) => {
      evento.preventDefault();
      const chave = document.getElementById('chave').value;
      const resposta = await fetch('/api/rodadas', { headers: { 'X-API-Key': chave } });
      if (!resposta.ok) { document.getElementById('erro').textContent = 'Chave recusada.'; return; }
      sessionStorage.setItem('alphaagent_chave', chave);
      location.href = '/painel';
    };
  </script>
</body>
</html>
"""

ROOT = Path(__file__).resolve().parents[2]
RELATORIOS = ROOT / "relatorios"
ROTAS = {
    "/api/alocacao": "alocacao.csv",
    "/api/renda-fixa": "renda_fixa.csv",
    "/api/exterior": "exterior.csv",
    "/api/fiis": "fiis.csv",
    "/api/mudancas": "mudancas.csv",
}


def chave_configurada() -> str:
    return os.environ.get("ALPHAAGENT_API_KEY", "").strip()


def autorizado(cabecalho: str | None, chave: str) -> bool:
    if not chave:
        return False
    return cabecalho == chave


def ler_csv(nome: str) -> list[dict[str, str]]:
    caminho = RELATORIOS / nome
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


class Leitor(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self._bytes(200, LOGIN.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path == "/painel":
            caminho = RELATORIOS / "carteira.html"
            if not caminho.exists():
                self._bytes(404, b"rode py -m src.main antes", "text/plain; charset=utf-8")
                return
            self._bytes(200, caminho.read_bytes(), "text/html; charset=utf-8")
            return
        chave = chave_configurada()
        if not autorizado(self.headers.get("X-API-Key"), chave):
            self._bytes(401, b"chave ausente ou invalida", "text/plain; charset=utf-8")
            return
        if self.path == "/api/rodadas":
            corpo = json.dumps(ultimas(ROOT / "dados" / "alphaagent.db"), ensure_ascii=False).encode("utf-8")
            self._bytes(200, corpo, "application/json; charset=utf-8")
            return
        nome = ROTAS.get(self.path)
        if nome is None or not (RELATORIOS / nome).exists():
            self._bytes(404, b"rota ou relatorio ausente", "text/plain; charset=utf-8")
            return
        corpo = json.dumps(ler_csv(nome), ensure_ascii=False).encode("utf-8")
        self._bytes(200, corpo, "application/json; charset=utf-8")

    def _bytes(self, status: int, corpo: bytes, tipo: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, formato: str, *args: object) -> None:
        return


def servir(porta: int = 8000) -> None:
    chave = chave_configurada()
    if not chave or chave == "teste-interno":
        raise SystemExit("Defina ALPHAAGENT_API_KEY com um valor seu, diferente de teste-interno.")
    host = os.environ.get("ALPHAAGENT_HOST", "127.0.0.1")
    servidor = ThreadingHTTPServer((host, porta), Leitor)
    print(f"AlphaAgent em http://{host}:{porta}  Header: X-API-Key")
    servidor.serve_forever()


if __name__ == "__main__":
    servir()
