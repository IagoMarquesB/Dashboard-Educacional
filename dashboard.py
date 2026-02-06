import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib

# Importar configurações
try:
    from config import (
        DIAS_MINIMOS_ABANDONO, 
        PERCENTUAL_MAXIMO_ABANDONO,
        APENAS_SEM_TERMINO,
        TOP_N_CURSOS,
        TOP_N_DISCIPLINAS,
        TOP_N_DISCIPLINAS_ACESSO,
        MIN_AVALIACOES_NOTA,
        MIN_MATRICULAS_TAXA,
        ABANDONO_INICIAL_PERCENTUAL,
        BINS_HISTOGRAMA_ABANDONO,
        SENHA_DASHBOARD,
        CORES
    )
except ImportError:
    # Valores padrão caso o arquivo de configuração não exista
    DIAS_MINIMOS_ABANDONO = 30
    PERCENTUAL_MAXIMO_ABANDONO = 50
    APENAS_SEM_TERMINO = True
    TOP_N_CURSOS = 10
    TOP_N_DISCIPLINAS = 20
    TOP_N_DISCIPLINAS_ACESSO = 15
    MIN_AVALIACOES_NOTA = 5
    MIN_MATRICULAS_TAXA = 10
    ABANDONO_INICIAL_PERCENTUAL = 20
    BINS_HISTOGRAMA_ABANDONO = 20
    SENHA_DASHBOARD = "admin123"
    CORES = {
        'positivo': 'greens',
        'negativo': 'reds',
        'neutro': 'blues',
        'geral': 'viridis',
        'destaque': '#2ecc71',
        'alerta': '#e74c3c'
    }

