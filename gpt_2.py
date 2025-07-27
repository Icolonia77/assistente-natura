import streamlit as st
import pandas as pd
import yaml
import re
import graphviz

def carregar_dados_iniciais():
    if 'df_perfis' not in st.session_state:
        st.session_state['df_perfis'] = pd.DataFrame()
    if 'diretrizes_cpb' not in st.session_state:
        st.session_state['diretrizes_cpb'] = "Campanha CRM — Reconexão com o cliente."
    if 'insights_anteriores' not in st.session_state:
        st.session_state['insights_anteriores'] = "Última campanha: WhatsApp foi o canal com melhor recompra."
    if 'processo_yaml_str' not in st.session_state:
        st.session_state.processo_yaml_str = '''
pools:
  pool_crm:
    name: "Processo de Campanha CRM"
    processRef: Processo_Campanha
    lanes:
      lane_planejamento: "Planejamento"
      lane_aprovacao: "Aprovação"
      lane_execucao: "Execução"
      lane_notificacao: "Notificação"
      lane_mensuracao: "Mensuração"

elements:
  - id: start_event
    name: "Início do Processo"
    type: startEvent
    lane: lane_planejamento

  - id: reunir_equipa
    name: "Reunir equipe de planejamento"
    type: userTask
    lane: lane_planejamento
    content: "Convocar todos os envolvidos: dados, CRM, comunicação."

  - id: definir_objetivo
    name: "Definir objetivo da campanha"
    type: userTask
    lane: lane_planejamento
    content: "Exemplo: aumentar recompra de consultoras em 20%."

  - id: analisar_dados
    name: "Analisar base de dados"
    type: serviceTask
    lane: lane_planejamento
    content: "Avaliar histórico de vendas, engajamento e perfis."

  - id: segmentar_publico
    name: "Segmentar público-alvo"
    type: serviceTask
    lane: lane_planejamento
    content: "Segmentos: A=ativas, B=inativas, C=novas. Variáveis: região, vendas, engajamento."

  - id: planejar_canais
    name: "Planejar canais de comunicação"
    type: userTask
    lane: lane_planejamento
    content: "Selecionar canais: WhatsApp, Email, SMS, App Push."

  - id: elaborar_mensagens
    name: "Elaborar mensagens de campanha"
    type: userTask
    lane: lane_planejamento
    content: |
      WhatsApp:
        - Assunto: Oferta exclusiva Natura Ekos
        - Mensagem: "Olá, [Nome]! Aproveite 30% OFF em Ekos só até domingo. Responda SIM para receber seu link."
      Email:
        - Assunto: Reconexão Natura: Condição Especial para Você!
        - Mensagem: "Olá, [Nome], aproveite a oferta exclusiva da linha Ekos para clientes fiéis. Só até domingo! Clique aqui [link]"
      SMS:
        - Mensagem: "Natura: Oferta Ekos exclusiva! Clique no link: [link]"
      App Push:
        - Mensagem: "Oferta Ekos só até domingo! Confira no app."

  - id: gateway_aprovacao_estrategia
    name: "Estratégia aprovada?"
    type: exclusiveGateway
    lane: lane_aprovacao

  - id: ajustar_estrategia
    name: "Ajustar estratégia"
    type: userTask
    lane: lane_aprovacao
    content: "Exemplo de ajuste: trocar canal principal para WhatsApp."

  - id: gateway_aprovacao_mensagens
    name: "Mensagens aprovadas?"
    type: exclusiveGateway
    lane: lane_aprovacao

  - id: ajustar_mensagens
    name: "Ajustar mensagens"
    type: userTask
    lane: lane_aprovacao
    content: "Exemplo: mensagem WhatsApp ficou longa, refazer texto."

  - id: preparar_envio
    name: "Preparar envio de mensagens"
    type: serviceTask
    lane: lane_aprovacao
    content: "Upload dos contatos segmentados e revisão de horários."

  - id: paralela_envios
    name: "Disparar Canais em Paralelo"
    type: parallelGateway
    lane: lane_execucao

  - id: enviar_whatsapp
    name: "Enviar WhatsApp"
    type: serviceTask
    lane: lane_execucao
    content: |
      Modelo:
        - Assunto: Oferta exclusiva Natura Ekos
        - Mensagem: "Olá, [Nome]! Aproveite 30% OFF em Ekos só até domingo. Responda SIM para receber seu link."

  - id: enviar_email
    name: "Enviar Email"
    type: serviceTask
    lane: lane_execucao
    content: |
      Modelo:
        - Assunto: Reconexão Natura: Condição Especial para Você!
        - Corpo: "Olá, [Nome], aproveite a oferta exclusiva da linha Ekos para clientes fiéis. Só até domingo! Clique aqui [link]"

  - id: enviar_sms
    name: "Enviar SMS"
    type: serviceTask
    lane: lane_execucao
    content: |
      Modelo:
        - Mensagem: "Natura: Oferta Ekos exclusiva! Clique no link: [link]"

  - id: enviar_push
    name: "Enviar App Push"
    type: serviceTask
    lane: lane_execucao
    content: |
      Modelo:
        - Mensagem: "Oferta Ekos só até domingo! Confira no app."

  - id: juntar_envios
    name: "Aguardar envios"
    type: parallelGateway
    lane: lane_execucao

  - id: monitorar_envio
    name: "Monitorar entregabilidade"
    type: serviceTask
    lane: lane_execucao
    content: "Acompanhar status de envio, entregas, erros."

  - id: tratar_erros
    name: "Tratar erros de envio"
    type: userTask
    lane: lane_execucao
    content: "Exemplo: Email com bounce > reenviar por SMS."

  - id: notificar_time
    name: "Notificar equipe de resultado parcial"
    type: userTask
    lane: lane_notificacao
    content: |
      Modelo:
        - Email para equipe:
            Assunto: Resultado Parcial Campanha CRM
            Corpo: "A campanha atingiu 65% da meta até o momento. Acompanhe o dashboard para mais detalhes."

  - id: coletar_resultados
    name: "Coletar resultados dos canais"
    type: serviceTask
    lane: lane_mensuracao
    content: "KPIs: Taxa abertura, clique, resposta WhatsApp, vendas."

  - id: analisar_resultados
    name: "Analisar performance final"
    type: userTask
    lane: lane_mensuracao
    content: "Comparar metas vs. resultados e gerar relatório."

  - id: feedback_loop
    name: "Reunião de lições aprendidas"
    type: userTask
    lane: lane_mensuracao
    content: "Checklist: o que funcionou, oportunidades de melhoria, próximos passos."

  - id: end_event
    name: "Campanha finalizada"
    type: endEvent
    lane: lane_mensuracao

flows:
  - id: f1
    source: start_event
    target: reunir_equipa
  - id: f2
    source: reunir_equipa
    target: definir_objetivo
  - id: f3
    source: definir_objetivo
    target: analisar_dados
  - id: f4
    source: analisar_dados
    target: segmentar_publico
  - id: f5
    source: segmentar_publico
    target: planejar_canais
  - id: f6
    source: planejar_canais
    target: elaborar_mensagens
  - id: f7
    source: elaborar_mensagens
    target: gateway_aprovacao_estrategia
  - id: f8
    source: gateway_aprovacao_estrategia
    target: ajustar_estrategia
    name: "Não"
  - id: f9
    source: ajustar_estrategia
    target: definir_objetivo
  - id: f10
    source: gateway_aprovacao_estrategia
    target: gateway_aprovacao_mensagens
    name: "Sim"
  - id: f11
    source: gateway_aprovacao_mensagens
    target: ajustar_mensagens
    name: "Não"
  - id: f12
    source: ajustar_mensagens
    target: elaborar_mensagens
  - id: f13
    source: gateway_aprovacao_mensagens
    target: preparar_envio
    name: "Sim"
  - id: f14
    source: preparar_envio
    target: paralela_envios
  - id: f15
    source: paralela_envios
    target: enviar_whatsapp
  - id: f16
    source: paralela_envios
    target: enviar_email
  - id: f17
    source: paralela_envios
    target: enviar_sms
  - id: f18
    source: paralela_envios
    target: enviar_push
  - id: f19
    source: enviar_whatsapp
    target: juntar_envios
  - id: f20
    source: enviar_email
    target: juntar_envios
  - id: f21
    source: enviar_sms
    target: juntar_envios
  - id: f22
    source: enviar_push
    target: juntar_envios
  - id: f23
    source: juntar_envios
    target: monitorar_envio
  - id: f24
    source: monitorar_envio
    target: tratar_erros
  - id: f25
    source: tratar_erros
    target: coletar_resultados
  - id: f26
    source: monitorar_envio
    target: notificar_time
  - id: f27
    source: notificar_time
    target: coletar_resultados
  - id: f28
    source: coletar_resultados
    target: analisar_resultados
  - id: f29
    source: analisar_resultados
    target: feedback_loop
  - id: f30
    source: feedback_loop
    target: end_event
'''

