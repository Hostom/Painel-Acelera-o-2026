"""
Metrics Service — Cálculos de Performance (MSI, FDL, OKR)
Migrado do Django para Supabase-py + Pandas.
"""
import pandas as pd
from ..database import supabase

def calculate_dashboard_metrics(ano: int, mes: str):
    """
    Consolida todos os KPIs extraindo dados diretamente do Supabase.
    """
    # 1. Buscar Alugados (MSI)
    res_msi = supabase.table("msi_alugados").select("*").eq("ano", ano).eq("mes", mes).execute()
    df_msi = pd.DataFrame(res_msi.data if res_msi else [])
    
    alugados_qtd = len(df_msi)
    vgl = df_msi["valor_aluguel"].sum() if not df_msi.empty else 0
    vgc = (df_msi["valor_aluguel"] * df_msi["taxa_adm_percent"]).sum() if not df_msi.empty else 0
    ticket_medio = vgl / alugados_qtd if alugados_qtd > 0 else 0

    # 2. Buscar Desocupações
    res_desoc = supabase.table("desocupacoes").select("*").eq("ano", ano).eq("mes", mes).execute()
    df_desoc = pd.DataFrame(res_desoc.data if res_desoc else [])
    desoc_qtd = len(df_desoc)
    desoc_valor = df_desoc["valor_aluguel"].sum() if not df_desoc.empty else 0

    # 3. Buscar Metas
    res_metas = supabase.table("metas_mensais").select("*").eq("ano", ano).eq("mes", mes).maybe_single().execute()
    meta = (res_metas.data if res_metas else None) or {"meta_qtd_1": 0, "meta_vgl_1": 0, "meta_capt_1": 0}
    
    meta_qtd = meta.get("meta_qtd_1", 0)
    meta_vgl_val = meta.get("meta_vgl_1", 0) or (meta_qtd * 4500) # Fallback planilha

    # 4. Cálculos de Saldo e Churn
    # Mapeamento de meses para filtros
    meses_lista = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    try:
        mes_idx = meses_lista.index(mes) + 1
    except ValueError:
        mes_idx = 1

    # Total Alugados histórico
    res_hist_msi = supabase.table("msi_alugados").select("id").execute()
    df_hist_msi = pd.DataFrame(res_hist_msi.data if res_hist_msi else [])
    
    total_alugados_hist = len(df_hist_msi)
    
    # Total Desocupações histórico
    res_hist_desoc = supabase.table("desocupacoes").select("id").execute()
    df_hist_desoc = pd.DataFrame(res_hist_desoc.data if res_hist_desoc else [])
    total_desoc_hist = len(df_hist_desoc)

    # Carteira Atual = Tudo que entrou - Tudo que saiu (até hoje)
    total_carteira = total_alugados_hist - total_desoc_hist
    
    # Churn = (Desocupados no mês / Carteira Total) * 100
    churn = (desoc_qtd / total_carteira) * 100 if total_carteira > 0 else 0

    # 5. FDL (Funil)
    res_leads = supabase.table("leads").select("*").eq("ano", ano).eq("mes", mes).execute()
    df_leads = pd.DataFrame(res_leads.data if res_leads else [])
    
    leads_fases = {
        "leads": len(df_leads[df_leads["lead_semana"] != ""]) if not df_leads.empty else 0,
        "interacoes": len(df_leads[df_leads["interacao_semana"] != ""]) if not df_leads.empty else 0,
        "visitas": len(df_leads[df_leads["visita_semana"] != ""]) if not df_leads.empty else 0,
        "condicoes": len(df_leads[df_leads["condicao_semana"] != ""]) if not df_leads.empty else 0,
        "alugados": len(df_leads[df_leads["alugado_semana"] != ""]) if not df_leads.empty else 0,
    }

    return {
        "ano": ano,
        "mes": mes,
        "kpis": {
            "alugados": alugados_qtd,
            "vgl": float(vgl),
            "vgc": float(vgc),
            "ticket_medio": float(ticket_medio),
            "termometro_vgl": float(vgl / meta_vgl_val) if meta_vgl_val > 0 else 0,
            "saldo_novos": alugados_qtd - desoc_qtd,
            "total_carteira": total_carteira,
            "churn": float(churn),
            "desocupados": desoc_qtd,
            "desoc_valor": float(desoc_valor)
        },
        "funil": leads_fases,
        "referencia_nacional": [100, 70, 42, 20, 8]
    }

