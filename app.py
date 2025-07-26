import streamlit as st
import pandas as pd
import yaml
import re
from io import StringIO
import base64
import graphviz # Reintroduzido para a visualização estável

# ==============================================================================
# FUNÇÕES DE INICIALIZAÇÃO, GERAÇÃO E PROCESSAMENTO
# ==============================================================================

def carregar_dados_iniciais():
    """Carrega valores iniciais na sessão, se ainda não existirem."""
    if 'df_perfis' not in st.session_state:
        st.session_state['df_perfis'] = pd.DataFrame() # Inicia vazio, espera o upload

    if 'diretrizes_cpb' not in st.session_state:
        st.session_state['diretrizes_cpb'] = "Tema do ciclo: Reconexão com a natureza. Mensagem: 'Redescubra sua essência com Ekos'."
    if 'insights_anteriores' not in st.session_state:
        st.session_state['insights_anteriores'] = "Análise: WhatsApp teve conversão 4,7% em recompra."
    
    if 'processo_yaml_str' not in st.session_state:
        st.session_state.processo_yaml_str = """
pools:
  pool_principal:
    name: Processo de Campanha
    processRef: Process_Main
    lanes:
      lane_estrategia: Estratégia
      lane_ativacao: Ativação

elements:
  - {id: start_event, name: Campanha Iniciada, type: startEvent, lane: lane_estrategia}
  - {id: task_segmentar, name: Segmentar Público, type: serviceTask, lane: lane_estrategia, content: 'Definir Cluster A e B.'}
  - {id: gw_fork, name: Disparar Canais, type: parallelGateway, lane: lane_ativacao}
  - {id: task_email, name: Enviar Email, type: serviceTask, lane: lane_ativacao, content: 'Mensagem para Cluster A.'}
  - {id: task_sms, name: Enviar SMS, type: serviceTask, lane: lane_ativacao, content: 'Mensagem para Cluster B.'}
  - {id: gw_join, name: Aguardar Disparos, type: parallelGateway, lane: lane_ativacao}
  - {id: end_event, name: Campanha Finalizada, type: endEvent, lane: lane_ativacao}

flows:
  - {id: f1, source: start_event, target: task_segmentar}
  - {id: f2, source: task_segmentar, target: gw_fork}
  - {id: f3, source: gw_fork, target: task_email}
  - {id: f4, source: gw_fork, target: task_sms}
  - {id: f5, source: task_email, target: gw_join}
  - {id: f6, source: task_sms, target: gw_join}
  - {id: f7, source: gw_join, target: end_event}
"""

def simular_organizador_de_contexto(diretrizes, insights):
    return f"""### Informações Relevantes:\n* **Tema:** {diretrizes.split(".")[0]}.\n* **Insight:** {insights.split(".")[0]}."""
def simular_especialista_de_dados(df):
    if df.empty: return "Carregue os dados para análise."
    media_vendas = df['vendas_ultimo_ciclo'].mean()
    return f"""### Direcional de Performance:\n* **Média de Vendas:** R$ {media_vendas:.2f}"""