def simular_organizador_de_contexto(diretrizes, insights):
    return f"""### Informações Relevantes:\n* **Tema:** {diretrizes}\n* **Insight:** {insights}"""

def simular_especialista_de_dados(df):
    if df.empty:
        return "Carregue os dados para análise."
    else:
        st.markdown("#### 📋 Amostra dos dados (5 primeiras linhas):")
        st.dataframe(df.head(5))
        try:
            media_vendas = df['vendas_ultimo_ciclo'].mean()
            st.markdown(f"- **Média de vendas último ciclo:** R$ {media_vendas:.2f}")
        except Exception:
            pass
        return ""

def gerar_modelo_bpmn_xml_com_lanes(id_campanha, processo_yaml):
    collaboration_id = f"Collaboration_{id_campanha}"
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',
                 f'  <bpmn:collaboration id="{collaboration_id}">']
    main_process_id = ""
    for pool_id, pool_data in processo_yaml.get('pools', {}).items():
        process_ref = pool_data['processRef']
        if not main_process_id: main_process_id = process_ref
        xml_parts.append(f'    <bpmn:participant id="{pool_id}" name="{pool_data["name"]}" processRef="{process_ref}" />')
    xml_parts.append('  </bpmn:collaboration>')
    for pool_id, pool_data in processo_yaml.get('pools', {}).items():
        process_id = pool_data['processRef']
        xml_parts.append(f'  <bpmn:process id="{process_id}" isExecutable="true">')
        xml_parts.append('      <bpmn:laneSet>')
        for lane_id, lane_name in pool_data.get('lanes', {}).items():
            xml_parts.append(f'        <bpmn:lane id="{lane_id}" name="{lane_name}">')
            for el in processo_yaml.get('elements', []):
                if el['lane'] == lane_id:
                    xml_parts.append(f'          <bpmn:flowNodeRef>{el["id"]}</bpmn:flowNodeRef>')
            xml_parts.append('        </bpmn:lane>')
        xml_parts.append('      </bpmn:laneSet>')
        for el in processo_yaml.get('elements', []):
            if el['lane'] in pool_data.get('lanes', {}):
                el_id, el_name, el_type = el['id'], el['name'], el.get('type', 'task')
                doc_text = el.get('content', '')
                doc_xml = f'<bpmn:documentation>{doc_text}</bpmn:documentation>' if doc_text else ''
                tag = el_type if 'Task' in el_type or 'Gateway' in el_type or 'Event' in el_type or 'CatchEvent' in el_type or 'ThrowEvent' in el_type else 'task'
                xml_parts.append(f'    <bpmn:{tag} id="{el_id}" name="{el_name}">{doc_xml}</bpmn:{tag}>')
        for flow in processo_yaml.get('flows', []):
            xml_parts.append(f'    <bpmn:sequenceFlow id="{flow["id"]}" name="{flow.get("name", "")}" sourceRef="{flow["source"]}" targetRef="{flow["target"]}" />')
        xml_parts.append('  </bpmn:process>')
    xml_parts.append(f'<bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{collaboration_id}"></bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
    xml_parts.append('</bpmn:definitions>')
    return '\n'.join(xml_parts)

def gerar_visualizacao_com_graphviz(id_campanha, processo_yaml):
    dot = graphviz.Digraph(graph_attr={'rankdir': 'LR', 'splines': 'ortho', 'compound': 'true', 'label': 'Processo BPMN — Campanha CRM', 'fontsize': '16'})
    estilos_visuais = {
        'startEvent': {'shape': 'circle', 'style': 'filled', 'fillcolor': '#C8E6C9'},
        'endEvent': {'shape': 'doublecircle', 'style': 'filled', 'fillcolor': '#FFCDD2'},
        'serviceTask': {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#BBDEFB'},
        'userTask': {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#D1C4E9'},
        'exclusiveGateway': {'shape': 'diamond', 'style': 'filled', 'fillcolor': '#FFF9C4', 'label': 'X'},
        'parallelGateway': {'shape': 'diamond', 'style': 'filled', 'fillcolor': '#FFE082', 'label': '+'}
    }
    for pool_id, pool_data in processo_yaml.get('pools', {}).items():
        with dot.subgraph(name=f'cluster_{pool_id}') as p:
            p.attr(label=pool_data['name'], style='filled', color='lightgrey')
            for lane_id, lane_name in pool_data.get('lanes', {}).items():
                with p.subgraph(name=f'cluster_{lane_id}') as l:
                    l.attr(label=lane_name, style='rounded', color='black')
                    for el in processo_yaml.get('elements', []):
                        if el['lane'] == lane_id:
                            node_id, node_name, node_type = el['id'], el['name'], el.get('type', 'task')
                            estilo = estilos_visuais.get(node_type, {}).copy()
                            label = node_name if 'Gateway' not in node_type else estilo.pop('label', '')
                            if el.get('content'):
                                label += "\n📝 " + el['content'][:60] + ("..." if len(el['content']) > 60 else "")
                            l.node(node_id, label, **estilo)
    for flow in processo_yaml.get('flows', []):
        dot.edge(flow['source'], flow['target'], label=flow.get('name', ''))
    return dot

def processar_comando_chat(comando, yaml_str):
    try:
        data = yaml.safe_load(yaml_str)
        comando = comando.lower()
        match_nome = re.search(r"mude o nome da tarefa '(.+?)' para '(.+?)'", comando)
        if match_nome:
            id_tarefa, novo_nome = match_nome.groups()
            for el in data.get('elements', []):
                if el['id'] == id_tarefa:
                    el['name'] = novo_nome
            return yaml.dump(data, sort_keys=False, indent=2), f"✅ Nome da tarefa '{id_tarefa}' alterado."
        return yaml_str, "❌ Comando não reconhecido."
    except yaml.YAMLError as e:
        return yaml_str, f"❌ Erro no formato do YAML: {e}"

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ==============================================================================
# INTERFACE
# ==============================================================================

st.set_page_config(layout="wide")
st.title("Assistente de Planejamento de Campanhas CRM — BPMN 2.0 Robusto")

carregar_dados_iniciais()
if 'processamento_iniciado' not in st.session_state:
    st.session_state['processamento_iniciado'] = False

tab1, tab2, tab3 = st.tabs(["**📊 Fase 1: Dados e Contexto**", "**⚙️ Fase 2: Análise e Segmentação**", "**✍️ Fase 3: Modelagem e Artefatos**"])

with tab1:
    st.header("Entrada de Dados da Campanha")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dados Estruturados")
        uploaded_file = st.file_uploader("Carregar arquivo de Consultoras (CSV)", type="csv")
        if uploaded_file is not None:
            try:
                st.session_state['df_perfis'] = pd.read_csv(uploaded_file)
                st.success("Novo arquivo carregado!")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")
        st.info("Amostra dos Dados Atuais")
        if not st.session_state.df_perfis.empty:
            st.dataframe(st.session_state['df_perfis'])
        else:
            st.warning("Nenhum dado carregado. Prossiga para o fluxo BPMN.")
    with col2:
        st.subheader("Dados Não Estruturados")
        st.text_area("Diretrizes da Campanha (CPB):", height=100, key='diretrizes_cpb')
        st.text_area("Insights de Ciclos Anteriores:", height=100, key='insights_anteriores')
    st.markdown("---")
    if st.button("🚦 Iniciar Processamento"):
        st.session_state['processamento_iniciado'] = True
        st.success("Processamento iniciado! Agora acesse as próximas fases.")
    elif not st.session_state['processamento_iniciado']:
        st.info("Preencha todos os dados e clique em **Iniciar Processamento** para liberar as próximas fases.")

with tab2:
    if not st.session_state['processamento_iniciado']:
        st.warning("Preencha e clique em **Iniciar Processamento** na Fase 1 para liberar esta etapa.")
    else:
        st.header("Execução dos Agentes e Segmentação de Público")
        st.subheader("Resultados dos Agentes de Análise")
        with st.expander("🤖 Agente: Organizador de Contexto", expanded=True):
            st.markdown(simular_organizador_de_contexto(st.session_state.diretrizes_cpb, st.session_state.insights_anteriores))
        with st.expander("🤖 Agente: Especialista de Dados", expanded=True):
            _ = simular_especialista_de_dados(st.session_state.df_perfis)
        st.divider()
        st.subheader("🎯 Agente: Seletor de Público Interativo")
        if st.session_state.df_perfis.empty:
            st.warning("Nenhum dado carregado, simulação não realizada. Carregue um CSV.")
        else:
            df = st.session_state.df_perfis.copy()
            col1, col2, col3 = st.columns(3)
            with col1:
                sel_regioes = st.multiselect("Região:", df['regiao'].unique(), default=df['regiao'].unique())
            with col2:
                sel_niveis = st.multiselect("Nível:", df['nivel_consultora'].unique(), default=df['nivel_consultora'].unique())
            with col3:
                max_vendas = int(df['vendas_ultimo_ciclo'].max()) if not df.empty else 1000
                sel_vendas = st.slider("Vendas (R$):", 0, max_vendas, (0, max_vendas))
            df_filtrado = df[
                (df['regiao'].isin(sel_regioes)) &
                (df['nivel_consultora'].isin(sel_niveis)) &
                (df['vendas_ultimo_ciclo'].between(sel_vendas[0], sel_vendas[1]))
            ]
            st.metric("Total no Segmento", len(df_filtrado))
            st.dataframe(df_filtrado)
            if st.button("💾 Salvar Segmentação"):
                st.session_state['df_segmentado'] = df_filtrado
                st.success(f"{len(df_filtrado)} consultoras salvas. Prossiga para a Fase 3.")

with tab3:
    if not st.session_state['processamento_iniciado']:
        st.warning("Preencha e clique em **Iniciar Processamento** na Fase 1 para liberar esta etapa.")
    else:
        st.header("Modelagem do Processo BPMN 2.0 — Campanha CRM")
        col1, col2 = st.columns([2, 3])
        with col1:
            st.subheader("Definição do Processo (YAML)")
            yaml_editor = st.text_area("Edite o processo:", value=st.session_state.processo_yaml_str, height=650, key="yaml_editor_main")
            st.session_state.processo_yaml_str = yaml_editor
            st.subheader("💬 Chat de Refinamento")
            comando = st.text_input("Seu comando:", placeholder="mude o nome da tarefa 'enviar_email' para 'Disparar Email'")
            if st.button("Executar Comando"):
                if comando:
                    novo_yaml, mensagem = processar_comando_chat(comando, st.session_state.processo_yaml_str)
                    st.session_state.processo_yaml_str = novo_yaml
                    if "✅" in mensagem:
                        st.success(mensagem)
                    else:
                        st.warning(mensagem)
                    st.rerun()
        with col2:
            st.subheader("Visualizador BPMN e Artefatos")
            try:
                processo_yaml_obj = yaml.safe_load(st.session_state.processo_yaml_str)
                visualizacao_dot = gerar_visualizacao_com_graphviz("campanha_crm", processo_yaml_obj)
                st.graphviz_chart(visualizacao_dot)
                st.divider()
                st.subheader("Downloads")
                modelo_xml = gerar_modelo_bpmn_xml_com_lanes("campanha_crm", processo_yaml_obj)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.download_button(label="📥 Baixar Modelo (.bpmn)", data=modelo_xml, file_name="processo_crm.bpmn", mime="application/xml")
                with col_btn2:
                    csv_data = convert_df_to_csv(st.session_state['df_perfis'])
                    st.download_button(label="📊 Baixar Audiência (.csv)", data=csv_data, file_name="audiencia_segmentada.csv", mime="text/csv")
                with st.expander("Ver código XML do modelo"):
                    st.code(modelo_xml, language='xml')
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o modelo: {e}")

# FIM
