import streamlit as st
import pandas as pd
import graphviz
import re
from io import StringIO

# ==============================================================================
# FUNÇÕES DE SIMULAÇÃO (Inalteradas)
# ==============================================================================
def simular_organizador_de_contexto(diretrizes, planos_anteriores):
    if not diretrizes and not planos_anteriores: return "Aguardando input..."
    info = "### Informações de Negócio Relevantes\n\n"
    if diretrizes: info += f"**Diretrizes:**\n- Foco em sustentabilidade e inovação.\n"
    if planos_anteriores: info += f"**Aprendizados:**\n- SMS tem alta conversão para o público jovem.\n"
    return info

def simular_especialista_de_dados(df):
    if df is None: return "Aguardando carregamento dos dados..."
    media_vendas = df['vendas_ultimo_ciclo'].mean()
    media_engajamento = df['taxa_engajamento'].mean()
    direcional = f"### Direcional de Performance\n- **Média de Vendas:** R$ {media_vendas:.2f}\n- **Média de Engajamento:** {media_engajamento:.1f}%"
    return direcional

# ##############################################################################
# ATUALIZAÇÃO FINAL E DEFINITIVA: REMOÇÃO DA BIBLIOTECA EXTERNA
# E CRIAÇÃO DE UMA FUNÇÃO DE GERAÇÃO DE XML NATIVA
# ##############################################################################
def gerar_modelo_bpmn_xml(id_campanha, etapas, conexoes):
    """Gera uma string XML de um modelo BPMN 2.0 válido."""
    process_id = f"Process_{id_campanha}"
    
    # Cabeçalho padrão do XML BPMN
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',
        f'  <bpmn:process id="{process_id}" isExecutable="false">'
    ]

    # Dicionário para mapear nomes de etapas para IDs BPMN
    element_map = {nome: f"bpmn_{attrs['id']}" for nome, attrs in etapas.items()}

    # Adicionar elementos do processo (eventos, tarefas, gateways)
    for nome, attrs in etapas.items():
        bpmn_id = element_map[nome]
        tipo = attrs.get('tipo', 'ETAPA')
        if tipo == 'INÍCIO':
            xml_parts.append(f'    <bpmn:startEvent id="{bpmn_id}" name="{nome}" />')
        elif tipo == 'FIM':
            xml_parts.append(f'    <bpmn:endEvent id="{bpmn_id}" name="{nome}" />')
        elif tipo == 'DECISÃO':
            xml_parts.append(f'    <bpmn:exclusiveGateway id="{bpmn_id}" name="{nome}" />')
        else: # ETAPA
            xml_parts.append(f'    <bpmn:task id="{bpmn_id}" name="{nome}" />')

    # Adicionar fluxos de sequência (conexões)
    for i, conexao in enumerate(conexoes):
        origem_id = element_map.get(conexao['origem'])
        destino_id = element_map.get(conexao['destino'])
        if origem_id and destino_id:
            flow_id = f"Flow_{i}"
            nome_fluxo = conexao.get('rotulo', '')
            xml_parts.append(f'    <bpmn:sequenceFlow id="{flow_id}" name="{nome_fluxo}" sourceRef="{origem_id}" targetRef="{destino_id}" />')

    xml_parts.append('  </bpmn:process>')
    
    # Adicionar a parte de diagrama (BPMNDI) para visualização
    xml_parts.append(f'  <bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{process_id}">')
    x, y = 150, 200
    for nome, attrs in etapas.items():
        bpmn_id = element_map[nome]
        tipo = attrs.get('tipo', 'ETAPA')
        height, width = (36, 36) if tipo in ['INÍCIO', 'FIM'] else (50, 50) if tipo == 'DECISÃO' else (80, 100)
        xml_parts.append(f'    <bpmndi:BPMNShape id="{bpmn_id}_di" bpmnElement="{bpmn_id}"><dc:Bounds x="{x}" y="{y - height/2}" width="{width}" height="{height}" /></bpmndi:BPMNShape>')
        x += 180
    
    for i, conexao in enumerate(conexoes):
        origem_id = element_map.get(conexao['origem'])
        destino_id = element_map.get(conexao['destino'])
        if origem_id and destino_id:
            flow_id = f"Flow_{i}"
            xml_parts.append(f'    <bpmndi:BPMNEdge id="{flow_id}_di" bpmnElement="{flow_id}"><di:waypoint x="0" y="0" /><di:waypoint x="0" y="0" /></bpmndi:BPMNEdge>')
            
    xml_parts.append('  </bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
    xml_parts.append('</bpmn:definitions>')
    
    return '\n'.join(xml_parts)

def gerar_visualizacao_bpmn(id_campanha, etapas, conexoes):
    """Gera um objeto Graphviz para visualização no Streamlit."""
    dot = graphviz.Digraph(f'visualizacao_{id_campanha}', graph_attr={'rankdir': 'LR', 'splines': 'ortho', 'bgcolor': 'transparent'})
    estilos_visuais = {
        'INÍCIO': {'shape': 'circle', 'style': 'filled', 'fillcolor': '#C8E6C9', 'penwidth': '1.5'},
        'FIM': {'shape': 'doublecircle', 'style': 'filled', 'fillcolor': '#FFCDD2', 'penwidth': '2'},
        'ETAPA': {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#BBDEFB'},
        'DECISÃO': {'shape': 'diamond', 'style': 'filled', 'fillcolor': '#FFF9C4', 'width': '1.5', 'height': '1.5'},
        'DEFAULT': {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#E0E0E0'}
    }
    for nome, attrs in etapas.items():
        dot.node(attrs['id'], nome, **estilos_visuais.get(attrs['tipo'], estilos_visuais['DEFAULT']))
    for conexao in conexoes:
        id_origem, id_destino = etapas.get(conexao['origem'], {}).get('id'), etapas.get(conexao['destino'], {}).get('id')
        if id_origem and id_destino:
            dot.edge(id_origem, id_destino, label=conexao['rotulo'])
    return dot

# ==============================================================================
# INTERFACE DA APLICAÇÃO
# ==============================================================================
st.title("🌿 Motor de Planejamento de Campanhas CRM")
st.markdown("Protótipo funcional para automatizar a estratégia, o planejamento e a criação de campanhas de CRM.")

if 'dados_carregados' not in st.session_state: st.session_state['dados_carregados'] = False
if 'df_perfis' not in st.session_state: st.session_state['df_perfis'] = None
if 'df_segmentado' not in st.session_state: st.session_state['df_segmentado'] = None

tab1, tab2, tab3 = st.tabs(["📊 Fase 1: Fontes de Dados", "🧠 Fase 2: Processamento e Planejamento", "🚀 Fase 3: Outputs Finais"])

with tab1:
    # O código da Aba 1 permanece o mesmo
    st.header("Carregue as Fontes de Dados"); col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dados Estruturados"); uploaded_file = st.file_uploader("Carregue o arquivo de Perfil e Mensuração CB (CSV)", type="csv")
        if uploaded_file or st.session_state['df_perfis'] is not None:
            if uploaded_file: st.session_state['df_perfis'] = pd.read_csv(uploaded_file)
            st.success("Dados de perfil carregados com sucesso!"); st.dataframe(st.session_state['df_perfis'].head())
    with col2:
        st.subheader("Dados Não Estruturados"); diretrizes_input = st.text_area("Cole aqui as Diretrizes de Comunicação", height=150, key="diretrizes"); planos_input = st.text_area("Cole aqui os insights de Planejamentos Anteriores", height=150, key="planos")
    if st.button("▶️ Iniciar Processamento", type="primary"):
        if st.session_state['df_perfis'] is None: st.error("Por favor, carregue o arquivo CSV.")
        else: st.session_state['dados_carregados'] = True; st.success("Dados processados!")

with tab2:
    # O código da Aba 2 permanece o mesmo
    if not st.session_state['dados_carregados']: st.warning("Por favor, carregue os dados na Fase 1 primeiro.")
    else:
        st.header("Processamento e Planejamento"); 
        with st.expander("📄 Organizador de Contexto", expanded=True): st.markdown(simular_organizador_de_contexto(st.session_state.diretrizes, st.session_state.planos))
        with st.expander("📈 Especialista de Dados", expanded=True): st.markdown(simular_especialista_de_dados(st.session_state.df_perfis))
        st.divider(); st.subheader("🎯 Seletor de Público"); df_para_filtrar = st.session_state.df_perfis.copy(); col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1: regioes_disponiveis = df_para_filtrar['regiao'].unique(); regioes_selecionadas = st.multiselect("Filtrar por Região", regioes_disponiveis, default=regioes_disponiveis)
        with col_filtro2: max_vendas = int(df_para_filtrar['vendas_ultimo_ciclo'].max()); filtro_vendas = st.slider("Filtrar por Vendas (R$)", 0, max_vendas, (0, max_vendas))
        df_filtrado = df_para_filtrar[(df_para_filtrar['regiao'].isin(regioes_selecionadas)) & (df_para_filtrar['vendas_ultimo_ciclo'].between(filtro_vendas[0], filtro_vendas[1]))]
        st.metric(label="Pessoas na Segmentação", value=len(df_filtrado)); st.dataframe(df_filtrado)
        if st.button("💾 Salvar Segmentação"): st.session_state['df_segmentado'] = df_filtrado; st.success("Segmentação salva!")
        if st.session_state['df_segmentado'] is not None:
            st.subheader("📝 Planejador de Campanhas"); exemplo_logica = "INÍCIO: Início Campanha\nETAPA: Enviar E-mail\nDECISÃO: Abriu?\nETAPA: Enviar SMS [Sim]\nFIM: Fim Sucesso\nETAPA: Ligar [Não]\nFIM: Fim Falha\n\nCONEXÃO: Início Campanha -> Enviar E-mail\nCONEXÃO: Enviar E-mail -> Abriu?\nCONEXÃO: Abriu? -> Enviar SMS [Sim]\nCONEXÃO: Enviar SMS -> Fim Sucesso\nCONEXÃO: Abriu? -> Ligar [Não]\nCONEXÃO: Ligar -> Fim Falha"
            st.session_state['logica_campanha'] = st.text_area("Lógica da Campanha:", value=exemplo_logica, height=250)

with tab3:
    # O código da Aba 3 foi ajustado para usar as novas funções
    st.header("Geração dos Artefatos Finais")
    if 'logica_campanha' not in st.session_state or not st.session_state['logica_campanha']: st.warning("Defina a lógica da campanha na Fase 2.")
    else:
        if st.button("✨ Gerar Todos os Outputs", type="primary", use_container_width=True):
            try:
                # Parsear a lógica uma vez
                etapas, conexoes = {}, []
                for i, linha in enumerate(st.session_state.logica_campanha.strip().split('\n')):
                    linha = linha.strip();
                    if not linha: continue;
                    tipo_match = re.match(r"(\w+):(.+)", linha);
                    conexao_match = re.match(r"CONEXÃO:\s*(.+?)\s*->\s*(.+?)(?:\s*\[(.+?)\])?", linha)
                    if conexao_match: orig, dest, rot = conexao_match.groups(); conexoes.append({'origem': orig.strip(), 'destino': dest.strip(), 'rotulo': rot.strip() if rot else ''})
                    elif tipo_match: tipo, nome = tipo_match.groups(); etapas[nome.strip()] = {'tipo': tipo.strip().upper(), 'id': f'id_{i}'}

                # Gerar os dois outputs
                visualizacao_dot = gerar_visualizacao_bpmn("campanha_natura", etapas, conexoes)
                modelo_xml = gerar_modelo_bpmn_xml("campanha_natura", etapas, conexoes)
                
                st.subheader("1. Visualização do Processo (Estilo BPMN)"); st.graphviz_chart(visualizacao_dot)
                st.subheader("2. Modelo de Processo BPMN 2.0 (para Salesforce)"); st.success("Arquivo .bpmn gerado com sucesso!")
                st.download_button(label="📥 Baixar Arquivo BPMN (.bpmn)", data=modelo_xml, file_name="processo_campanha.bpmn", mime="application/xml")
                with st.expander("Ver código XML do modelo"): st.code(modelo_xml, language='xml')
                st.divider()
                st.subheader("3. Planilha com Estratégia de Audiência"); st.dataframe(st.session_state.df_segmentado)
            except Exception as e: st.error(f"Ocorreu um erro: {e}")