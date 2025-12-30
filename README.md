# LogCenter API

## Visão Geral
- API de ingestão e observabilidade de logs para múltiplos projetos
- Stack: `Django 4.x`, `Django REST Framework`, `drf-spectacular`, `SQLite`
- Auth: Header `Authorization: Bearer <LOG_INGEST_TOKEN>`
- Deploy: PythonAnywhere via `WSGI`

## Endpoints
- `POST /api/ingest/` recebe logs remotos
- `GET /api/logs/` lista logs com filtros `host`, `type`, `level`, `since`, `until`, `limit`
- `GET /api/health/` status
- `GET /api/schema/` OpenAPI 3
- `GET /api/docs/` Swagger UI
- `GET /dashboard/` leitura pública

## Payload de Ingestão
```json
{
  "host": "vilksonvtch.pythonanywhere.com",
  "type": "access | error | server",
  "message": "linha completa do log",
  "hash": "sha256",
  "timestamp": 1735532123.123
}
```

## Regras de Alertas
- `>= 5 ERROR` em 1 minuto: alerta
- `CRITICAL`: alerta imediato

## Instalação Local
- Criar virtualenv: `python -m venv .venv && .venv\\Scripts\\activate` (Windows)
- Instalar deps: `pip install -r requirements.txt`
- Migrar: `python manage.py migrate`
- Token: definir `LOG_INGEST_TOKEN` no ambiente
  - Windows PowerShell: `$env:LOG_INGEST_TOKEN = "seu-token"`
- Rodar: `python manage.py runserver`

## Deploy PythonAnywhere
- Criar virtualenv e instalar deps
- Subir código para `~/mysite/logcenter`
- Configurar `WSGI` para apontar para `logcenter/logcenter/wsgi.py`
- Definir variáveis de ambiente, incluindo `LOG_INGEST_TOKEN`
- Coletar estáticos: `python manage.py collectstatic`
- Reiniciar app via painel

## URLs de Produção
- Base: `https://<seu-usuario>.pythonanywhere.com/`
- `https://<host>/api/ingest/`
- `https://<host>/api/logs/`
- `https://<host>/api/health/`
- `https://<host>/api/schema/`
- `https://<host>/api/docs/`
- `https://<host>/dashboard/`

## Testes
- Executar: `python manage.py test`
- Cobertura mínima:
  - Token inválido
  - Log duplicado
  - Payload inválido
  - Alerta disparado
  - Filtros funcionando

