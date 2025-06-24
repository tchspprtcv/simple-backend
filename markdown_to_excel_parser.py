import re
import pandas as pd
import markdown

def extrair_tarefas_plano_execucao(markdown_content):
    """
    Extrai tarefas da secção "Parte 3 – Plano de Execução do Projeto" de um texto Markdown.
    """
    tarefas = []

    # Regex para encontrar as Fases e o seu conteúdo
    fases_regex = r"Fase \d+: (.*?)\n(.*?)(?=\nFase \d+:|\Z)"

    # Encontrar a secção "Parte 3 – Plano de Execução do Projeto"
    parte_3_match = re.search(r"## Parte 3 – Plano de Execução do Projeto(.*?)\Z", markdown_content, re.DOTALL | re.IGNORECASE)

    if not parte_3_match:
        return tarefas

    plano_execucao_content = parte_3_match.group(1)

    for fase_match in re.finditer(fases_regex, plano_execucao_content, re.DOTALL | re.IGNORECASE):
        categoria = fase_match.group(1).strip()
        conteudo_fase = fase_match.group(2)

        # Tentar extrair "Entregáveis Esperados" como subtarefas
        entregaveis_match = re.search(r"\*   Entregáveis Esperados:\s*\n(.*?)(?=\n\s*\*|\Z)", conteudo_fase, re.DOTALL | re.IGNORECASE)

        if entregaveis_match:
            lista_entregaveis = entregaveis_match.group(1).strip()
            # Cada item da lista de entregáveis será uma subtarefa
            subtarefas_raw = re.findall(r"\*   (.*?)(?:\n\s*\*   |\Z)", lista_entregaveis, re.DOTALL)
            for subtarefa_desc in subtarefas_raw:
                # Limpar a descrição da subtarefa
                descricao_limpa = re.sub(r'\s+', ' ', subtarefa_desc.strip()).strip()
                tarefas.append({
                    "Categoria/Tópico": categoria,
                    "Subtarefa": descricao_limpa,
                    "Descrição": "",  # Descrição mais detalhada pode ser adicionada manualmente se necessário
                    "Prioridade": "",
                    "Responsável": "",
                    "Estado": "Pendente",
                    "Data de Início": "",
                    "Prazo": ""
                })
        else:
            # Se não houver "Entregáveis Esperados" específicos, a própria fase é uma tarefa
            # Tenta extrair "Objetivo" para a descrição
            objetivo_match = re.search(r"\*   Objetivo:\s*(.*?)\n", conteudo_fase, re.IGNORECASE)
            descricao_fase = objetivo_match.group(1).strip() if objetivo_match else ""
            tarefas.append({
                "Categoria/Tópico": categoria,
                "Subtarefa": f"Concluir {categoria}", # Subtarefa genérica
                "Descrição": descricao_fase,
                "Prioridade": "",
                "Responsável": "",
                "Estado": "Pendente",
                "Data de Início": "",
                "Prazo": ""
            })

    return tarefas

def markdown_to_excel(markdown_file_path, excel_file_path):
    """
    Converte um ficheiro Markdown para uma folha de cálculo Excel.
    """
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"Erro: Ficheiro Markdown '{markdown_file_path}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao ler o ficheiro Markdown: {e}")
        return

    # Extrair tarefas da secção do plano de execução
    tarefas_extraidas = extrair_tarefas_plano_execucao(markdown_content)

    if not tarefas_extraidas:
        print("Nenhuma tarefa encontrada na secção 'Parte 3 – Plano de Execução do Projeto'.")
        # Tentar uma abordagem mais genérica se a específica falhar
        # Esta parte pode ser expandida para analisar títulos e listas de forma mais geral
        html = markdown.markdown(markdown_content)
        # A conversão genérica de Markdown para Excel pode ser complexa
        # e depende muito da estrutura do Markdown.
        # Para este caso, focamos na "Parte 3".
        # Se precisar de uma conversão mais genérica, seria necessário um parser mais robusto.
        print("A conversão genérica de Markdown para Excel não está implementada em detalhe para este script.")
        print("Foco na extração da 'Parte 3 - Plano de Execução'.")
        if not tarefas_extraidas: # Ainda sem tarefas
             print("Não foi possível extrair tarefas para o Excel.")
             return

    # Criar DataFrame do Pandas
    df = pd.DataFrame(tarefas_extraidas)

    # Definir a ordem das colunas
    colunas_ordenadas = [
        "Categoria/Tópico",
        "Subtarefa",
        "Descrição",
        "Prioridade",
        "Responsável",
        "Estado",
        "Data de Início",
        "Prazo"
    ]
    df = df[colunas_ordenadas]

    # Exportar para Excel
    try:
        df.to_excel(excel_file_path, index=False, engine='openpyxl')
        print(f"Folha de cálculo '{excel_file_path}' gerada com sucesso.")
    except Exception as e:
        print(f"Erro ao gerar a folha de cálculo Excel: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Uso: python markdown_to_excel_parser.py <caminho_ficheiro_markdown> <caminho_ficheiro_excel>")
        sys.exit(1)

    markdown_file_path = sys.argv[1]
    excel_file_path = sys.argv[2]

    markdown_to_excel(markdown_file_path, excel_file_path)