# Configuração da página
st.set_page_config(
    page_title="Dashboard Educacional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sistema de autenticação
def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    
    def password_entered():
        """Verifica se a senha está correta."""
        # Hash da senha configurada
        senha_hash = hashlib.sha256(SENHA_DASHBOARD.encode()).hexdigest()
        
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == senha_hash:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não armazena a senha
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primeira execução, mostra input de senha
        st.title("🔐 Dashboard Educacional - Login")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        st.info("💡 Senha enviada por whatsapp")
        return False
    elif not st.session_state["password_correct"]:
        # Senha incorreta
        st.title("🔐 Dashboard Educacional - Login")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Senha incorreta")
        return False
    else:
        # Senha correta
        return True

if not check_password():
    st.stop()

# Carregar dados
@st.cache_data
def load_data():
    """Carrega os dados dos arquivos CSV e Excel"""
    try:
        # Carregar dados de cursos
        df_cursos = pd.read_csv('Cursos.csv', 
                                encoding='ISO-8859-1', 
                                sep=';',
                                low_memory=False)
        
        # Carregar dados de disciplinas
        df_disciplinas = pd.read_excel('Disciplinas.xlsx')
        
        # Converter status de aluno ativo (1 = Sim, 0 = Não) em ambos os dataframes
        df_cursos['Aluno Ativo'] = df_cursos['Aluno Ativo'].apply(lambda x: 'Sim' if x == 1 else 'Não')
        df_disciplinas['Aluno Ativo'] = df_disciplinas['Aluno Ativo'].apply(lambda x: 'Sim' if x == 1 else 'Não')
        
        # Usar Curso1 (nome completo) em vez de Curso (código)
        df_cursos['Curso'] = df_cursos['Curso1']
        
        # Converter datas
        df_cursos['Data Matrícula'] = pd.to_datetime(df_cursos['Data Matrícula'], 
                                                      format='%d/%m/%Y %H:%M:%S', 
                                                      errors='coerce')
        df_cursos['Primeiro Acesso'] = pd.to_datetime(df_cursos['Primeiro Acesso'], 
                                                       format='%d/%m/%Y %H:%M:%S', 
                                                       errors='coerce')
        df_cursos['Último Acesso'] = pd.to_datetime(df_cursos['Último Acesso'], 
                                                     format='%d/%m/%Y %H:%M:%S', 
                                                     errors='coerce')
        
        df_disciplinas['Data Matrícula'] = pd.to_datetime(df_disciplinas['Data Matrícula'], 
                                                           format='%d/%m/%Y %H:%M:%S', 
                                                           errors='coerce')
        df_disciplinas['Data Início'] = pd.to_datetime(df_disciplinas['Data Início'], 
                                                        errors='coerce')
        df_disciplinas['Data Término'] = pd.to_datetime(df_disciplinas['Data Término'], 
                                                         errors='coerce')
        df_disciplinas['Primeiro Acesso'] = pd.to_datetime(df_disciplinas['Primeiro Acesso'], 
                                                            format='%d/%m/%Y %H:%M:%S', 
                                                            errors='coerce')
        df_disciplinas['Último Acesso'] = pd.to_datetime(df_disciplinas['Último Acesso'], 
                                                          format='%d/%m/%Y %H:%M:%S', 
                                                          errors='coerce')
        
        return df_cursos, df_disciplinas
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None, None

# Carregar dados
df_cursos, df_disciplinas = load_data()

if df_cursos is None or df_disciplinas is None:
    st.stop()

# Sidebar
st.sidebar.title("📊 Dashboard Educacional")
st.sidebar.markdown("---")

# Filtros na sidebar
st.sidebar.header("🔍 Filtros")

# Filtro de curso
cursos_disponiveis = ['Todos'] + sorted(df_cursos['Curso'].dropna().unique().tolist())
curso_selecionado = st.sidebar.selectbox("Selecione o Curso:", cursos_disponiveis)

# Aplicar filtros
df_cursos_filtrado = df_cursos.copy()
df_disciplinas_filtrado = df_disciplinas.copy()

if curso_selecionado != 'Todos':
    df_cursos_filtrado = df_cursos_filtrado[df_cursos_filtrado['Curso'] == curso_selecionado]
    # Filtrar disciplinas pelos IDs de alunos do curso selecionado
    alunos_ids = df_cursos_filtrado['idAluno'].unique()
    df_disciplinas_filtrado = df_disciplinas_filtrado[df_disciplinas_filtrado['idAluno'].isin(alunos_ids)]

st.sidebar.markdown("---")
st.sidebar.info("💡 Use o filtro acima para visualizar dados por curso específico ou veja todos os cursos")

# Título principal
st.title("📊 Dashboard Educacional")
st.markdown("---")

# Menu de navegação
menu = st.sidebar.radio(
    "Navegação:",
    ["📈 Visão Geral", "👥 Análise de Alunos", "📚 Análise de Disciplinas", "📊 Dados Detalhados"]
)

# ============================================
# PÁGINA 1: VISÃO GERAL
# ============================================
if menu == "📈 Visão Geral":
    st.header("📈 Visão Geral")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        alunos_ativos = df_cursos_filtrado[df_cursos_filtrado['Aluno Ativo'] == 'Sim']['idAluno'].nunique()
        st.metric("👤 Alunos Ativos", f"{alunos_ativos:,}")
    
    with col2:
        total_matriculas = len(df_cursos_filtrado)
        st.metric("📝 Total de Matrículas", f"{total_matriculas:,}")
    
    with col3:
        alunos_inativos = df_cursos_filtrado[df_cursos_filtrado['Aluno Ativo'] == 'Não']['idAluno'].nunique()
        st.metric("⛔ Alunos Inativos", f"{alunos_inativos:,}")
    
    with col4:
        cursos_unicos = df_cursos_filtrado['Curso'].nunique()
        st.metric("🎓 Cursos Disponíveis", f"{cursos_unicos:,}")
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição de Alunos por Status")
        status_counts = df_cursos_filtrado['Aluno Ativo'].value_counts()
        fig = px.pie(values=status_counts.values, 
                     names=status_counts.index,
                     title="Alunos Ativos vs Inativos",
                     color_discrete_sequence=['#2ecc71', '#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Top 10 Cursos por Matrículas")
        top_cursos = df_cursos_filtrado['Curso'].value_counts().head(TOP_N_CURSOS)
        fig = px.bar(x=top_cursos.values, 
                     y=top_cursos.index,
                     orientation='h',
                     title="Cursos Mais Procurados",
                     labels={'x': 'Número de Matrículas', 'y': 'Curso'},
                     color=top_cursos.values,
                     color_continuous_scale='viridis')
        fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Evolução temporal
    st.subheader("📈 Evolução de Matrículas Mês a Mês")
    
    df_temp = df_cursos_filtrado[df_cursos_filtrado['Data Matrícula'].notna()].copy()
    df_temp['Ano-Mês'] = df_temp['Data Matrícula'].dt.to_period('M').astype(str)
    
    matriculas_mes = df_temp.groupby('Ano-Mês').size().reset_index(name='Matrículas')
    
    fig = px.line(matriculas_mes, 
                  x='Ano-Mês', 
                  y='Matrículas',
                  title="Evolução Mensal de Matrículas",
                  markers=True)
    fig.update_layout(xaxis_title="Mês", yaxis_title="Número de Matrículas")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Evolução de cancelamentos
    st.subheader("📉 Evolução de Cancelamentos Mês a Mês")
    
    df_cancelados = df_cursos_filtrado[
        (df_cursos_filtrado['Aluno Ativo'] == 'Não') & 
        (df_cursos_filtrado['Data Matrícula'].notna())
    ].copy()
    
    if len(df_cancelados) > 0:
        df_cancelados['Ano-Mês'] = df_cancelados['Data Matrícula'].dt.to_period('M').astype(str)
        cancelamentos_mes = df_cancelados.groupby('Ano-Mês').size().reset_index(name='Cancelamentos')
        
        fig = px.line(cancelamentos_mes, 
                      x='Ano-Mês', 
                      y='Cancelamentos',
                      title="Evolução Mensal de Cancelamentos",
                      markers=True,
                      color_discrete_sequence=['#e74c3c'])
        fig.update_layout(xaxis_title="Mês", yaxis_title="Número de Cancelamentos")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há dados de cancelamentos para o período selecionado")

# ============================================
# PÁGINA 2: ANÁLISE DE ALUNOS
# ============================================
elif menu == "👥 Análise de Alunos":
    st.header("👥 Análise Detalhada de Alunos")
    
    # Alunos ativos por curso
    st.subheader("👤 Quantidade de Alunos Ativos por Curso")
    
    alunos_por_curso = df_cursos_filtrado[df_cursos_filtrado['Aluno Ativo'] == 'Sim'].groupby('Curso')['idAluno'].nunique().reset_index()
    alunos_por_curso.columns = ['Curso', 'Alunos Ativos']
    alunos_por_curso = alunos_por_curso.sort_values('Alunos Ativos', ascending=False)
    
    fig = px.bar(alunos_por_curso, 
                 x='Alunos Ativos', 
                 y='Curso',
                 orientation='h',
                 title="Alunos Ativos por Curso",
                 color='Alunos Ativos',
                 color_continuous_scale='blues')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Cancelamentos por curso
    st.subheader("⛔ Quantidade de Cancelamentos por Curso")
    
    cancelamentos_por_curso = df_cursos_filtrado[df_cursos_filtrado['Aluno Ativo'] == 'Não'].groupby('Curso')['idAluno'].nunique().reset_index()
    cancelamentos_por_curso.columns = ['Curso', 'Cancelamentos']
    cancelamentos_por_curso = cancelamentos_por_curso.sort_values('Cancelamentos', ascending=False)
    
    fig = px.bar(cancelamentos_por_curso, 
                 x='Cancelamentos', 
                 y='Curso',
                 orientation='h',
                 title="Cancelamentos por Curso",
                 color='Cancelamentos',
                 color_continuous_scale='reds')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Matrículas por período
    st.subheader("📅 Matrículas por Período")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Por ano
        df_temp = df_cursos_filtrado[df_cursos_filtrado['Data Matrícula'].notna()].copy()
        df_temp['Ano'] = df_temp['Data Matrícula'].dt.year
        matriculas_ano = df_temp.groupby('Ano').size().reset_index(name='Matrículas')
        
        fig = px.bar(matriculas_ano, 
                     x='Ano', 
                     y='Matrículas',
                     title="Matrículas por Ano",
                     color='Matrículas',
                     color_continuous_scale='greens')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Por trimestre
        df_temp['Trimestre'] = df_temp['Data Matrícula'].dt.quarter
        df_temp['Ano-Trimestre'] = df_temp['Ano'].astype(str) + '-Q' + df_temp['Trimestre'].astype(str)
        matriculas_trimestre = df_temp.groupby('Ano-Trimestre').size().reset_index(name='Matrículas')
        
        fig = px.bar(matriculas_trimestre, 
                     x='Ano-Trimestre', 
                     y='Matrículas',
                     title="Matrículas por Trimestre",
                     color='Matrículas',
                     color_continuous_scale='oranges')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Taxa de retenção/cancelamento
    st.subheader("📊 Taxa de Retenção vs Cancelamento")
    
    total_alunos = df_cursos_filtrado['idAluno'].nunique()
    ativos = df_cursos_filtrado[df_cursos_filtrado['Aluno Ativo'] == 'Sim']['idAluno'].nunique()
    inativos = df_cursos_filtrado[df_cursos_filtrado['Aluno Ativo'] == 'Não']['idAluno'].nunique()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Alunos Únicos", f"{total_alunos:,}")
    
    with col2:
        taxa_retencao = (ativos / total_alunos * 100) if total_alunos > 0 else 0
        st.metric("Taxa de Retenção", f"{taxa_retencao:.1f}%", delta=None)
    
    with col3:
        taxa_cancelamento = (inativos / total_alunos * 100) if total_alunos > 0 else 0
        st.metric("Taxa de Cancelamento", f"{taxa_cancelamento:.1f}%", delta=None)

# ============================================
# PÁGINA 3: ANÁLISE DE DISCIPLINAS
# ============================================
elif menu == "📚 Análise de Disciplinas":
    st.header("📚 Análise Detalhada de Disciplinas")
    
    # Notas médias por disciplina
    st.subheader("📊 Notas Médias por Disciplina")
    
    # Filtrar disciplinas com notas
    df_com_notas = df_disciplinas_filtrado[df_disciplinas_filtrado['Nota de Aproveitamento Final'].notna()].copy()
    
    if len(df_com_notas) > 0:
        notas_por_disciplina = df_com_notas.groupby('Disciplina')['Nota de Aproveitamento Final'].agg(['mean', 'count']).reset_index()
        notas_por_disciplina.columns = ['Disciplina', 'Nota Média', 'Quantidade de Avaliações']
        notas_por_disciplina = notas_por_disciplina.sort_values('Nota Média', ascending=False)
        
        # Top 20 disciplinas por nota média (com pelo menos X avaliações)
        top_notas = notas_por_disciplina[notas_por_disciplina['Quantidade de Avaliações'] >= MIN_AVALIACOES_NOTA].head(TOP_N_DISCIPLINAS)
        
        fig = px.bar(top_notas, 
                     x='Nota Média', 
                     y='Disciplina',
                     orientation='h',
                     title=f"Top {TOP_N_DISCIPLINAS} Disciplinas por Nota Média (mínimo {MIN_AVALIACOES_NOTA} avaliações)",
                     color='Nota Média',
                     color_continuous_scale='RdYlGn',
                     hover_data=['Quantidade de Avaliações'])
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        with st.expander("📋 Ver tabela completa de notas por disciplina"):
            st.dataframe(
                notas_por_disciplina.style.background_gradient(subset=['Nota Média'], cmap='RdYlGn'),
                use_container_width=True
            )
    else:
        st.warning("Não há dados de notas disponíveis para o filtro selecionado")
    
    st.markdown("---")
    
    # Disciplinas mais concluídas
    st.subheader("✅ Disciplinas Mais Concluídas")
    
    df_concluidas = df_disciplinas_filtrado[df_disciplinas_filtrado['Percentual Concluído'] == 100].copy()
    
    if len(df_concluidas) > 0:
        conclusoes_por_disciplina = df_concluidas['Disciplina'].value_counts().head(TOP_N_DISCIPLINAS).reset_index()
        conclusoes_por_disciplina.columns = ['Disciplina', 'Conclusões']
        
        fig = px.bar(conclusoes_por_disciplina, 
                     x='Conclusões', 
                     y='Disciplina',
                     orientation='h',
                     title=f"Top {TOP_N_DISCIPLINAS} Disciplinas Mais Concluídas",
                     color='Conclusões',
                     color_continuous_scale=CORES['positivo'],
                     height=600)  # Aumentar altura
        fig.update_layout(
            yaxis={'categoryorder':'total ascending'},
            showlegend=False,
            margin=dict(l=300, r=50, t=50, b=50)  # Margem esquerda maior para nomes
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há dados de conclusões para o filtro selecionado")
    
    st.markdown("---")
    
    # Disciplinas: Análise por Status de Engajamento
    st.subheader("⚠️ Análise de Engajamento nas Disciplinas")
    
    # Considerar apenas disciplinas liberadas há mais de X dias (configurável)
    data_limite = datetime.now() - timedelta(days=DIAS_MINIMOS_ABANDONO)
    
    # Filtro base: disciplinas liberadas há mais de X dias e sem término
    df_base = df_disciplinas_filtrado[
        (df_disciplinas_filtrado['Liberado a Partir De'].notna()) &
        (pd.to_datetime(df_disciplinas_filtrado['Liberado a Partir De'], errors='coerce') < data_limite) &
        (df_disciplinas_filtrado['Data Término'].isna()) &
        (df_disciplinas_filtrado['Percentual Concluído'] < PERCENTUAL_MAXIMO_ABANDONO)
    ].copy()
    
    if len(df_base) > 0:
        # Categoria 1: NÃO INICIADAS (0% e nunca acessou)
        df_nao_iniciadas = df_base[
            (df_base['Percentual Concluído'] == 0) & 
            (df_base['Último Acesso'].isna())
        ].copy()
        
        # Categoria 2: VISUALIZADAS APENAS (0% mas acessou)
        df_visualizadas = df_base[
            (df_base['Percentual Concluído'] == 0) & 
            (df_base['Último Acesso'].notna())
        ].copy()
        
        # Categoria 3: ABANDONADAS (começou mas parou - >0% e <50%)
        df_abandonadas_real = df_base[
            (df_base['Percentual Concluído'] > 0) & 
            (df_base['Percentual Concluído'] < PERCENTUAL_MAXIMO_ABANDONO)
        ].copy()
        
        # Mostrar resumo em cards
        st.info(f"💡 **Análise de disciplinas liberadas há mais de {DIAS_MINIMOS_ABANDONO} dias** (antes de {data_limite.strftime('%d/%m/%Y')}) e com menos de {PERCENTUAL_MAXIMO_ABANDONO}% de conclusão.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🔴 Não Iniciadas", 
                f"{len(df_nao_iniciadas):,}",
                help="Disciplinas liberadas mas nunca acessadas pelo aluno"
            )
        
        with col2:
            st.metric(
                "🟡 Apenas Visualizadas", 
                f"{len(df_visualizadas):,}",
                help="Aluno acessou mas não começou (0% concluído)"
            )
        
        with col3:
            st.metric(
                "🟠 Abandonadas", 
                f"{len(df_abandonadas_real):,}",
                help="Aluno começou mas abandonou (>0% e <50% concluído)"
            )
        
        st.markdown("---")
        
        # Tabs para cada categoria
        tab1, tab2, tab3 = st.tabs(["🔴 Não Iniciadas", "🟡 Visualizadas Apenas", "🟠 Abandonadas"])
        
        # TAB 1: NÃO INICIADAS
        with tab1:
            st.subheader("Disciplinas Não Iniciadas")
            st.caption("Disciplinas que foram liberadas mas o aluno nunca acessou")
            
            if len(df_nao_iniciadas) > 0:
                nao_iniciadas_ranking = df_nao_iniciadas['Disciplina'].value_counts().head(TOP_N_DISCIPLINAS).reset_index()
                nao_iniciadas_ranking.columns = ['Disciplina', 'Quantidade']
                
                fig = px.bar(nao_iniciadas_ranking, 
                             x='Quantidade', 
                             y='Disciplina',
                             orientation='h',
                             title=f"Top {TOP_N_DISCIPLINAS} Disciplinas Não Iniciadas",
                             color='Quantidade',
                             color_continuous_scale='Greys',
                             height=600)
                fig.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False,
                    margin=dict(l=300, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas
                pct_nao_iniciadas = (len(df_nao_iniciadas) / len(df_base) * 100) if len(df_base) > 0 else 0
                st.info(f"📊 **{pct_nao_iniciadas:.1f}%** das disciplinas elegíveis nunca foram iniciadas")
            else:
                st.success("✅ Todas as disciplinas foram pelo menos acessadas!")
        
        # TAB 2: VISUALIZADAS APENAS
        with tab2:
            st.subheader("Disciplinas Apenas Visualizadas")
            st.caption("Aluno acessou a disciplina mas não iniciou o conteúdo (0% de conclusão)")
            
            if len(df_visualizadas) > 0:
                visualizadas_ranking = df_visualizadas['Disciplina'].value_counts().head(TOP_N_DISCIPLINAS).reset_index()
                visualizadas_ranking.columns = ['Disciplina', 'Quantidade']
                
                fig = px.bar(visualizadas_ranking, 
                             x='Quantidade', 
                             y='Disciplina',
                             orientation='h',
                             title=f"Top {TOP_N_DISCIPLINAS} Disciplinas Apenas Visualizadas",
                             color='Quantidade',
                             color_continuous_scale='YlOrRd',
                             height=600)
                fig.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False,
                    margin=dict(l=300, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas
                pct_visualizadas = (len(df_visualizadas) / len(df_base) * 100) if len(df_base) > 0 else 0
                st.warning(f"⚠️ **{pct_visualizadas:.1f}%** das disciplinas foram apenas visualizadas sem início efetivo")
                
                # Insight adicional
                st.info("💡 **Insight pedagógico:** Estas disciplinas podem ter conteúdo inicial pouco engajador ou instruções pouco claras sobre como começar.")
            else:
                st.success("✅ Alunos que acessam sempre iniciam o conteúdo!")
        
        # TAB 3: ABANDONADAS (REAL)
        with tab3:
            st.subheader("Disciplinas Abandonadas")
            st.caption("Aluno começou a disciplina mas abandonou antes de completar 50%")
            
            if len(df_abandonadas_real) > 0:
                abandonadas_ranking = df_abandonadas_real['Disciplina'].value_counts().head(TOP_N_DISCIPLINAS).reset_index()
                abandonadas_ranking.columns = ['Disciplina', 'Abandonos']
                
                fig = px.bar(abandonadas_ranking, 
                             x='Abandonos', 
                             y='Disciplina',
                             orientation='h',
                             title=f"Top {TOP_N_DISCIPLINAS} Disciplinas Abandonadas",
                             color='Abandonos',
                             color_continuous_scale=CORES['negativo'],
                             height=600)
                fig.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False,
                    margin=dict(l=300, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise do momento de abandono
                st.subheader("📉 Momento do Abandono")
                
                # Criar faixas mais significativas
                df_abandonadas_real['Faixa de Abandono'] = pd.cut(
                    df_abandonadas_real['Percentual Concluído'], 
                    bins=[0, 10, 20, 30, 40, 50],
                    labels=['1-10%', '11-20%', '21-30%', '31-40%', '41-50%']
                )
                
                faixas_abandono = df_abandonadas_real['Faixa de Abandono'].value_counts().sort_index().reset_index()
                faixas_abandono.columns = ['Faixa', 'Quantidade']
                
                fig = px.bar(faixas_abandono, 
                            x='Faixa', 
                            y='Quantidade',
                            title="Distribuição de Abandonos por Faixa de Conclusão",
                            labels={'Faixa': 'Faixa de Conclusão (%)', 'Quantidade': 'Número de Abandonos'},
                            color='Quantidade',
                            color_continuous_scale=CORES['negativo'])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas de abandono
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    media_abandono = df_abandonadas_real['Percentual Concluído'].mean()
                    st.metric("Média de Conclusão ao Abandonar", f"{media_abandono:.1f}%")
                
                with col2:
                    mediana_abandono = df_abandonadas_real['Percentual Concluído'].median()
                    st.metric("Mediana de Conclusão ao Abandonar", f"{mediana_abandono:.1f}%")
                
                with col3:
                    abandono_inicial = len(df_abandonadas_real[df_abandonadas_real['Percentual Concluído'] < ABANDONO_INICIAL_PERCENTUAL])
                    pct_abandono_inicial = (abandono_inicial / len(df_abandonadas_real) * 100) if len(df_abandonadas_real) > 0 else 0
                    st.metric(f"Abandonos Iniciais (< {ABANDONO_INICIAL_PERCENTUAL}%)", f"{pct_abandono_inicial:.1f}%")
                
                # Insight
                pct_abandonadas = (len(df_abandonadas_real) / len(df_base) * 100) if len(df_base) > 0 else 0
                st.error(f"🚨 **{pct_abandonadas:.1f}%** das disciplinas foram iniciadas mas abandonadas antes de completar {PERCENTUAL_MAXIMO_ABANDONO}%")
                
            else:
                st.success("✅ Nenhuma disciplina foi abandonada após início!")
        
        st.markdown("---")
        
        # Gráfico de pizza com a distribuição geral
        st.subheader("📊 Distribuição Geral de Status")
        
        distribuicao = pd.DataFrame({
            'Status': ['Não Iniciadas', 'Visualizadas Apenas', 'Abandonadas'],
            'Quantidade': [len(df_nao_iniciadas), len(df_visualizadas), len(df_abandonadas_real)]
        })
        
        fig = px.pie(distribuicao, 
                     values='Quantidade', 
                     names='Status',
                     title=f'Distribuição de Disciplinas Incompletas (liberadas há +{DIAS_MINIMOS_ABANDONO} dias)',
                     color='Status',
                     color_discrete_map={
                         'Não Iniciadas': '#95a5a6',
                         'Visualizadas Apenas': '#f39c12', 
                         'Abandonadas': '#e74c3c'
                     },
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info(f"Não há disciplinas elegíveis para análise (liberadas há mais de {DIAS_MINIMOS_ABANDONO} dias)")
    
    st.markdown("---")
    
    # Análise de acessos
    st.subheader("👁️ Análise de Acessos às Disciplinas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Disciplinas com mais acessos (baseado em último acesso recente)
        df_acessos = df_disciplinas_filtrado[df_disciplinas_filtrado['Último Acesso'].notna()].copy()
        
        if len(df_acessos) > 0:
            acessos_por_disciplina = df_acessos.groupby('Disciplina').size().sort_values(ascending=False).head(TOP_N_DISCIPLINAS_ACESSO).reset_index()
            acessos_por_disciplina.columns = ['Disciplina', 'Total de Acessos']
            
            fig = px.bar(acessos_por_disciplina, 
                         y='Disciplina', 
                         x='Total de Acessos',
                         orientation='h',
                         title=f"Top {TOP_N_DISCIPLINAS_ACESSO} Disciplinas Mais Acessadas",
                         color='Total de Acessos',
                         color_continuous_scale=CORES['neutro'])
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados de acesso disponíveis")
    
    with col2:
        # Taxa de conclusão por disciplina (top 15)
        df_temp = df_disciplinas_filtrado.groupby('Disciplina').agg({
            'Percentual Concluído': 'mean',
            'idAluno': 'count'
        }).reset_index()
        df_temp.columns = ['Disciplina', 'Taxa Média de Conclusão', 'Total de Matrículas']
        df_temp = df_temp[df_temp['Total de Matrículas'] >= MIN_MATRICULAS_TAXA].sort_values('Taxa Média de Conclusão', ascending=False).head(TOP_N_DISCIPLINAS_ACESSO)
        
        if len(df_temp) > 0:
            fig = px.bar(df_temp, 
                         y='Disciplina', 
                         x='Taxa Média de Conclusão',
                         orientation='h',
                         title=f"Top {TOP_N_DISCIPLINAS_ACESSO} Disciplinas por Taxa Média de Conclusão",
                         color='Taxa Média de Conclusão',
                         color_continuous_scale=CORES['positivo'],
                         hover_data=['Total de Matrículas'])
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para calcular taxa de conclusão")
    
    st.markdown("---")
    
    # Tempo médio de conclusão
    st.subheader("⏱️ Tempo Médio de Conclusão das Disciplinas")
    
    df_tempo = df_disciplinas_filtrado[
        (df_disciplinas_filtrado['Data Início'].notna()) & 
        (df_disciplinas_filtrado['Data Término'].notna())
    ].copy()
    
    if len(df_tempo) > 0:
        df_tempo['Dias para Conclusão'] = (df_tempo['Data Término'] - df_tempo['Data Início']).dt.days
        df_tempo = df_tempo[df_tempo['Dias para Conclusão'] >= 0]  # Remover valores negativos
        
        tempo_por_disciplina = df_tempo.groupby('Disciplina').agg({
            'Dias para Conclusão': ['mean', 'count']
        }).reset_index()
        tempo_por_disciplina.columns = ['Disciplina', 'Média de Dias', 'Quantidade']
        tempo_por_disciplina = tempo_por_disciplina[tempo_por_disciplina['Quantidade'] >= MIN_AVALIACOES_NOTA]
        tempo_por_disciplina = tempo_por_disciplina.sort_values('Média de Dias').head(TOP_N_DISCIPLINAS)
        
        if len(tempo_por_disciplina) > 0:
            fig = px.bar(tempo_por_disciplina, 
                         y='Disciplina', 
                         x='Média de Dias',
                         orientation='h',
                         title=f"Top {TOP_N_DISCIPLINAS} Disciplinas por Tempo Médio de Conclusão (mínimo {MIN_AVALIACOES_NOTA} conclusões)",
                         color='Média de Dias',
                         color_continuous_scale=CORES['geral'],
                         hover_data=['Quantidade'])
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise de tempo de conclusão")
    else:
        st.info("Não há dados de tempo de conclusão disponíveis")

# ============================================
# PÁGINA 4: DADOS DETALHADOS
# ============================================
elif menu == "📊 Dados Detalhados":
    st.header("📊 Visualização Detalhada dos Dados")
    
    tab1, tab2 = st.tabs(["📋 Dados de Cursos", "📚 Dados de Disciplinas"])
    
    with tab1:
        st.subheader("Dados de Cursos e Alunos")
        
        # Seletor de colunas
        colunas_disponiveis = df_cursos_filtrado.columns.tolist()
        colunas_default = ['idAluno', 'Matrícula', 'Nome', 'Curso', 'Data Matrícula', 
                          'Aluno Ativo', 'Situação', 'Primeiro Acesso', 'Último Acesso']
        colunas_default = [col for col in colunas_default if col in colunas_disponiveis]
        
        colunas_selecionadas = st.multiselect(
            "Selecione as colunas para exibir:",
            colunas_disponiveis,
            default=colunas_default
        )
        
        if colunas_selecionadas:
            # Exibir dataframe
            st.dataframe(
                df_cursos_filtrado[colunas_selecionadas],
                use_container_width=True,
                height=400
            )
            
            # Download
            csv = df_cursos_filtrado[colunas_selecionadas].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="dados_cursos.csv",
                mime="text/csv"
            )
        else:
            st.warning("Selecione pelo menos uma coluna para exibir")
    
    with tab2:
        st.subheader("Dados de Disciplinas")
        
        # Seletor de colunas
        colunas_disponiveis = df_disciplinas_filtrado.columns.tolist()
        colunas_default = ['idAluno', 'Matrícula', 'Nome', 'Disciplina', 'Percentual Concluído',
                          'Nota de Aproveitamento Final', 'Data Início', 'Data Término', 'Legenda']
        colunas_default = [col for col in colunas_default if col in colunas_disponiveis]
        
        colunas_selecionadas = st.multiselect(
            "Selecione as colunas para exibir:",
            colunas_disponiveis,
            default=colunas_default,
            key="disciplinas_cols"
        )
        
        if colunas_selecionadas:
            # Exibir dataframe
            st.dataframe(
                df_disciplinas_filtrado[colunas_selecionadas],
                use_container_width=True,
                height=400
            )
            
            # Download
            csv = df_disciplinas_filtrado[colunas_selecionadas].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="dados_disciplinas.csv",
                mime="text/csv",
                key="download_disciplinas"
            )
        else:
            st.warning("Selecione pelo menos uma coluna para exibir")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Dashboard Educacional | Desenvolvido com Streamlit e Plotly</p>
        <p>💡 Dica: Use os filtros na barra lateral para explorar os dados</p>
    </div>
    """,
    unsafe_allow_html=True
)
