import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import supabase
from .services.metrics import calculate_dashboard_metrics
from .services.ai import generate_diagnostic

app = FastAPI()

# Configuração de templates e estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        return {"error": str(e)}

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
        return {"error": str(e)}

@app.get("/api/ai-diagnostic")
def get_diagnostic(ano: int = 2026, mes: str = "Abril"):
    """Gera insight via Gemini 1.5 Pro."""
    try:
        metrics = calculate_dashboard_metrics(ano, mes)
        diagnostic = generate_diagnostic(metrics)
        return {"diagnostic": diagnostic}
    except Exception as e:
        return {"error": str(e)}

# Export para a Vercel
index = app
