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

        return templates.TemplateResponse(
            request=request,
            name="dashboard/index.html",
            context={
                "kpis": metrics["kpis"],
                "mes": mes,
                "ano": ano,
                "meses": meses,
                "gauge_data": gauge_data,
                "funil_data": funil_data,
                "bairros_data": bairros_data
            }
        )
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
def admin_leads(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Gerenciamento de Leads e Funil."""
    try:
        # 1. Buscar Leads com Joins
        res = supabase.table("leads").select("*, bairros(nome), corretores(nome)").eq("ano", ano).eq("mes", mes).order("created_at", desc=True).execute()
        leads_raw = res.data if res else []
        
        # Formatar dados para o template
        leads = []
        funil = {"leads": 0, "interacoes": 0, "visitas": 0, "condicoes": 0, "alugados": 0}
        
        for l in leads_raw:
            lead_item = {
                "id": l["id"],
                "nome": l["nome"],
                "telefone": l["telefone"],
                "midia": l["midia"],
                "bairro_nome": l.get("bairros", {}).get("nome", "N/A") if l.get("bairros") else "N/A",
                "corretor_nome": l.get("corretores", {}).get("nome", "N/A") if l.get("corretores") else "N/A",
                "lead_semana": l["lead_semana"],
                "interacao_semana": l["interacao_semana"],
                "visita_semana": l["visita_semana"],
                "condicao_semana": l["condicao_semana"],
                "alugado_semana": l["alugado_semana"]
            }
            leads.append(lead_item)
            
            # Contagem para o funil rápido
            if l["lead_semana"]: funil["leads"] += 1
            if l["interacao_semana"]: funil["interacoes"] += 1
            if l["visita_semana"]: funil["visitas"] += 1
            if l["condicao_semana"]: funil["condicoes"] += 1
            if l["alugado_semana"]: funil["alugados"] += 1

        return templates.TemplateResponse(
            request=request, 
            name="admin/leads.html", 
            context={
                "leads": leads,
                "funil": funil,
                "ano": ano,
                "mes": mes
            }
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/contratos")
def admin_contratos(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Matriz de Segmentação Imobiliária (MSI)."""
    try:
        # 1. Buscar Métricas Globais para os cards
        metrics = calculate_dashboard_metrics(ano, mes)
        
        # 2. Buscar Contratos Detalhados com Joins
        res = supabase.table("msi_alugados").select("*, bairros(nome), corretores(nome)").eq("ano", ano).eq("mes", mes).order("dia", desc=True).execute()
        contratos_raw = res.data if res else []
        
        contratos = []
        for c in contratos_raw:
            contratos.append({
                **c,
                "bairro_nome": c.get("bairros", {}).get("nome", "N/A") if c.get("bairros") else "N/A",
                "corretor_nome": c.get("corretores", {}).get("nome", "N/A") if c.get("corretores") else "N/A",
            })

        return templates.TemplateResponse(
            request=request, 
            name="admin/msi.html", 
            context={
                "contratos": contratos,
                "stats": metrics["kpis"],
                "ano": ano,
                "mes": mes
            }
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/captacao")
def admin_captacao(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Gerenciamento de Captações."""
    try:
        # 1. Buscar Captações com Joins
        try:
            res = supabase.table("captacoes").select("*, bairros(nome), corretores(nome)").eq("ano", ano).eq("mes", mes).order("id", desc=True).execute()
            capt_raw = res.data if res else []
        except Exception as table_err:
            print(f"Erro ao acessar tabela captacoes: {table_err}")
            capt_raw = []
        
        captacoes = []
        captados_count = 0
        for c in capt_raw:
            if c["status"] == "Captado":
                captados_count += 1
                
            captacoes.append({
                **c,
                "bairro_nome": c.get("bairros", {}).get("nome", "N/A") if c.get("bairros") else "N/A",
                "captador_nome": c.get("corretores", {}).get("nome", "N/A") if c.get("corretores") else "N/A",
            })

        total_apontados = len(captacoes)
        stats = {
            "total": total_apontados,
            "captados": captados_count,
            "conversao": (captados_count / total_apontados * 100) if total_apontados > 0 else 0
        }

        return templates.TemplateResponse(
            request=request, 
            name="admin/captacao.html", 
            context={
                "captacoes": captacoes,
                "stats": stats,
                "ano": ano,
                "mes": mes
            }
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/desocupacao")
def admin_desocupacao(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Gerenciamento de Desocupações."""
    try:
        # 1. Buscar Métricas para os cards (Churn, etc)
        metrics = calculate_dashboard_metrics(ano, mes)
        
        # 2. Buscar Desocupações com Joins (Usando ID para ordem pois não existe coluna DIA)
        res = supabase.table("desocupacoes").select("*, bairros(nome)").eq("ano", ano).eq("mes", mes).order("id", desc=True).execute()
        desoc_raw = res.data if res else []
        
        desocupacoes = []
        for d in desoc_raw:
            desocupacoes.append({
                **d,
                "codigo_imovel": d.get("codigo_sistema", "N/A"),
                "bairro_nome": d.get("bairros", {}).get("nome", "N/A") if d.get("bairros") else "N/A",
                "motivo": d.get("motivo", "Não informado")
            })

        return templates.TemplateResponse(
            request=request, 
            name="admin/desocupacao.html", 
            context={
                "desocupacoes": desocupacoes,
                "stats": metrics["kpis"],
                "ano": ano,
                "mes": mes
            }
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/okr")
def admin_okr(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Gerenciamento de OKRs."""
    try:
        # 1. Buscar KRs do mês
        res = supabase.table("okrs").select("*").eq("ano", ano).eq("mes", mes).execute()
        krs_raw = res.data if res else []
        
        # 2. Processar KRs e Agrupar por Objetivo
        krs = []
        objetivos_map = {}
        
        for k in krs_raw:
            alcançado = float(k["semana_1"] or 0) + float(k["semana_2"] or 0) + float(k["semana_3"] or 0) + float(k["semana_4"] or 0) + float(k["semana_5"] or 0)
            meta = float(k["meta"] or 1) # Evitar divisão por zero
            progresso = (alcançado / meta) * 100
            
            kr_item = {
                **k,
                "alcançado": alcançado,
                "progresso": min(progresso, 100) # Cap no 100%
            }
            krs.append(kr_item)
            
            # Agrupar para o resumo do objetivo
            obj_name = k["objetivo"]
            if obj_name not in objetivos_map:
                objetivos_map[obj_name] = {"objetivo": obj_name, "soma_progresso": 0, "count": 0}
            
            objetivos_map[obj_name]["soma_progresso"] += min(progresso, 100)
            objetivos_map[obj_name]["count"] += 1

        # Calcular média dos objetivos
        objetivos = []
        for obj in objetivos_map.values():
            obj["progresso_medio"] = obj["soma_progresso"] / obj["count"]
            objetivos.append(obj)

        return templates.TemplateResponse(
            request=request, 
            name="admin/okr.html", 
            context={
                "krs": krs,
                "objetivos": objetivos,
                "ano": ano,
                "mes": mes
            }
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/metas")
def admin_metas(request: Request, ano: int = 2026, mes: str = "Abril"):
    """Configuração de Metas."""
    try:
        # 1. Buscar meta do mês
        res = supabase.table("metas_mensais").select("*").eq("ano", ano).eq("mes", mes).maybe_single().execute()
        meta = (res.data if res else None) or {"meta_qtd_1": 0, "meta_vgl_1": 0, "meta_capt_1": 0}
        
        # 2. Buscar todas as metas do ano para a tabela
        res_ano = supabase.table("metas_mensais").select("*").eq("ano", ano).execute()
        metas_existentes = {m["mes"]: m for m in res_ano.data} if res_ano else {}
        
        meses_lista = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        metas_ano = []
        for m_nome in meses_lista:
            metas_ano.append(metas_existentes.get(m_nome, {"mes": m_nome, "meta_qtd_1": 0, "meta_vgl_1": 0, "meta_capt_1": 0}))

        return templates.TemplateResponse(
            request=request, 
            name="admin/metas.html", 
            context={
                "meta": meta,
                "metas_ano": metas_ano,
                "ano": ano,
                "mes": mes
            }
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.post("/admin/metas/save")
async def save_metas(request: Request):
    """Salva as metas no banco."""
    try:
        form = await request.form()
        data = {
            "ano": int(form.get("ano")),
            "mes": form.get("mes"),
            "meta_qtd_1": int(form.get("meta_qtd_1") or 0),
            "meta_vgl_1": float(form.get("meta_vgl_1") or 0),
            "meta_capt_1": int(form.get("meta_capt_1") or 0),
        }
        
        # Upsert baseado em (mes, ano)
        supabase.table("metas_mensais").upsert(data, on_conflict="mes,ano").execute()
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/admin/metas?ano={data['ano']}&mes={data['mes']}", status_code=303)
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/admin")
def admin_settings(request: Request):
    return templates.TemplateResponse(request=request, name="admin/placeholder.html", context={"title": "Configurações do Sistema"})

# Export para a Vercel
index = app
