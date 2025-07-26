


import streamlit as st
import pandas as pd
import yaml
import re
from io import StringIO
import base64

# ==============================================================================
# DADOS SINTÉTICOS E EXEMPLO YAML (CARREGADOS NA INICIALIZAÇÃO)
# ==============================================================================
def carregar_dados_iniciais():
    """Carrega todos os dados da demonstração na sessão do Streamlit."""
    if 'df_perfis' not in st.session_state:
        csv_data = """id_consultora,nome_consultora,regiao,nivel_consultora,meses_de_casa,vendas_ultimo_ciclo,taxa_engajamento,categoria_preferida
2001,Ana Silva,Sudeste,Ouro,24,2850.50,92,Perfumaria
2002,Bruno Costa,Nordeste,Prata,12,1550.00,65,Cuidados Diários
2003,Carla Dias,Sudeste,Diamante,36,4100.75,98,Maquegem
2004,Daniel Farias,Norte,Semente,3,450.20,25,Cuidados Diários
"""
        st.session_state['df_perfis'] = pd.read_csv(StringIO(csv_data))
    if 'diretrizes_cpb' not in st.session_state:
        st.session_state['diretrizes_cpb'] = "Tema do ciclo: Reconexão com a natureza e os sentidos. Mensagem central: 'Redescubra sua essência com Ekos'. Objetivo: Aumentar recompra da linha Ekos em 20%."
    if 'insights_anteriores' not in st.session_state:
        st.session_state['insights_anteriores'] = "Análise do ciclo anterior: WhatsApp teve conversão 4,7% em recompra. ROI da linha Ekos foi de 5,3x. Consultoras com mais de 3 interações convertem 2,4x mais."
    if 'processo_yaml_str' not in st.session_state:
        st.session_state.processo_yaml_str = """
pools:
  pool_ciclo_11:
    name: Campanha Ekos Essência da Amazônia
    processRef: Process_Ekos
    lanes:
      lane_estrategia: Estratégia e Análise
      lane_ativacao: Ativação de Canais
      lane_stakeholders: Validação
elements:
  - {id: start_ciclo, name: Início do Ciclo 11/2025, type: startEvent, lane: lane_estrategia, content: 'Planejamento de CRM.'}
  - {id: task_segmentar, name: Definir Segmentos, type: serviceTask, lane: lane_estrategia, content: 'Cluster 1 (Frequentes) e Cluster 2 (Reativáveis)'}
  - {id: gw_paralelo_inicio, name: Iniciar Ativação, type: parallelGateway, lane: lane_ativacao}
  - {id: task_app, name: Disparar Push no App, type: serviceTask, lane: lane_ativacao, content: 'Cluster 1 → Mensagem A'}
  - {id: task_whatsapp, name: Disparar WhatsApp, type: serviceTask, lane: lane_ativacao, content: 'Cluster 2 → Mensagem B'}
  - {id: gw_paralelo_fim, name: Aguardar Disparos, type: parallelGateway, lane: lane_ativacao}
  - {id: task_validar, name: Validar com Stakeholders, type: userTask, lane: lane_stakeholders, content: 'Ajuste: Incluir opt-out.'}
  - {id: end_campanha, name: Fim do Planejamento, type: endEvent, lane: lane_stakeholders}
flows:
  - {id: f1, source: start_ciclo, target: task_segmentar}
  - {id: f2, source: task_segmentar, target: gw_paralelo_inicio}
  - {id: f3, source: gw_paralelo_inicio, target: task_app}
  - {id: f4, source: gw_paralelo_inicio, target: task_whatsapp}
  - {id: f5, source: task_app, target: gw_paralelo_fim}
  - {id: f6, source: task_whatsapp, target: gw_paralelo_fim}
  - {id: f7, source: gw_paralelo_fim, target: task_validar}
  - {id: f8, source: task_validar, target: end_campanha}
"""

# ==============================================================================
# FUNÇÕES DOS AGENTES E DE GERAÇÃO
# ==============================================================================
def simular_organizador_de_contexto(diretrizes, insights):
    return f"""### Informações de Negócio Relevantes:\n* **Tema do ciclo:** {diretrizes.split(".")[0]}.\n* **Mensagem central:** {diretrizes.split(".")[1]}.\n* **Canal Prioritário (Insight):** {insights.split(".")[0]}."""
def simular_especialista_de_dados(df):
    media_vendas = df['vendas_ultimo_ciclo'].mean(); media_engajamento = df['taxa_engajamento'].mean()
    return f"""### Direcional de Performance Detalhado:\n* **Média de Vendas (Base Atual):** R$ {media_vendas:.2f}\n* **Média de Engajamento (Base Atual):** {media_engajamento:.1f}%"""

