import streamlit as st
import pandas as pd
import graphviz
import re
from io import StringIO

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Motor de Campanhas CRM - Natura",
    page_icon="🌿",
    layout="wide"
)

# ==============================================================================
# FUNÇÕES DOS AGENTES E PROCESSAMENTO (Simulação)
# ==============================================================================

def simular_organizador_de_contexto(diretrizes, planos_anteriores):
    """
    Simula o agente "Organizador de Contexto".
    Extrai informações relevantes dos textos de entrada.
    """
    if not diretrizes and not planos_anteriores:
        return "Aguardando input de diretrizes e planejamentos..."
    
    # Em um projeto real, aqui entraria um modelo de NLP para sumarização.
    # Para o protótipo, fazemos uma extração simples de palavras-chave.
    info_relevantes = "### Informações de Negócio Relevantes\n\n"
    if diretrizes:
        info_relevantes += f"**Diretrizes de Comunicação:**\n- Foco em sustentabilidade e produtos da linha Ekos.\n- Tom de voz: próximo e inspirador.\n- Promoção principal: 20% de desconto na primeira compra.\n\n"
    if planos_anteriores:
        info_relevantes += f"**Aprendizados de Planos Anteriores:**\n- Campanhas de SMS tiveram alta taxa de conversão para o público jovem.\n- E-mails com vídeos de tutoriais aumentaram o engajamento em 30%.\n- Evitar comunicação excessiva aos sábados."
    
    return info_relevantes

def simular_especialista_de_dados(df):
    """
    Simula o agente "Especialista de Dados".
    Gera um direcional de performance a partir dos dados das consultoras.
    """
    if df is None:
        return "Aguardando carregamento dos dados de perfil das consultoras..."
        
    # Em um projeto real, aqui entraria uma análise estatística mais profunda.
    # Para o protótipo, calculamos algumas médias e destaques.
    media_vendas = df['vendas_ultimo_ciclo'].mean()
    media_engajamento = df['taxa_engajamento'].mean()
    
    direcional = f"""
    ### Direcional de Performance Detalhado
    
    - **Performance de Vendas:** A média de vendas no último ciclo foi de **R$ {media_vendas:.2f}**. Consultoras da região Sudeste apresentaram performance 15% acima da média.
    - **Nível de Engajamento:** A taxa média de engajamento com as comunicações é de **{media_engajamento:.1f}%**. As consultoras com menos de 6 meses de casa possuem engajamento 20% menor e representam uma oportunidade de atuação.
    - **Recomendação:** Focar em campanhas de reativação para consultoras com vendas abaixo da média e engajamento baixo.
    """
    return direcional

def gerar_fluxograma_campanha(id_campanha, descricao_textual):
    """
    Gera um objeto de grafo Graphviz a partir de uma descrição textual.
    (Função adaptada da nossa conversa anterior).
    """
    dot = graphviz.Digraph(
        comment=f'Fluxograma da Campanha {id_campanha}',
        graph_attr={'rankdir': 'TB', 'bgcolor': 'transparent', 'splines': 'ortho'},
        node_attr={'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#FFFFFF', 'fontname': 'Helvetica'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '10'}
    )
    
    # Função interna para parsear o texto
    def extrair_etapas_e_conexoes(descricao):
        etapas = {}
        conexoes = []
        for i, linha in enumerate(descricao.strip().split('\n')):
            linha = linha.strip()
            if not linha: continue
            
            tipo_match = re.match(r"(\w+):(.+)", linha)
            conexao_match = re.match(r"CONEXÃO:\s*(.+?)\s*->\s*(.+?)(?:\s*\[(.+?)\])?", linha)

            if conexao_match:
                origem, destino, rotulo = conexao_match.groups()
                conexoes.append({'origem': origem.strip(), 'destino': destino.strip(), 'rotulo': rotulo.strip() if rotulo else ''})
            elif tipo_match:
                tipo, nome = tipo_match.groups()
                tipo = tipo.strip().upper()
                nome = nome.strip()
                etapas[nome] = {'tipo': tipo, 'id': f'id_{i}'}
        return etapas, conexoes

    etapas, conexoes = extrair_etapas_e_conexoes(descricao_textual)

    for nome, attrs in etapas.items():
        cor = '#BBDEFB' # Azul padrão
        forma = 'box'
        if attrs['tipo'] == 'INÍCIO':
            cor, forma = '#C8E6C9', 'circle' # Verde
        elif attrs['tipo'] == 'FIM':
            cor, forma = '#FFCDD2', 'doublecircle' # Vermelho
        elif attrs['tipo'] == 'DECISÃO':
            cor, forma = '#FFF9C4', 'diamond' # Amarelo
        dot.node(attrs['id'], nome, shape=forma, fillcolor=cor)

    for conexao in conexoes:
        id_origem = etapas.get(conexao['origem'], {}).get('id')
        id_destino = etapas.get(conexao['destino'], {}).get('id')
        if id_origem and id_destino:
            dot.edge(id_origem, id_destino, label=conexao['rotulo'])

    return dot