def gerar_modelo_bpmn_xml_com_lanes(id_campanha, processo_yaml):
    collaboration_id=f"Collaboration_{id_campanha}";xml_parts=['<?xml version="1.0" encoding="UTF-8"?>','<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',f'  <bpmn:collaboration id="{collaboration_id}">']
    main_process_id = ""
    for pool_id,pool_data in processo_yaml.get('pools',{}).items():
        process_ref=pool_data['processRef'];
        if not main_process_id:main_process_id=process_ref
        xml_parts.append(f'    <bpmn:participant id="{pool_id}" name="{pool_data["name"]}" processRef="{process_ref}" />')
    xml_parts.append('  </bpmn:collaboration>')
    for pool_id,pool_data in processo_yaml.get('pools',{}).items():
        process_id=pool_data['processRef']
        xml_parts.append(f'  <bpmn:process id="{process_id}" isExecutable="true">');xml_parts.append('      <bpmn:laneSet>')
        for lane_id,lane_name in pool_data.get('lanes',{}).items():
            xml_parts.append(f'        <bpmn:lane id="{lane_id}" name="{lane_name}">')
            for el in processo_yaml.get('elements',[]):
                if el['lane']==lane_id:xml_parts.append(f'          <bpmn:flowNodeRef>{el["id"]}</bpmn:flowNodeRef>')
            xml_parts.append('        </bpmn:lane>')
        xml_parts.append('      </bpmn:laneSet>')
        for el in processo_yaml.get('elements',[]):
            if el['lane'] in pool_data.get('lanes',{}):
                el_id,el_name,el_type=el['id'],el['name'],el.get('type','task')
                doc_text=el.get('content','');doc_xml=f'<bpmn:documentation>{doc_text}</bpmn:documentation>' if doc_text else ''
                tag=el_type if 'Task' in el_type or 'Gateway' in el_type or 'Event' in el_type else 'task'
                xml_parts.append(f'    <bpmn:{tag} id="{el_id}" name="{el_name}">{doc_xml}</bpmn:{tag}>')
        for flow in processo_yaml.get('flows',[]):xml_parts.append(f'    <bpmn:sequenceFlow id="{flow["id"]}" name="{flow.get("name","")}" sourceRef="{flow["source"]}" targetRef="{flow["target"]}" />')
        xml_parts.append('  </bpmn:process>')
    xml_parts.append(f'<bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{collaboration_id}"></bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
    xml_parts.append('</bpmn:definitions>')
    return '\n'.join(xml_parts)

# ##############################################################################
# ATUALIZAÇÃO PRINCIPAL: A função de visualização volta a usar o Graphviz
# ##############################################################################
def gerar_visualizacao_com_graphviz(id_campanha, processo_yaml):
    """Gera uma visualização Graphviz com Pools e Lanes a partir de um YAML."""
    dot = graphviz.Digraph(graph_attr={'rankdir': 'LR', 'splines': 'ortho', 'compound': 'true', 'label': 'Visualização do Processo', 'fontsize': '20'})
    estilos_visuais = {
        'startEvent': {'shape': 'circle', 'style': 'filled', 'fillcolor': '#C8E6C9'},
        'endEvent': {'shape': 'doublecircle', 'style': 'filled', 'fillcolor': '#FFCDD2'},
        'serviceTask': {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#BBDEFB'},
        'userTask': {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#BBDEFB'},
        'exclusiveGateway': {'shape': 'diamond', 'style': 'filled', 'fillcolor': '#FFF9C4', 'label': 'X'},
        'parallelGateway': {'shape': 'diamond', 'style': 'filled', 'fillcolor': '#FFF9C4', 'label': '+'}
    }
    for pool_id, pool_data in processo_yaml.get('pools', {}).items():
        with dot.subgraph(name=f'cluster_{pool_id}') as p:
            p.attr(label=pool_data['name'], style='filled', color='lightgrey', fontcolor='black')
            for lane_id, lane_name in pool_data.get('lanes', {}).items():
                with p.subgraph(name=f'cluster_{lane_id}') as l:
                    l.attr(label=lane_name, style='rounded', color='black', fontcolor='black')
                    for el in processo_yaml.get('elements', []):
                        if el['lane'] == lane_id:
                            node_id, node_name, node_type = el['id'], el['name'], el.get('type', 'task')
                            estilo = estilos_visuais.get(node_type, {}).copy()
                            label = node_name if 'Gateway' not in node_type else estilo.pop('label', '')
                            l.node(node_id, label, **estilo)
    for flow in processo_yaml.get('flows', []):
        dot.edge(flow['source'], flow['target'], label=flow.get('name', ''))
    return dot

def processar_comando_chat(comando,yaml_str):
    try:
        data=yaml.safe_load(yaml_str);comando=comando.lower()
        match_nome=re.search(r"mude o nome da tarefa '(.+?)' para '(.+?)'",comando)
        if match_nome:
            id_tarefa,novo_nome=match_nome.groups();
            for el in data.get('elements',[]):
                if el['id']==id_tarefa:el['name']=novo_nome;
            return yaml.dump(data,sort_keys=False,indent=2),f"✅ Nome da tarefa '{id_tarefa}' alterado."
        return yaml_str,"❌ Comando não reconhecido."
    except yaml.YAMLError as e:return yaml_str,f"❌ Erro no formato do YAML: {e}"
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ==============================================================================
# INTERFACE DA APLICAÇÃO
# ==============================================================================
st.set_page_config(layout="wide")
st.title("Assistente de Planejamento de Campanhas CRM")
carregar_dados_iniciais()
tab1, tab2, tab3 = st.tabs(["**📊 Fase 1: Dados e Contexto**", "**⚙️ Fase 2: Análise e Segmentação**", "**✍️ Fase 3: Modelagem e Artefatos**"])
with tab1:
    st.header("Entrada de Dados da Campanha")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dados Estruturados")
        uploaded_file = st.file_uploader("Carregar arquivo de Consultoras (CSV)", type="csv")
        if uploaded_file is not None:
            try:
                st.session_state['df_perfis'] = pd.read_csv(uploaded_file); st.success("Novo arquivo carregado!")
            except Exception as e: st.error(f"Erro ao ler o arquivo: {e}")
        st.info("Amostra dos Dados Atuais")
        if not st.session_state.df_perfis.empty:
            st.dataframe(st.session_state['df_perfis'])
        else:
            st.warning("Nenhum dado carregado. Por favor, carregue um arquivo CSV.")
    with col2:
        st.subheader("Dados Não Estruturados")
        st.text_area("Diretrizes da Campanha (CPB):", height=120, key='diretrizes_cpb')
        st.text_area("Insights de Ciclos Anteriores:", height=120, key='insights_anteriores')
with tab2:
    st.header("Execução dos Agentes e Segmentação de Público")
    if st.session_state.df_perfis.empty:
        st.warning("Carregue os dados na Fase 1 para continuar.")
    else:
        st.subheader("Resultados dos Agentes de Análise")
        with st.expander("🤖 Agente: Organizador de Contexto", expanded=True):
            st.markdown(simular_organizador_de_contexto(st.session_state.diretrizes_cpb, st.session_state.insights_anteriores))
        with st.expander("🤖 Agente: Especialista de Dados", expanded=True):
            st.markdown(simular_especialista_de_dados(st.session_state.df_perfis))
        st.divider()
        st.subheader("🎯 Agente: Seletor de Público Interativo")
        df = st.session_state.df_perfis.copy(); col1, col2, col3 = st.columns(3)
        with col1: sel_regioes = st.multiselect("Região:", df['regiao'].unique(), default=df['regiao'].unique())
        with col2: sel_niveis = st.multiselect("Nível:", df['nivel_consultora'].unique(), default=df['nivel_consultora'].unique())
        with col3: max_vendas = int(df['vendas_ultimo_ciclo'].max()) if not df.empty else 1000; sel_vendas = st.slider("Vendas (R$):", 0, max_vendas, (0, max_vendas))
        df_filtrado = df[(df['regiao'].isin(sel_regioes))&(df['nivel_consultora'].isin(sel_niveis))&(df['vendas_ultimo_ciclo'].between(sel_vendas[0], sel_vendas[1]))]
        st.metric("Total no Segmento", len(df_filtrado)); st.dataframe(df_filtrado)
        if st.button("💾 Salvar Segmentação"):
            st.session_state['df_segmentado'] = df_filtrado; st.success(f"{len(df_filtrado)} consultoras salvas. Prossiga para a Fase 3.")
with tab3:
    st.header("Modelagem do Processo e Geração de Artefatos")
    if 'df_segmentado' not in st.session_state:
        st.warning("Crie e salve um segmento na Fase 2 primeiro.")
    else:
        st.success(f"Modelando a estratégia para o segmento de **{len(st.session_state['df_segmentado'])}** consultoras.")
        col1, col2 = st.columns([2, 3])
        with col1:
            st.subheader("Definição do Processo (YAML)")
            yaml_editor = st.text_area("Edite o processo:", value=st.session_state.processo_yaml_str, height=500, key="yaml_editor_main")
            st.session_state.processo_yaml_str = yaml_editor
            st.subheader("💬 Chat de Refinamento")
            comando = st.text_input("Seu comando:", placeholder="mude o nome da tarefa 'task_email' para 'Enviar Email Marketing'")
            if st.button("Executar Comando"):
                if comando:
                    novo_yaml, mensagem = processar_comando_chat(comando, st.session_state.processo_yaml_str)
                    st.session_state.processo_yaml_str = novo_yaml
                    if "✅" in mensagem: st.success(mensagem)
                    else: st.warning(mensagem)
                    st.rerun()
        with col2:
            st.subheader("Visualizador de Processo e Artefatos")
            try:
                processo_yaml_obj = yaml.safe_load(st.session_state.processo_yaml_str)
                # A visualização agora usa Graphviz
                visualizacao_dot = gerar_visualizacao_com_graphviz("campanha_natura", processo_yaml_obj)
                st.graphviz_chart(visualizacao_dot)
                
                st.divider()
                st.subheader("Downloads")
                modelo_xml = gerar_modelo_bpmn_xml_com_lanes("campanha_natura", processo_yaml_obj)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.download_button(label="📥 Baixar Modelo (.bpmn)", data=modelo_xml, file_name="processo_final.bpmn", mime="application/xml")
                with col_btn2:
                    csv_data = convert_df_to_csv(st.session_state['df_segmentado'])
                    st.download_button(label="📊 Baixar Audiência (.csv)", data=csv_data, file_name="audiencia_segmentada.csv", mime="text/csv")
                with st.expander("Ver código XML do modelo"): st.code(modelo_xml, language='xml')
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o modelo: {e}")