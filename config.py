# ⚙️ CONFIGURAÇÕES DO DASHBOARD EDUCACIONAL

"""
Este arquivo permite personalizar os critérios e parâmetros usados nas análises do dashboard.
Modifique os valores abaixo conforme necessário e reinicie o dashboard.
"""

# ========================================
# CRITÉRIOS DE ABANDONO DE DISCIPLINAS
# ========================================

# Dias mínimos desde liberação para considerar abandono
# Disciplinas liberadas há menos tempo não são contadas como abandonadas
DIAS_MINIMOS_ABANDONO = 30

# Percentual máximo de conclusão para considerar abandono
# Ex: 50 = disciplinas com menos de 50% concluídas
PERCENTUAL_MAXIMO_ABANDONO = 50

# Considerar apenas disciplinas sem data de término?
APENAS_SEM_TERMINO = True

# ========================================
# CRITÉRIOS DE CONCLUSÃO
# ========================================

# Percentual mínimo para considerar disciplina concluída
PERCENTUAL_MINIMO_CONCLUSAO = 100

# ========================================
# ANÁLISES E GRÁFICOS
# ========================================

# Número de itens a exibir nos Top N gráficos
TOP_N_CURSOS = 10
TOP_N_DISCIPLINAS = 20
TOP_N_DISCIPLINAS_ACESSO = 15

# Número mínimo de avaliações para incluir disciplina em rankings de nota
MIN_AVALIACOES_NOTA = 5

# Número mínimo de matrículas para calcular taxa de conclusão
MIN_MATRICULAS_TAXA = 10

# ========================================
# FAIXAS DE ANÁLISE DE ABANDONO
# ========================================

# Percentual para considerar "abandono inicial"
ABANDONO_INICIAL_PERCENTUAL = 20

# Número de bins no histograma de abandono
BINS_HISTOGRAMA_ABANDONO = 20

# ========================================
# SENHA DO DASHBOARD
# ========================================

# Senha para acesso ao dashboard (em texto plano - será convertida em hash)
# Para alterar, modifique aqui e execute: python gerar_senha.py
SENHA_DASHBOARD = "admin123"

# ========================================
# OPÇÕES DE VISUALIZAÇÃO
# ========================================

# Tema de cores para gráficos
CORES = {
    'positivo': 'greens',      # Para conclusões, ativos
    'negativo': 'reds',        # Para abandonos, cancelamentos
    'neutro': 'blues',         # Para acessos, distribuições
    'geral': 'viridis',        # Para análises gerais
    'destaque': '#2ecc71',     # Verde para métricas positivas
    'alerta': '#e74c3c'        # Vermelho para métricas de atenção
}

# ========================================
# CACHE E PERFORMANCE
# ========================================

# Tempo de cache dos dados em segundos (None = cache permanente até reiniciar)
TEMPO_CACHE_SEGUNDOS = None

# ========================================
# NOTAS E DOCUMENTAÇÃO
# ========================================

"""
EXEMPLOS DE USO:

1. Para considerar abandono apenas após 60 dias:
   DIAS_MINIMOS_ABANDONO = 60

2. Para ser mais rigoroso com abandono (apenas < 25%):
   PERCENTUAL_MAXIMO_ABANDONO = 25

3. Para incluir disciplinas em progresso no abandono:
   APENAS_SEM_TERMINO = False

4. Para exibir Top 15 em vez de Top 10:
   TOP_N_CURSOS = 15
   TOP_N_DISCIPLINAS = 30

5. Para alterar a senha:
   SENHA_DASHBOARD = "minha_nova_senha"
   (Depois execute: python gerar_senha.py)
"""

# ========================================
# VALIDAÇÃO (NÃO MODIFIQUE)
# ========================================

def validar_configuracoes():
    """Valida se as configurações estão corretas"""
    assert DIAS_MINIMOS_ABANDONO > 0, "DIAS_MINIMOS_ABANDONO deve ser maior que 0"
    assert 0 < PERCENTUAL_MAXIMO_ABANDONO <= 100, "PERCENTUAL_MAXIMO_ABANDONO deve estar entre 1 e 100"
    assert PERCENTUAL_MINIMO_CONCLUSAO >= 0, "PERCENTUAL_MINIMO_CONCLUSAO deve ser >= 0"
    assert TOP_N_CURSOS > 0, "TOP_N_CURSOS deve ser maior que 0"
    assert TOP_N_DISCIPLINAS > 0, "TOP_N_DISCIPLINAS deve ser maior que 0"
    assert isinstance(APENAS_SEM_TERMINO, bool), "APENAS_SEM_TERMINO deve ser True ou False"
    print("✅ Configurações validadas com sucesso!")
    return True

if __name__ == "__main__":
    validar_configuracoes()
    print("\nConfigurações atuais:")
    print(f"- Dias mínimos para abandono: {DIAS_MINIMOS_ABANDONO}")
    print(f"- Percentual máximo abandono: {PERCENTUAL_MAXIMO_ABANDONO}%")
    print(f"- Apenas sem término: {APENAS_SEM_TERMINO}")
    print(f"- Top N cursos: {TOP_N_CURSOS}")
    print(f"- Top N disciplinas: {TOP_N_DISCIPLINAS}")
    print(f"- Senha: {'*' * len(SENHA_DASHBOARD)}")