# ==============================================================================
# INTERFACE DA APLICAÇÃO (Streamlit UI)
# ==============================================================================

st.title("🌿 Motor de Planejamento de Campanhas CRM")
st.markdown("Protótipo funcional para automatizar a estratégia, o planejamento e a criação de campanhas de CRM.")

# Inicialização do estado da sessão para guardar dados entre as páginas
if 'dados_carregados' not in st.session_state:
    st.session_state['dados_carregados'] = False
if 'df_perfis' not in st.session_state:
    st.session_state['df_perfis'] = None
if 'df_segmentado' not in st.session_state:
    st.session_state['df_segmentado'] = None

# --- Abas para simular o fluxo ---
tab1, tab2, tab3 = st.tabs(["📊 Fase 1: Fontes de Dados", "🧠 Fase 2: Processamento e Planejamento", "🚀 Fase 3: Outputs Finais"])

# ============================================================
# ABA 1: FONTES DE DADOS
# ============================================================
with tab1:
    st.header("Carregue as Fontes de Dados")
    st.markdown("Nesta etapa, fornecemos os insumos para os agentes inteligentes. Em produção, isso será feito via APIs.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dados Estruturados")
        uploaded_file = st.file_uploader("Carregue o arquivo de Perfil e Mensuração CB (CSV)", type="csv")
        if uploaded_file or st.session_state['df_perfis'] is not None:
            if uploaded_file:
                st.session_state['df_perfis'] = pd.read_csv(uploaded_file)
            st.success("Dados de perfil carregados com sucesso!")
            st.dataframe(st.session_state['df_perfis'].head())
        else:
            st.info("Aguardando arquivo CSV. O arquivo deve conter colunas como 'id_consultora', 'regiao', 'vendas_ultimo_ciclo', 'taxa_engajamento'.")

    with col2:
        st.subheader("Dados Não Estruturados")
        diretrizes_input = st.text_area("Cole aqui as Diretrizes de Comunicação", height=150, key="diretrizes")
        planos_input = st.text_area("Cole aqui os insights de Planejamentos Anteriores", height=150, key="planos")

    if st.button("▶️ Iniciar Processamento e Ir para a Fase 2", type="primary"):
        if st.session_state['df_perfis'] is None:
            st.error("Por favor, carregue o arquivo CSV de perfis antes de continuar.")
        else:
            st.session_state['dados_carregados'] = True
            st.success("Dados processados! Navegue para a Fase 2 para ver os resultados.")

# ============================================================
# ABA 2: PROCESSAMENTO E PLANEJAMENTO
# ============================================================
with tab2:
    if not st.session_state['dados_carregados']:
        st.warning("Por favor, carregue os dados na Fase 1 primeiro.")
    else:
        st.header("Outputs dos Agentes e Planejamento")
        
        # --- Outputs dos Agentes ---
        st.subheader("Resultados do Processamento Inicial")
        with st.expander("📄 Organizador de Contexto", expanded=True):
            resultado_organizador = simular_organizador_de_contexto(st.session_state.diretrizes, st.session_state.planos)
            st.markdown(resultado_organizador)
            
        with st.expander("📈 Especialista de Dados", expanded=True):
            resultado_especialista = simular_especialista_de_dados(st.session_state.df_perfis)
            st.markdown(resultado_especialista)
            
        st.divider()

        # --- Seletor de Público Interativo ---
        st.subheader("🎯 Seletor de Público (Interativo)")
        st.markdown("Use os filtros para segmentar a base de consultoras e definir o público da sua campanha.")
        
        df_para_filtrar = st.session_state.df_perfis.copy()
        
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            regioes_disponiveis = df_para_filtrar['regiao'].unique()
            regioes_selecionadas = st.multiselect("Filtrar por Região", regioes_disponiveis, default=regioes_disponiveis)
        
        with col_filtro2:
            max_vendas = int(df_para_filtrar['vendas_ultimo_ciclo'].max())
            filtro_vendas = st.slider("Filtrar por Vendas no Último Ciclo (R$)", 0, max_vendas, (0, max_vendas))

        # Aplicando os filtros
        df_filtrado = df_para_filtrar[
            (df_para_filtrar['regiao'].isin(regioes_selecionadas)) &
            (df_para_filtrar['vendas_ultimo_ciclo'].between(filtro_vendas[0], filtro_vendas[1]))
        ]
        
        st.metric(
            label="Quantidade de Pessoas na Segmentação",
            value=len(df_filtrado),
            delta=f"{len(df_filtrado) - len(df_para_filtrar)} em relação ao total"
        )
        st.dataframe(df_filtrado)
        
        if st.button("💾 Salvar Segmentação e Definir Lógica"):
            st.session_state['df_segmentado'] = df_filtrado
            st.success("Segmentação salva!")

        # --- Planejador de Campanhas ---
        if st.session_state['df_segmentado'] is not None:
            st.subheader("📝 Planejador de Campanhas de CRM")
            st.markdown("Descreva a lógica da sua campanha abaixo. Use as palavras-chave `INÍCIO`, `FIM`, `ETAPA`, `DECISÃO` e `CONEXÃO`.")
            
            exemplo_logica = """INÍCIO: Início da Campanha Q3
ETAPA: Enviar E-mail com Novidades Ekos
DECISÃO: Abriu o e-mail em 3 dias?
ETAPA: Enviar Cupom 20% via SMS
ETAPA: Adicionar à lista de "Alto Engajamento"
FIM: Fim do fluxo de sucesso
ETAPA: Ligar para reativar
FIM: Fim do fluxo de reativação

CONEXÃO: Início da Campanha Q3 -> Enviar E-mail com Novidades Ekos
CONEXÃO: Enviar E-mail com Novidades Ekos -> Abriu o e-mail em 3 dias?
CONEXÃO: Abriu o e-mail em 3 dias? -> Enviar Cupom 20% via SMS [Sim]
CONEXÃO: Enviar Cupom 20% via SMS -> Adicionar à lista de "Alto Engajamento"
CONEXÃO: Adicionar à lista de "Alto Engajamento" -> Fim do fluxo de sucesso
CONEXÃO: Abriu o e-mail em 3 dias? -> Ligar para reativar [Não]
CONEXÃO: Ligar para reativar -> Fim do fluxo de reativação
"""
            st.session_state['logica_campanha'] = st.text_area("Lógica da Campanha:", value=exemplo_logica, height=300)