def gerar_modelo_bpmn_xml_com_lanes(id_campanha, processo_yaml):
    # Função de geração de XML (sem alterações)
    collaboration_id = f"Collaboration_{id_campanha}"; xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',
        f'  <bpmn:collaboration id="{collaboration_id}">'
    ]
    main_process_id = ""
    for pool_id, pool_data in processo_yaml.get('pools', {}).items():
        process_ref = pool_data['processRef'];
        if not main_process_id: main_process_id = process_ref
        xml_parts.append(f'    <bpmn:participant id="{pool_id}" name="{pool_data["name"]}" processRef="{process_ref}" />')
    xml_parts.append('  </bpmn:collaboration>')
    for pool_id, pool_data in processo_yaml.get('pools', {}).items():
        process_id = pool_data['processRef']
        xml_parts.append(f'  <bpmn:process id="{process_id}" isExecutable="true">'); xml_parts.append('      <bpmn:laneSet>')
        for lane_id, lane_name in pool_data.get('lanes', {}).items():
            xml_parts.append(f'        <bpmn:lane id="{lane_id}" name="{lane_name}">')
            for el in processo_yaml.get('elements', []):
                if el['lane'] == lane_id: xml_parts.append(f'          <bpmn:flowNodeRef>{el["id"]}</bpmn:flowNodeRef>')
            xml_parts.append('        </bpmn:lane>')
        xml_parts.append('      </bpmn:laneSet>')
        for el in processo_yaml.get('elements', []):
            if el['lane'] in pool_data.get('lanes', {}):
                el_id, el_name, el_type = el['id'], el['name'], el.get('type', 'task')
                doc_text = el.get('content', ''); doc_xml = f'<bpmn:documentation>{doc_text}</bpmn:documentation>' if doc_text else ''
                tag = el_type if 'Task' in el_type or 'Gateway' in el_type or 'Event' in el_type else 'task'
                xml_parts.append(f'    <bpmn:{tag} id="{el_id}" name="{el_name}">{doc_xml}</bpmn:{tag}>')
        for flow in processo_yaml.get('flows', []): xml_parts.append(f'    <bpmn:sequenceFlow id="{flow["id"]}" name="{flow.get("name", "")}" sourceRef="{flow["source"]}" targetRef="{flow["target"]}" />')
        xml_parts.append('  </bpmn:process>')
    xml_parts.append(f'<bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{collaboration_id}"></bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
    xml_parts.append('</bpmn:definitions>')
    return '\n'.join(xml_parts)

def renderizar_bpmn_com_js(bpmn_xml_string):
    # Função de renderização com exportação para SVG (sem alterações)
    escaped_bpmn_xml = bpmn_xml_string.replace("`", "\\`").replace("'", "\\'").replace("\n", " ")
    html_content = f"""
    <!DOCTYPE html><html><head><title>BPMN Viewer</title><script src="https://unpkg.com/bpmn-js@17.0.2/dist/bpmn-viewer.development.js"></script><style>html,body,#container{{height:100%;width:100%;margin:0;padding:0}}#container{{height:calc(100% - 40px);width:100%}}#export-button-wrapper{{height:40px;text-align:right;padding:5px;background-color:#f7f7f7;border-top:1px solid #ddd}}.bjs-powered-by{{display:none !important}}button{{background-color:#1976D2;color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-family:sans-serif}}button:hover{{background-color:#1565C0}}</style></head><body><div id="container"></div><div id="export-button-wrapper"><button id="save-svg">Exportar como Imagem (SVG)</button></div><script>
        var viewer = new BpmnJS({{container:'#container'}}); var bpmnXML=`{escaped_bpmn_xml}`;
        async function openDiagram(xml){{try{{await viewer.importXML(xml);viewer.get('canvas').zoom('fit-viewport','auto')}}catch(err){{console.error(err)}}}}
        async function exportSVG(){{try{{const{{svg}}=await viewer.saveSVG();const encodedData=encodeURIComponent(svg);const link=document.createElement('a');link.href='data:image/svg+xml;charset=UTF-8,'+encodedData;link.download='diagrama_bpmn.svg';document.body.appendChild(link);link.click();document.body.removeChild(link)}}catch(err){{console.error(err)}}}}
        document.getElementById('save-svg').addEventListener('click',exportSVG);openDiagram(bpmnXML);
    </script></body></html>"""
    return html_content

def processar_comando_chat(comando, yaml_str):
    try:
        data = yaml.safe_load(yaml_str); comando = comando.lower()
        match_nome = re.search(r"mude o nome da tarefa '(.+?)' para '(.+?)'", comando)
        if match_nome:
            id_tarefa, novo_nome = match_nome.groups();
            for el in data.get('elements', []):
                if el['id'] == id_tarefa: el['name'] = novo_nome;
            return yaml.dump(data, sort_keys=False, indent=2), f"✅ Nome da tarefa '{id_tarefa}' alterado."
        return yaml_str, "❌ Comando não reconhecido."
    except yaml.YAMLError as e: return yaml_str, f"❌ Erro no formato do YAML: {e}"

# ##############################################################################
# ATUALIZAÇÃO PRINCIPAL #1: Adicionada a função para converter DataFrame para CSV
# ##############################################################################
@st.cache_data
def convert_df_to_csv(df):
    """Converte um DataFrame para um arquivo CSV codificado em UTF-8 para download."""
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
                st.session_state['df_perfis'] = pd.read_csv(uploaded_file)
                st.success("Novo arquivo carregado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")
        st.info("Amostra dos Dados Atuais")
        st.dataframe(st.session_state['df_perfis'])
        
    with col2:
        st.subheader("Dados Não Estruturados")
        st.info("Diretrizes da Campanha (CPB)")
        
        # CORREÇÃO: Removido o parâmetro 'value='
        st.text_area(
            "Edite as diretrizes:",
            height=120,
            key='diretrizes_cpb' 
        )
        
        st.info("Insights de Ciclos Anteriores")

        # CORREÇÃO: Removido o parâmetro 'value='
        st.text_area(
            "Edite os insights:",
            height=120,
            key='insights_anteriores'
        )
with tab2:
    st.header("Execução dos Agentes e Segmentação de Público")
    if 'df_perfis' not in st.session_state:
        st.warning("Carregue os dados na Fase 1 primeiro.")
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
            comando = st.text_input("Seu comando:", placeholder="mude o nome da tarefa 'task_validar' para 'Revisão Final'")
            if st.button("Executar Comando"):
                if comando:
                    novo_yaml, mensagem = processar_comando_chat(comando, st.session_state.processo_yaml_str)
                    st.session_state.processo_yaml_str = novo_yaml
                    st.success(mensagem) if "✅" in mensagem else st.warning(mensagem)
                    st.experimental_rerun()
        with col2:
            st.subheader("Visualizador BPMN e Artefatos")
            try:
                processo_yaml_obj = yaml.safe_load(st.session_state.processo_yaml_str)
                modelo_xml = gerar_modelo_bpmn_xml_com_lanes("campanha_natura", processo_yaml_obj)
                componente_html = renderizar_bpmn_com_js(modelo_xml)
                st.components.v1.html(componente_html, height=550, scrolling=False)
                
                st.divider()
                st.subheader("Downloads")
                
                # Botão para baixar o modelo BPMN
                st.download_button(label="📥 Baixar Modelo (.bpmn)", data=modelo_xml, file_name="processo_final.bpmn", mime="application/xml")
                
                # ##############################################################################
                # ATUALIZAÇÃO PRINCIPAL #2: Restaurado o botão de download da planilha
                # ##############################################################################
                csv_data = convert_df_to_csv(st.session_state['df_segmentado'])
                st.download_button(
                   label="📊 Baixar Planilha de Audiência (.csv)",
                   data=csv_data,
                   file_name="audiencia_segmentada.csv",
                   mime="text/csv",
                )

                with st.expander("Ver código XML do modelo"):
                    st.code(modelo_xml, language='xml')

            except yaml.YAMLError as e:
                st.error(f"Erro na sintaxe do YAML: {e}")
















# import streamlit as st
# import pandas as pd
# import yaml
# import re
# from io import StringIO
# import base64

# # ==============================================================================
# # DADOS SINTÉTICOS E EXEMPLO YAML (CARREGADOS NA INICIALIZAÇÃO)
# # ==============================================================================
# def carregar_dados_iniciais():
#     """Carrega todos os dados da demonstração na sessão do Streamlit."""
#     if 'df_perfis' not in st.session_state:
#         csv_data = """id_consultora,nome_consultora,regiao,nivel_consultora,meses_de_casa,vendas_ultimo_ciclo,taxa_engajamento,categoria_preferida
# 2001,Ana Silva,Sudeste,Ouro,24,2850.50,92,Perfumaria
# 2002,Bruno Costa,Nordeste,Prata,12,1550.00,65,Cuidados Diários
# 2003,Carla Dias,Sudeste,Diamante,36,4100.75,98,Maquegem
# 2004,Daniel Farias,Norte,Semente,3,450.20,25,Cuidados Diários
# """
#         st.session_state['df_perfis'] = pd.read_csv(StringIO(csv_data))
    
#     # Esta parte está correta: inicializa o estado se ele não existir.
#     if 'diretrizes_cpb' not in st.session_state:
#         st.session_state['diretrizes_cpb'] = "Tema do ciclo: Reconexão com a natureza e os sentidos. Mensagem central: 'Redescubra sua essência com Ekos'. Objetivo: Aumentar recompra da linha Ekos em 20%."
#     if 'insights_anteriores' not in st.session_state:
#         st.session_state['insights_anteriores'] = "Análise do ciclo anterior: WhatsApp teve conversão 4,7% em recompra. ROI da linha Ekos foi de 5,3x. Consultoras com mais de 3 interações convertem 2,4x mais."
#     if 'processo_yaml_str' not in st.session_state:
#         st.session_state.processo_yaml_str = """
# pools:
#   pool_ciclo_11:
#     name: Campanha Ekos Essência da Amazônia
#     processRef: Process_Ekos
#     lanes:
#       lane_estrategia: Estratégia e Análise
#       lane_ativacao: Ativação de Canais
#       lane_stakeholders: Validação
# elements:
#   - {id: start_ciclo, name: Início do Ciclo 11/2025, type: startEvent, lane: lane_estrategia, content: 'Planejamento de CRM.'}
#   - {id: task_segmentar, name: Definir Segmentos, type: serviceTask, lane: lane_estrategia, content: 'Cluster 1 (Frequentes) e Cluster 2 (Reativáveis)'}
#   - {id: gw_paralelo_inicio, name: Iniciar Ativação, type: parallelGateway, lane: lane_ativacao}
#   - {id: task_app, name: Disparar Push no App, type: serviceTask, lane: lane_ativacao, content: 'Cluster 1 → Mensagem A'}
#   - {id: task_whatsapp, name: Disparar WhatsApp, type: serviceTask, lane: lane_ativacao, content: 'Cluster 2 → Mensagem B'}
#   - {id: gw_paralelo_fim, name: Aguardar Disparos, type: parallelGateway, lane: lane_ativacao}
#   - {id: task_validar, name: Validar com Stakeholders, type: userTask, lane: lane_stakeholders, content: 'Ajuste: Incluir opt-out.'}
#   - {id: end_campanha, name: Fim do Planejamento, type: endEvent, lane: lane_stakeholders}
# flows:
#   - {id: f1, source: start_ciclo, target: task_segmentar}
#   - {id: f2, source: task_segmentar, target: gw_paralelo_inicio}
#   - {id: f3, source: gw_paralelo_inicio, target: task_app}
#   - {id: f4, source: gw_paralelo_inicio, target: task_whatsapp}
#   - {id: f5, source: task_app, target: gw_paralelo_fim}
#   - {id: f6, source: task_whatsapp, target: gw_paralelo_fim}
#   - {id: f7, source: gw_paralelo_fim, target: task_validar}
#   - {id: f8, source: task_validar, target: end_campanha}
# """

# # ==============================================================================
# # FUNÇÕES DOS AGENTES E DE GERAÇÃO
# # ==============================================================================
# def simular_organizador_de_contexto(diretrizes, insights):
#     return f"""### Informações de Negócio Relevantes:\n* **Tema do ciclo:** {diretrizes.split(".")[0]}.\n* **Mensagem central:** {diretrizes.split(".")[1]}.\n* **Canal Prioritário (Insight):** {insights.split(".")[0]}."""
# def simular_especialista_de_dados(df):
#     media_vendas = df['vendas_ultimo_ciclo'].mean(); media_engajamento = df['taxa_engajamento'].mean()
#     return f"""### Direcional de Performance Detalhado:\n* **Média de Vendas (Base Atual):** R$ {media_vendas:.2f}\n* **Média de Engajamento (Base Atual):** {media_engajamento:.1f}%"""
# def gerar_modelo_bpmn_xml_com_lanes(id_campanha, processo_yaml):
#     collaboration_id = f"Collaboration_{id_campanha}"; xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>','<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',f'  <bpmn:collaboration id="{collaboration_id}">']
#     main_process_id = ""
#     for pool_id, pool_data in processo_yaml.get('pools', {}).items():
#         process_ref = pool_data['processRef'];
#         if not main_process_id: main_process_id = process_ref
#         xml_parts.append(f'    <bpmn:participant id="{pool_id}" name="{pool_data["name"]}" processRef="{process_ref}" />')
#     xml_parts.append('  </bpmn:collaboration>')
#     for pool_id, pool_data in processo_yaml.get('pools', {}).items():
#         process_id = pool_data['processRef']
#         xml_parts.append(f'  <bpmn:process id="{process_id}" isExecutable="true">'); xml_parts.append('      <bpmn:laneSet>')
#         for lane_id, lane_name in pool_data.get('lanes', {}).items():
#             xml_parts.append(f'        <bpmn:lane id="{lane_id}" name="{lane_name}">')
#             for el in processo_yaml.get('elements', []):
#                 if el['lane'] == lane_id: xml_parts.append(f'          <bpmn:flowNodeRef>{el["id"]}</bpmn:flowNodeRef>')
#             xml_parts.append('        </bpmn:lane>')
#         xml_parts.append('      </bpmn:laneSet>')
#         for el in processo_yaml.get('elements', []):
#             if el['lane'] in pool_data.get('lanes', {}):
#                 el_id, el_name, el_type = el['id'], el['name'], el.get('type', 'task')
#                 doc_text = el.get('content', ''); doc_xml = f'<bpmn:documentation>{doc_text}</bpmn:documentation>' if doc_text else ''
#                 tag = el_type if 'Task' in el_type or 'Gateway' in el_type or 'Event' in el_type else 'task'
#                 xml_parts.append(f'    <bpmn:{tag} id="{el_id}" name="{el_name}">{doc_xml}</bpmn:{tag}>')
#         for flow in processo_yaml.get('flows', []): xml_parts.append(f'    <bpmn:sequenceFlow id="{flow["id"]}" name="{flow.get("name", "")}" sourceRef="{flow["source"]}" targetRef="{flow["target"]}" />')
#         xml_parts.append('  </bpmn:process>')
#     xml_parts.append(f'<bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{collaboration_id}"></bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
#     xml_parts.append('</bpmn:definitions>')
#     return '\n'.join(xml_parts)
# def renderizar_bpmn_com_js(bpmn_xml_string):
#     escaped_bpmn_xml = bpmn_xml_string.replace("`", "\\`").replace("'", "\\'").replace("\n", " ")
#     html_content = f"""<!DOCTYPE html><html><head><title>BPMN Viewer</title><script src="https://unpkg.com/bpmn-js@17.0.2/dist/bpmn-viewer.development.js"></script><style>html,body,#container{{height:100%;width:100%;margin:0;padding:0}}#container{{height:calc(100% - 40px);width:100%}}#export-button-wrapper{{height:40px;text-align:right;padding:5px;background-color:#f7f7f7;border-top:1px solid #ddd}}.bjs-powered-by{{display:none !important}}button{{background-color:#1976D2;color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-family:sans-serif}}button:hover{{background-color:#1565C0}}</style></head><body><div id="container"></div><div id="export-button-wrapper"><button id="save-svg">Exportar como Imagem (SVG)</button></div><script>
#         var viewer = new BpmnJS({{container:'#container'}}); var bpmnXML=`{escaped_bpmn_xml}`;
#         async function openDiagram(xml){{try{{await viewer.importXML(xml);viewer.get('canvas').zoom('fit-viewport','auto')}}catch(err){{console.error(err)}}}}
#         async function exportSVG(){{try{{const{{svg}}=await viewer.saveSVG();const encodedData=encodeURIComponent(svg);const link=document.createElement('a');link.href='data:image/svg+xml;charset=UTF-8,'+encodedData;link.download='diagrama_bpmn.svg';document.body.appendChild(link);link.click();document.body.removeChild(link)}}catch(err){{console.error(err)}}}}
#         document.getElementById('save-svg').addEventListener('click',exportSVG);openDiagram(bpmnXML);
#     </script></body></html>"""
#     return html_content
# def processar_comando_chat(comando, yaml_str):
#     try:
#         data = yaml.safe_load(yaml_str); comando = comando.lower()
#         match_nome = re.search(r"mude o nome da tarefa '(.+?)' para '(.+?)'", comando)
#         if match_nome:
#             id_tarefa, novo_nome = match_nome.groups();
#             for el in data.get('elements', []):
#                 if el['id'] == id_tarefa: el['name'] = novo_nome;
#             return yaml.dump(data, sort_keys=False, indent=2), f"✅ Nome da tarefa '{id_tarefa}' alterado."
#         return yaml_str, "❌ Comando não reconhecido."
#     except yaml.YAMLError as e: return yaml_str, f"❌ Erro no formato do YAML: {e}"

# # ==============================================================================
# # INTERFACE DA APLICAÇÃO
# # ==============================================================================
# st.set_page_config(layout="wide")
# st.title("Assistente de Planejamento de Campanhas CRM")

# carregar_dados_iniciais()

# tab1, tab2, tab3 = st.tabs(["**📊 Fase 1: Dados e Contexto**", "**⚙️ Fase 2: Análise e Segmentação**", "**✍️ Fase 3: Modelagem e Artefatos**"])

# with tab1:
#     st.header("Entrada de Dados da Campanha")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Dados Estruturados")
#         uploaded_file = st.file_uploader("Carregar arquivo de Consultoras (CSV)", type="csv")
#         if uploaded_file is not None:
#             try:
#                 st.session_state['df_perfis'] = pd.read_csv(uploaded_file); st.success("Novo arquivo carregado!")
#             except Exception as e: st.error(f"Erro ao ler o arquivo: {e}")
#         st.info("Amostra dos Dados Atuais"); st.dataframe(st.session_state['df_perfis'])
#     with col2:
#         st.subheader("Dados Não Estruturados")
#         # ##############################################################################
#         # ATUALIZAÇÃO PRINCIPAL AQUI: Removido o parâmetro 'value=' das chamadas
#         # ##############################################################################
#         st.text_area("Diretrizes da Campanha (CPB):", height=120, key='diretrizes_cpb')
#         st.text_area("Insights de Ciclos Anteriores:", height=120, key='insights_anteriores')

# with tab2:
#     st.header("Execução dos Agentes e Segmentação de Público")
#     if 'df_perfis' not in st.session_state:
#         st.warning("Carregue os dados na Fase 1 primeiro.")
#     else:
#         st.subheader("Resultados dos Agentes de Análise")
#         with st.expander("🤖 Agente: Organizador de Contexto", expanded=True):
#             st.markdown(simular_organizador_de_contexto(st.session_state.diretrizes_cpb, st.session_state.insights_anteriores))
#         with st.expander("🤖 Agente: Especialista de Dados", expanded=True):
#             st.markdown(simular_especialista_de_dados(st.session_state.df_perfis))
#         st.divider()
#         st.subheader("🎯 Agente: Seletor de Público Interativo")
#         df = st.session_state.df_perfis.copy(); col1, col2, col3 = st.columns(3)
#         with col1: sel_regioes = st.multiselect("Região:", df['regiao'].unique(), default=df['regiao'].unique())
#         with col2: sel_niveis = st.multiselect("Nível:", df['nivel_consultora'].unique(), default=df['nivel_consultora'].unique())
#         with col3: max_vendas = int(df['vendas_ultimo_ciclo'].max()) if not df.empty else 1000; sel_vendas = st.slider("Vendas (R$):", 0, max_vendas, (0, max_vendas))
#         df_filtrado = df[(df['regiao'].isin(sel_regioes))&(df['nivel_consultora'].isin(sel_niveis))&(df['vendas_ultimo_ciclo'].between(sel_vendas[0], sel_vendas[1]))]
#         st.metric("Total no Segmento", len(df_filtrado)); st.dataframe(df_filtrado)
#         if st.button("💾 Salvar Segmentação"):
#             st.session_state['df_segmentado'] = df_filtrado; st.success(f"{len(df_filtrado)} consultoras salvas. Prossiga para a Fase 3.")

# with tab3:
#     st.header("Modelagem do Processo e Geração de Artefatos")
#     if 'df_segmentado' not in st.session_state:
#         st.warning("Crie e salve um segmento na Fase 2 primeiro.")
#     else:
#         st.success(f"Modelando a estratégia para o segmento de **{len(st.session_state['df_segmentado'])}** consultoras.")
#         col1, col2 = st.columns([2, 3])
#         with col1:
#             st.subheader("Definição do Processo (YAML)")
#             yaml_editor = st.text_area("Edite o processo:", value=st.session_state.processo_yaml_str, height=500, key="yaml_editor_main")
#             st.session_state.processo_yaml_str = yaml_editor
#             st.subheader("💬 Chat de Refinamento")
#             comando = st.text_input("Seu comando:", placeholder="mude o nome da tarefa 'task_validar' para 'Revisão Final'")
#             if st.button("Executar Comando"):
#                 if comando:
#                     novo_yaml, mensagem = processar_comando_chat(comando, st.session_state.processo_yaml_str)
#                     st.session_state.processo_yaml_str = novo_yaml
#                     st.success(mensagem) if "✅" in mensagem else st.warning(mensagem)
#                     st.experimental_rerun()
#         with col2:
#             st.subheader("Visualizador BPMN e Artefatos")
#             try:
#                 processo_yaml_obj = yaml.safe_load(st.session_state.processo_yaml_str)
#                 modelo_xml = gerar_modelo_bpmn_xml_com_lanes("campanha_natura", processo_yaml_obj)
#                 componente_html = renderizar_bpmn_com_js(modelo_xml)
#                 st.components.v1.html(componente_html, height=550, scrolling=False)
#                 st.download_button(label="📥 Baixar Modelo (.bpmn)", data=modelo_xml, file_name="processo_final.bpmn", mime="application/xml")
#                 with st.expander("Ver código XML"): st.code(modelo_xml, language='xml')
#             except yaml.YAMLError as e:
#                 st.error(f"Erro na sintaxe do YAML: {e}")





# import streamlit as st
# import pandas as pd
# import yaml
# import re
# from io import StringIO
# import base64

# # ==============================================================================
# # DADOS SINTÉTICOS E EXEMPLO YAML (CARREGADOS NA INICIALIZAÇÃO)
# # ==============================================================================
# def carregar_dados_iniciais():
#     """Carrega todos os dados da demonstração na sessão do Streamlit."""
#     if 'df_perfis' not in st.session_state:
#         csv_data = """id_consultora,nome_consultora,regiao,nivel_consultora,meses_de_casa,vendas_ultimo_ciclo,taxa_engajamento,categoria_preferida
# 2001,Ana Silva,Sudeste,Ouro,24,2850.50,92,Perfumaria
# 2002,Bruno Costa,Nordeste,Prata,12,1550.00,65,Cuidados Diários
# 2003,Carla Dias,Sudeste,Diamante,36,4100.75,98,Maquegem
# 2004,Daniel Farias,Norte,Semente,3,450.20,25,Cuidados Diários
# """
#         st.session_state['df_perfis'] = pd.read_csv(StringIO(csv_data))
#     if 'diretrizes_cpb' not in st.session_state:
#         st.session_state['diretrizes_cpb'] = "Tema do ciclo: Reconexão com a natureza e os sentidos. Mensagem central: 'Redescubra sua essência com Ekos'. Objetivo: Aumentar recompra da linha Ekos em 20%."
#     if 'insights_anteriores' not in st.session_state:
#         st.session_state['insights_anteriores'] = "Análise do ciclo anterior: WhatsApp teve conversão 4,7% em recompra. ROI da linha Ekos foi de 5,3x. Consultoras com mais de 3 interações convertem 2,4x mais."
#     if 'processo_yaml_str' not in st.session_state:
#         st.session_state.processo_yaml_str = """
# pools:
#   pool_ciclo_11:
#     name: Campanha Ekos Essência da Amazônia
#     processRef: Process_Ekos
#     lanes:
#       lane_estrategia: Estratégia e Análise
#       lane_ativacao: Ativação de Canais
#       lane_stakeholders: Validação
# elements:
#   - {id: start_ciclo, name: Início do Ciclo 11/2025, type: startEvent, lane: lane_estrategia, content: 'Planejamento de CRM.'}
#   - {id: task_segmentar, name: Definir Segmentos, type: serviceTask, lane: lane_estrategia, content: 'Cluster 1 (Frequentes) e Cluster 2 (Reativáveis)'}
#   - {id: gw_paralelo_inicio, name: Iniciar Ativação, type: parallelGateway, lane: lane_ativacao}
#   - {id: task_app, name: Disparar Push no App, type: serviceTask, lane: lane_ativacao, content: 'Cluster 1 → Mensagem A'}
#   - {id: task_whatsapp, name: Disparar WhatsApp, type: serviceTask, lane: lane_ativacao, content: 'Cluster 2 → Mensagem B'}
#   - {id: gw_paralelo_fim, name: Aguardar Disparos, type: parallelGateway, lane: lane_ativacao}
#   - {id: task_validar, name: Validar com Stakeholders, type: userTask, lane: lane_stakeholders, content: 'Ajuste: Incluir opt-out.'}
#   - {id: end_campanha, name: Fim do Planejamento, type: endEvent, lane: lane_stakeholders}
# flows:
#   - {id: f1, source: start_ciclo, target: task_segmentar}
#   - {id: f2, source: task_segmentar, target: gw_paralelo_inicio}
#   - {id: f3, source: gw_paralelo_inicio, target: task_app}
#   - {id: f4, source: gw_paralelo_inicio, target: task_whatsapp}
#   - {id: f5, source: task_app, target: gw_paralelo_fim}
#   - {id: f6, source: task_whatsapp, target: gw_paralelo_fim}
#   - {id: f7, source: gw_paralelo_fim, target: task_validar}
#   - {id: f8, source: task_validar, target: end_campanha}
# """

# # ==============================================================================
# # FUNÇÕES DOS AGENTES E DE GERAÇÃO
# # ==============================================================================
# def simular_organizador_de_contexto(diretrizes, insights):
#     return f"""
#     ### Informações de Negócio Relevantes:
#     * **Tema do ciclo:** {diretrizes.split(".")[0]}.
#     * **Mensagem central:** {diretrizes.split(".")[1]}.
#     * **Canal Prioritário (Insight):** {insights.split(".")[0]}.
#     """

# def simular_especialista_de_dados(df):
#     media_vendas = df['vendas_ultimo_ciclo'].mean()
#     media_engajamento = df['taxa_engajamento'].mean()
#     return f"""
#     ### Direcional de Performance Detalhado:
#     * **Média de Vendas (Base Atual):** R$ {media_vendas:.2f}
#     * **Média de Engajamento (Base Atual):** {media_engajamento:.1f}%
#     """

# def gerar_modelo_bpmn_xml_com_lanes(id_campanha, processo_yaml):
#     # Função de geração de XML (sem alterações)
#     collaboration_id = f"Collaboration_{id_campanha}"; xml_parts = [
#         '<?xml version="1.0" encoding="UTF-8"?>',
#         '<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',
#         f'  <bpmn:collaboration id="{collaboration_id}">'
#     ]
#     main_process_id = ""
#     for pool_id, pool_data in processo_yaml.get('pools', {}).items():
#         process_ref = pool_data['processRef'];
#         if not main_process_id: main_process_id = process_ref
#         xml_parts.append(f'    <bpmn:participant id="{pool_id}" name="{pool_data["name"]}" processRef="{process_ref}" />')
#     xml_parts.append('  </bpmn:collaboration>')
#     for pool_id, pool_data in processo_yaml.get('pools', {}).items():
#         process_id = pool_data['processRef']
#         xml_parts.append(f'  <bpmn:process id="{process_id}" isExecutable="true">'); xml_parts.append('      <bpmn:laneSet>')
#         for lane_id, lane_name in pool_data.get('lanes', {}).items():
#             xml_parts.append(f'        <bpmn:lane id="{lane_id}" name="{lane_name}">')
#             for el in processo_yaml.get('elements', []):
#                 if el['lane'] == lane_id: xml_parts.append(f'          <bpmn:flowNodeRef>{el["id"]}</bpmn:flowNodeRef>')
#             xml_parts.append('        </bpmn:lane>')
#         xml_parts.append('      </bpmn:laneSet>')
#         for el in processo_yaml.get('elements', []):
#             if el['lane'] in pool_data.get('lanes', {}):
#                 el_id, el_name, el_type = el['id'], el['name'], el.get('type', 'task')
#                 doc_text = el.get('content', ''); doc_xml = f'<bpmn:documentation>{doc_text}</bpmn:documentation>' if doc_text else ''
#                 tag = el_type if 'Task' in el_type or 'Gateway' in el_type or 'Event' in el_type else 'task'
#                 xml_parts.append(f'    <bpmn:{tag} id="{el_id}" name="{el_name}">{doc_xml}</bpmn:{tag}>')
#         for flow in processo_yaml.get('flows', []): xml_parts.append(f'    <bpmn:sequenceFlow id="{flow["id"]}" name="{flow.get("name", "")}" sourceRef="{flow["source"]}" targetRef="{flow["target"]}" />')
#         xml_parts.append('  </bpmn:process>')
#     xml_parts.append(f'<bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{collaboration_id}"></bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
#     xml_parts.append('</bpmn:definitions>')
#     return '\n'.join(xml_parts)

# def renderizar_bpmn_com_js(bpmn_xml_string):
#     escaped_bpmn_xml = bpmn_xml_string.replace("`", "\\`").replace("'", "\\'").replace("\n", " ")
#     html_content = f"""
#     <!DOCTYPE html><html><head><title>BPMN Viewer</title><script src="https://unpkg.com/bpmn-js@17.0.2/dist/bpmn-viewer.development.js"></script><style>html,body,#container{{height:100%;width:100%;margin:0;padding:0}}#container{{height:calc(100% - 40px);width:100%}}#export-button-wrapper{{height:40px;text-align:right;padding:5px;background-color:#f7f7f7;border-top:1px solid #ddd}}.bjs-powered-by{{display:none !important}}button{{background-color:#1976D2;color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-family:sans-serif}}button:hover{{background-color:#1565C0}}</style></head><body><div id="container"></div><div id="export-button-wrapper"><button id="save-svg">Exportar como Imagem (SVG)</button></div><script>
#         var viewer = new BpmnJS({{container:'#container'}}); var bpmnXML=`{escaped_bpmn_xml}`;
#         async function openDiagram(xml){{try{{await viewer.importXML(xml);viewer.get('canvas').zoom('fit-viewport','auto')}}catch(err){{console.error(err)}}}}
#         async function exportSVG(){{try{{const{{svg}}=await viewer.saveSVG();const encodedData=encodeURIComponent(svg);const link=document.createElement('a');link.href='data:image/svg+xml;charset=UTF-8,'+encodedData;link.download='diagrama_bpmn.svg';document.body.appendChild(link);link.click();document.body.removeChild(link)}}catch(err){{console.error(err)}}}}
#         document.getElementById('save-svg').addEventListener('click',exportSVG);openDiagram(bpmnXML);
#     </script></body></html>"""
#     return html_content

# def processar_comando_chat(comando, yaml_str):
#     try:
#         data = yaml.safe_load(yaml_str); comando = comando.lower()
#         match_nome = re.search(r"mude o nome da tarefa '(.+?)' para '(.+?)'", comando)
#         if match_nome:
#             id_tarefa, novo_nome = match_nome.groups();
#             for el in data.get('elements', []):
#                 if el['id'] == id_tarefa: el['name'] = novo_nome;
#             return yaml.dump(data, sort_keys=False, indent=2), f"✅ Nome da tarefa '{id_tarefa}' alterado."
#         return yaml_str, "❌ Comando não reconhecido."
#     except yaml.YAMLError as e: return yaml_str, f"❌ Erro no formato do YAML: {e}"

# # ==============================================================================
# # INTERFACE DA APLICAÇÃO
# # ==============================================================================
# st.set_page_config(layout="wide")
# st.title("Assistente de Planejamento de Campanhas CRM")

# carregar_dados_iniciais()

# tab1, tab2, tab3 = st.tabs(["**📊 Fase 1: Dados e Contexto**", "**⚙️ Fase 2: Análise e Segmentação**", "**✍️ Fase 3: Modelagem e Artefatos**"])

# with tab1:
#     st.header("Entrada de Dados da Campanha")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Dados Estruturados")
#         uploaded_file = st.file_uploader("Carregar arquivo de Consultoras (CSV)", type="csv")
#         if uploaded_file is not None:
#             try:
#                 st.session_state['df_perfis'] = pd.read_csv(uploaded_file)
#                 st.success("Novo arquivo carregado com sucesso!")
#             except Exception as e:
#                 st.error(f"Erro ao ler o arquivo: {e}")
#         st.info("Amostra dos Dados Atuais")
#         st.dataframe(st.session_state['df_perfis'])
#     with col2:
#         st.subheader("Dados Não Estruturados")
#         st.text_area("Diretrizes da Campanha (CPB):", value=st.session_state['diretrizes_cpb'], height=120, key='diretrizes_cpb')
#         st.text_area("Insights de Ciclos Anteriores:", value=st.session_state['insights_anteriores'], height=120, key='insights_anteriores')

# with tab2:
#     st.header("Execução dos Agentes e Segmentação de Público")
#     if 'df_perfis' not in st.session_state:
#         st.warning("Por favor, carregue os dados na Fase 1 primeiro.")
#     else:
#         st.subheader("Resultados dos Agentes de Análise")
#         with st.expander("🤖 Agente: Organizador de Contexto", expanded=True):
#             st.markdown(simular_organizador_de_contexto(st.session_state.diretrizes_cpb, st.session_state.insights_anteriores))
#         with st.expander("🤖 Agente: Especialista de Dados", expanded=True):
#             st.markdown(simular_especialista_de_dados(st.session_state.df_perfis))
        
#         st.divider()
#         st.subheader("🎯 Agente: Seletor de Público Interativo")
#         df_para_filtrar = st.session_state.df_perfis.copy()
#         col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
#         with col_filtro1:
#             regioes_selecionadas = st.multiselect("Filtrar por Região:", df_para_filtrar['regiao'].unique(), default=df_para_filtrar['regiao'].unique())
#         with col_filtro2:
#             niveis_selecionados = st.multiselect("Filtrar por Nível:", df_para_filtrar['nivel_consultora'].unique(), default=df_para_filtrar['nivel_consultora'].unique())
#         with col_filtro3:
#             max_vendas = int(df_para_filtrar['vendas_ultimo_ciclo'].max()) if not df_para_filtrar.empty else 1000
#             filtro_vendas = st.slider("Filtrar por Vendas (R$):", 0, max_vendas, (0, max_vendas))
#         df_filtrado = df_para_filtrar[(df_para_filtrar['regiao'].isin(regioes_selecionadas)) & (df_para_filtrar['nivel_consultora'].isin(niveis_selecionados)) & (df_para_filtrar['vendas_ultimo_ciclo'].between(filtro_vendas[0], filtro_vendas[1]))]
#         st.metric(label="Total de Pessoas no Segmento", value=len(df_filtrado))
#         st.dataframe(df_filtrado)
#         if st.button("💾 Salvar Segmentação e Avançar"):
#             st.session_state['df_segmentado'] = df_filtrado
#             st.success(f"{len(df_filtrado)} consultoras foram salvas. Prossiga para a Fase 3.")

# # ##############################################################################
# # ATUALIZAÇÃO PRINCIPAL: Fase 3 agora contém o editor, o chat e o visualizador
# # ##############################################################################
# with tab3:
#     st.header("Modelagem do Processo e Geração de Artefatos")
#     if 'df_segmentado' not in st.session_state:
#         st.warning("Por favor, crie e salve um segmento na Fase 2 primeiro.")
#     else:
#         st.success(f"Modelando a estratégia para o segmento de **{len(st.session_state['df_segmentado'])}** consultoras.")
        
#         col1, col2 = st.columns([2, 3])
#         with col1:
#             st.subheader("Definição do Processo (YAML)")
#             yaml_editor = st.text_area("Edite o processo:", value=st.session_state.processo_yaml_str, height=500, key="yaml_editor_main")
#             st.session_state.processo_yaml_str = yaml_editor
            
#             # --- CHAT INTERATIVO RESTAURADO ---
#             st.subheader("💬 Chat de Refinamento")
#             comando = st.text_input("Seu comando:", placeholder="mude o nome da tarefa 'task_validar' para 'Revisão Final'")
#             if st.button("Executar Comando"):
#                 if comando:
#                     novo_yaml, mensagem = processar_comando_chat(comando, st.session_state.processo_yaml_str)
#                     st.session_state.processo_yaml_str = novo_yaml
#                     st.success(mensagem) if "✅" in mensagem else st.warning(mensagem)
#                     st.experimental_rerun()

#         with col2:
#             st.subheader("Visualizador BPMN e Artefatos")
#             try:
#                 processo_yaml_obj = yaml.safe_load(st.session_state.processo_yaml_str)
#                 modelo_xml = gerar_modelo_bpmn_xml_com_lanes("campanha_natura", processo_yaml_obj)
#                 componente_html = renderizar_bpmn_com_js(modelo_xml)
#                 st.components.v1.html(componente_html, height=550, scrolling=False)
                
#                 st.download_button(label="📥 Baixar Modelo (.bpmn)", data=modelo_xml, file_name="processo_final.bpmn", mime="application/xml")
#                 with st.expander("Ver código XML do modelo"):
#                     st.code(modelo_xml, language='xml')

#             except yaml.YAMLError as e:
#                 st.error(f"Erro na sintaxe do YAML: {e}")