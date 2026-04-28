import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuração do Gemini
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_diagnostic(data: dict):
    """
    Gera um diagnóstico inteligente baseado nos KPIs do dashboard.
    """
    if not api_key:
        return "Erro: GOOGLE_API_KEY não configurada no servidor."

    model = genai.GenerativeModel('gemini-1.5-pro')
    
    kpis = data.get("kpis", {})
    funil = data.get("funil", {})
    ref_nacional = data.get("referencia_nacional", [100, 70, 42, 20, 8])
    
    # Cálculo de conversões reais do funil
    leads = funil.get("leads", 0)
    interacoes = funil.get("interacoes", 0)
    visitas = funil.get("visitas", 0)
    condicoes = funil.get("condicoes", 0)
    alugados = funil.get("alugados", 0)
    
    conv_interacao = (interacoes / leads * 100) if leads > 0 else 0
    conv_visita = (visitas / interacoes * 100) if interacoes > 0 else 0
    conv_condicao = (condicoes / visitas * 100) if visitas > 0 else 0
    conv_alugado = (alugados / condicoes * 100) if condicoes > 0 else 0
    conv_geral = (alugados / leads * 100) if leads > 0 else 0

    prompt = f"""
    Você é um Consultor Estratégico de Imobiliárias especializado no método "Painel 220".
    Analise os seguintes KPIs mensais da imobiliária (Mês: {data.get('mes')}, Ano: {data.get('ano')}):

    MÉTRICAS PRINCIPAIS:
    - Alugados: {kpis.get('alugados')}
    - VGL (Valor Geral de Locação): R$ {kpis.get('vgl', 0):,.2f}
    - Ticket Médio: R$ {kpis.get('ticket_medio', 0):,.2f}
    - Termômetro VGL (Atingimento da Meta): {kpis.get('termometro_vgl', 0)*100:.1f}%
    - Churn (Taxa de Desocupação): {kpis.get('churn', 0):.2f}%
    - Saldo Líquido de Carteira: {kpis.get('saldo_novos')} contratos

    FUNIL DE VENDAS (FDL):
    - Leads: {leads}
    - Interações: {interacoes} (Conversão: {conv_interacao:.1f}% | Ref: {ref_nacional[1]}%)
    - Visitas: {visitas} (Conversão: {conv_visita:.1f}% | Ref: {ref_nacional[2]}%)
    - Condições: {condicoes} (Conversão: {conv_condicao:.1f}% | Ref: {ref_nacional[3]}%)
    - Alugados: {alugados} (Conversão: {conv_alugado:.1f}% | Ref: {ref_nacional[4]}%)
    - Conversão Geral: {conv_geral:.1f}% (Ref Nacional: 8.0%)

    REGRAS DO DIAGNÓSTICO:
    1. Identifique o maior gargalo no funil (onde a conversão está mais abaixo da referência).
    2. Comente sobre o Ticket Médio vs Meta (Referência de R$ 4.500).
    3. Analise o impacto do Churn no crescimento da carteira.
    4. Dê 3 recomendações acionáveis e curtas para melhorar o resultado no próximo mês.
    5. Use um tom profissional, direto e motivador.

    Responda em Markdown.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar diagnóstico: {str(e)}"