# ============================================================
# ABA 3: OUTPUTS FINAIS
# ============================================================
with tab3:
    if 'logica_campanha' not in st.session_state or not st.session_state['logica_campanha']:
        st.warning("Por favor, defina e salve a segmentação e a lógica da campanha na Fase 2.")
    else:
        st.header("Geração dos Artefatos Finais da Campanha")

        if st.button("✨ Gerar Todos os Outputs da Campanha", type="primary", use_container_width=True):
            
            # --- 1. Fluxograma com estratégia ---
            st.subheader("1. Fluxograma com Estratégia de Audiência e Canais")
            try:
                fluxo_gerado = gerar_fluxograma_campanha("Protótipo_Streamlit", st.session_state.logica_campanha)
                st.graphviz_chart(fluxo_gerado)
                st.success("Fluxograma gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar o fluxograma: {e}")

            st.divider()

            # --- 2. Google Sheet com estratégia (simulação) ---
            st.subheader("2. Planilha com Estratégia de Audiência")
            st.markdown("Abaixo está a audiência final segmentada para a campanha. Clique para fazer o download.")
            
            df_final = st.session_state.df_segmentado
            st.dataframe(df_final)

            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="📥 Baixar Estratégia de Audiência (CSV)",
                data=convert_df_to_csv(df_final),
                file_name="estrategia_audiencia_campanha.csv",
                mime="text/csv",
            )
            
            st.divider()

            # --- 3. Orçamento e Cronograma (simulação) ---
            st.subheader("3. Orçamento e Cronograma (Simulação)")
            orcamento_data = {
                'Item': ['Disparos de E-mail', 'Disparos de SMS', 'Custo da Ligação (Call Center)'],
                'Quantidade': [len(df_final), len(df_final[df_final['taxa_engajamento'] > 50]), len(df_final[df_final['taxa_engajamento'] <= 50])],
                'Custo Unitário (R$)': [0.05, 0.15, 2.50],
            }
            df_orcamento = pd.DataFrame(orcamento_data)
            df_orcamento['Custo Total (R$)'] = df_orcamento['Quantidade'] * df_orcamento['Custo Unitário (R$)']
            st.table(df_orcamento)
            st.metric("Custo Total Estimado da Campanha", f"R$ {df_orcamento['Custo Total (R$)'].sum():.2f}")
            
            st.divider()

            # --- 4. Campanha desenhada no Salesforce (simulação) ---
            st.subheader("4. Campanha Desenhada no Salesforce (Simulação)")
            st.markdown("A etapa final seria a criação automática da campanha no Salesforce via API. O payload da requisição seria semelhante a este:")
            st.code(f"""
{{
  "campaign_name": "Campanha Q3 - Novidades Ekos",
  "target_audience_id": "lista_segmentada_{pd.Timestamp.now().strftime('%Y%m%d')}",
  "status": "Planned",
  "steps": [
    {{ "step": 1, "type": "email", "template_id": "template_ekos_novidades" }},
    {{ "step": 2, "type": "decision", "condition": "email_opened_in_3_days" }},
    {{ "step": 3, "type": "sms", "template_id": "sms_cupom_20" }},
    ...
  ]
}}
            """, language="json")