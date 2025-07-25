import graphviz
import re

def extrair_etapas_e_conexoes(descricao):
    """
    Função auxiliar para extrair etapas e decisões de um texto simples.
    Assume que cada linha é uma etapa ou uma conexão.
    Exemplos de formato esperado:
    "ETAPA: Nome da Etapa"
    "DECISÃO: Nome da Decisão"
    "CONEXÃO: Etapa de Origem -> Etapa de Destino [rótulo]"
    """
    etapas = {}
    conexoes = []
    
    linhas = [linha.strip() for linha in descricao.strip().split('\n')]
    
    for i, linha in enumerate(linhas):
        if linha.startswith("ETAPA:"):
            nome = linha.replace("ETAPA:", "").strip()
            etapas[nome] = {'tipo': 'etapa', 'id': f'etapa_{i}'}
        elif linha.startswith("INÍCIO:"):
            nome = linha.replace("INÍCIO:", "").strip()
            etapas[nome] = {'tipo': 'inicio', 'id': f'inicio_{i}'}
        elif linha.startswith("FIM:"):
            nome = linha.replace("FIM:", "").strip()
            etapas[nome] = {'tipo': 'fim', 'id': f'fim_{i}'}
        elif linha.startswith("DECISÃO:"):
            nome = linha.replace("DECISÃO:", "").strip()
            etapas[nome] = {'tipo': 'decisao', 'id': f'decisao_{i}'}
        elif linha.startswith("CONEXÃO:"):
            partes = re.match(r"CONEXÃO:\s*(.+?)\s*->\s*(.+?)(?:\s*\[(.+?)\])?", linha)
            if partes:
                origem, destino, rotulo = partes.groups()
                conexoes.append({
                    'origem': origem.strip(),
                    'destino': destino.strip(),
                    'rotulo': rotulo.strip() if rotulo else ''
                })
                
    return etapas, conexoes

def gerar_fluxograma_campanha(id_campanha, descricao_textual):
    """
    Gera um fluxograma visual para uma campanha de CRM a partir de uma descrição textual.

    Args:
        id_campanha (str): Um identificador único para a campanha (usado no nome do arquivo).
        descricao_textual (str): Um texto estruturado descrevendo os passos da campanha.
    """
    # Documentação: Inicializa o objeto do grafo.
    # 'Digraph' cria um grafo direcionado (com setas).
    # 'graph_attr' define atributos globais para o gráfico, como a direção do layout (de cima para baixo).
    # 'node_attr' e 'edge_attr' definem o estilo padrão para nós (caixas) e arestas (setas).
    dot = graphviz.Digraph(
        comment=f'Fluxograma da Campanha {id_campanha}',
        graph_attr={'rankdir': 'TB', 'bgcolor': '#F5F5F5', 'splines': 'ortho'},
        node_attr={'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#FFFFFF', 'fontname': 'Helvetica'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '10'}
    )

    # Documentação: Extrai as etapas e conexões da descrição textual.
    etapas, conexoes = extrair_etapas_e_conexoes(descricao_textual)

    # Documentação: Itera sobre cada etapa identificada para adicioná-la ao gráfico como um "nó".
    # Diferentes tipos de etapas (início, fim, decisão) recebem formas e cores diferentes
    # para se assemelharem a um diagrama BPMN.
    for nome, attrs in etapas.items():
        if attrs['tipo'] == 'inicio':
            dot.node(attrs['id'], nome, shape='circle', fillcolor='#C8E6C9') # Verde
        elif attrs['tipo'] == 'fim':
            dot.node(attrs['id'], nome, shape='doublecircle', fillcolor='#FFCDD2') # Vermelho
        elif attrs['tipo'] == 'decisao':
            dot.node(attrs['id'], nome, shape='diamond', fillcolor='#FFF9C4') # Amarelo
        else: # Etapa padrão
            dot.node(attrs['id'], nome, shape='box', fillcolor='#BBDEFB') # Azul

    # Documentação: Itera sobre as conexões para criar as "arestas" (setas) entre os nós.
    # O 'label' é o texto que aparece na seta (ex: "Sim", "Não", "Abriu E-mail").
    for conexao in conexoes:
        id_origem = etapas.get(conexao['origem'], {}).get('id')
        id_destino = etapas.get(conexao['destino'], {}).get('id')
        if id_origem and id_destino:
            dot.edge(id_origem, id_destino, label=conexao['rotulo'])

    # Documentação: Renderiza o gráfico e o salva em um arquivo.
    # O formato é 'png'. O nome do arquivo será, por exemplo, 'fluxo_campanha_Q3_BoasVindas.png'.
    # O argumento 'cleanup=True' remove o arquivo de código-fonte do Graphviz após a geração da imagem.
    nome_arquivo = f'fluxo_campanha_{id_campanha}'
    dot.render(nome_arquivo, format='png', cleanup=True)
    
    print(f"✅ Sucesso! Fluxograma gerado e salvo como '{nome_arquivo}.png'")


# --- Exemplo de Uso ---
# Documentação: Aqui simulamos o input que viria do "Planejador de Campanhas".
# É uma string simples e estruturada que descreve a lógica da jornada do cliente.
descricao_campanha_boas_vindas = """
INÍCIO: Nova Consultora Cadastrada
ETAPA: Enviar E-mail de Boas Vindas
DECISÃO: E-mail foi aberto em 48h?
ETAPA: Enviar SMS com Link para o App
ETAPA: Adicionar à lista de "Engajadas"
ETAPA: Reenviar E-mail com Título Diferente
DECISÃO: Abriu o segundo E-mail?
ETAPA: Ligar para a Consultora
FIM: Fim do Fluxo de Boas Vindas

CONEXÃO: Nova Consultora Cadastrada -> Enviar E-mail de Boas Vindas
CONEXÃO: Enviar E-mail de Boas Vindas -> E-mail foi aberto em 48h?
CONEXÃO: E-mail foi aberto em 48h? -> Enviar SMS com Link para o App [Sim]
CONEXÃO: E-mail foi aberto em 48h? -> Reenviar E-mail com Título Diferente [Não]
CONEXÃO: Enviar SMS com Link para o App -> Adicionar à lista de "Engajadas"
CONEXÃO: Adicionar à lista de "Engajadas" -> Fim do Fluxo de Boas Vindas
CONEXÃO: Reenviar E-mail com Título Diferente -> Abriu o segundo E-mail?
CONEXÃO: Abriu o segundo E-mail? -> Adicionar à lista de "Engajadas" [Sim]
CONEXÃO: Abriu o segundo E-mail? -> Ligar para a Consultora [Não]
CONEXÃO: Ligar para a Consultora -> Fim do Fluxo de Boas Vindas
"""

# Documentação: Chamamos a função principal para gerar o fluxograma.
gerar_fluxograma_campanha("Q3_BoasVindas", descricao_campanha_boas_vindas)