import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import supabase
from .services.metrics import calculate_dashboard_metrics
from .services.ai import generate_diagnostic

app = FastAPI()

# Configuração de templates e estáticos usando caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Renderiza a página principal do dashboard."""
    try:
        if not supabase:
            return {"error": "Conexão com o Supabase não configurada. Verifique as Environment Variables na Vercel (SUPABASE_URL e SUPABASE_ANON_KEY)."}

        metrics = calculate_dashboard_metrics(ano, mes)
        
        # Preparar dados para o Plotly
        gauge_data = {
            "value": metrics["kpis"]["termometro_vgl"] * 100,
            "title": "Termômetro VGL"
        }
        
        funil_data = {
            "valores": [
                metrics["funil"]["leads"],
                metrics["funil"]["interacoes"],
                metrics["funil"]["visitas"],
                metrics["funil"]["condicoes"],
                metrics["funil"]["alugados"]
            ],
            "fases": ["Leads", "Interações", "Visitas", "Condições", "Alugados"],
            "referencia": metrics["referencia_nacional"]
        }
        
        bairros_data = {
            "alugados": [10, 8, 5, 3],
            "nomes": ["Centro", "São Bento", "Cidade Alta", "Planalto"]
        }

        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        return templates.TemplateResponse("dashboard/index.html", {
            "request": request,
            "kpis": metrics["kpis"],
            "mes": mes,
            "ano": ano,
            "meses": meses,
            "gauge_data": gauge_data,
            "funil_data": funil_data,
            "bairros_data": bairros_data
        })
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/health")
def health():
    return {"status": "ok", "architecture": "serverless"}

@app.get("/api/dashboard")
def get_dashboard(ano: int = 2026, mes: str = "Abril"):
    """Retorna os KPIs consolidados para o dashboard."""
    try:
        metrics = calculate_dashboard_metrics(ano, mes)
        return metrics
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/ai-diagnostic")
def get_diagnostic(ano: int = 2026, mes: str = "Abril"):
    """Gera insight via Gemini 1.5 Pro."""
    try:
        metrics = calculate_dashboard_metrics(ano, mes)
        diagnostic = generate_diagnostic(metrics)
        return {"diagnostic": diagnostic}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
@app.get("/admin/leads")
def admin_leads(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Gestão de Leads"})

@app.get("/admin/contratos")
def admin_contratos(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Gestão de Contratos"})

@app.get("/admin/captacao")
def admin_captacao(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Gestão de Captação"})

@app.get("/admin/desocupacao")
def admin_desocupacao(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Gestão de Desocupação"})

@app.get("/admin/okr")
def admin_okr(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Acompanhamento de OKRs"})

@app.get("/admin/metas")
def admin_metas(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Definição de Metas"})

@app.get("/admin")
def admin_settings(request: Request):
    return templates.TemplateResponse("admin/placeholder.html", {"request": request, "title": "Configurações do Sistema"})

# Export para a Vercel
index = app
