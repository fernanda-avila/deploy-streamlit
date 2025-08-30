
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Google Play Store Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar e transformar dados
@st.cache_data
def load_and_transform_data():
    df = pd.read_csv('googleplaystore.csv')
    
    # 1. Remover linhas duplicadas
    df = df.drop_duplicates()
    print(f"Linhas após remover duplicatas: {len(df)}")
    
    # 2. Transformar coluna Installs
    df['Installs'] = df['Installs'].astype(str)
    df['Installs'] = df['Installs'].str.replace('+', '', regex=False)
    df['Installs'] = df['Installs'].str.replace(',', '', regex=False)
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')
    
    # 3. Transformar coluna Price
    df['Price'] = df['Price'].astype(str)
    df['Price'] = df['Price'].str.replace('$', '', regex=False)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    
    # 4. Transformar coluna Reviews
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
    
    # 5. Criar coluna Type baseada em Price
    df['Type'] = df['Price'].apply(lambda x: 'Paid' if x > 0 else 'Free')
    
    # 6. Limpar coluna Size (opcional)
    if 'Size' in df.columns:
        df['Size'] = df['Size'].astype(str)
        df['Size'] = df['Size'].str.replace('M', '', regex=False)
        df['Size'] = df['Size'].str.replace('k', '', regex=False)
        df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
    
    # 7. Remover linhas com valores críticos nulos
    df = df.dropna(subset=['Installs', 'Rating', 'Price'])
    
    print("✅ Dados transformados com sucesso!")
    print(f"📊 Total de apps: {len(df)}")
    print(f"💰 Apps gratuitos: {len(df[df['Type'] == 'Free'])}")
    print(f"💵 Apps pagos: {len(df[df['Type'] == 'Paid'])}")
    
    return df

# Carregar dados
df = load_and_transform_data()

# Sidebar
st.sidebar.title("📊 Filtros")
st.sidebar.markdown("---")

# Filtro por categoria
categories = ['Todas'] + sorted(df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox(
    "Selecione a Categoria:",
    categories
)

# Filtro por tipo
app_type = st.sidebar.selectbox(
    "Tipo de App:",
    ['Todos', 'Free', 'Paid']
)

# Filtro por preço
max_price = df['Price'].max()
price_range = st.sidebar.slider(
    "Faixa de Preço (USD):",
    min_value=0.0,
    max_value=float(max_price),
    value=(0.0, min(50.0, max_price))
)

# Filtro por rating
rating_range = st.sidebar.slider(
    "Faixa de Rating:",
    min_value=0.0,
    max_value=5.0,
    value=(3.0, 5.0),
    step=0.1
)

# Filtro por instalações
min_installs = int(df['Installs'].min())
max_installs = int(df['Installs'].max())
installs_range = st.sidebar.slider(
    "Faixa de Instalações:",
    min_value=min_installs,
    max_value=max_installs,
    value=(min_installs, max_installs),
    step=1000000
)

# Aplicar filtros
filtered_df = df.copy()

if selected_category != 'Todas':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

if app_type != 'Todos':
    filtered_df = filtered_df[filtered_df['Type'] == app_type]

filtered_df = filtered_df[
    (filtered_df['Price'] >= price_range[0]) & 
    (filtered_df['Price'] <= price_range[1]) &
    (filtered_df['Rating'] >= rating_range[0]) & 
    (filtered_df['Rating'] <= rating_range[1]) &
    (filtered_df['Installs'] >= installs_range[0]) & 
    (filtered_df['Installs'] <= installs_range[1])
]

# Layout principal
st.title("📱 Google Play Store Analytics Dashboard")
st.markdown("---")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Apps", f"{len(filtered_df):,}")

with col2:
    avg_rating = filtered_df['Rating'].mean()
    st.metric("Rating Médio", f"{avg_rating:.2f}")

with col3:
    total_installs = filtered_df['Installs'].sum()
    st.metric("Total de Instalações", f"{total_installs:,.0f}")

with col4:
    paid_apps = len(filtered_df[filtered_df['Type'] == 'Paid'])
    st.metric("Apps Pagos", f"{paid_apps:,}")

# Gráficos - Primeira linha
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Distribuição por Categoria")
    if len(filtered_df) > 0:
        category_counts = filtered_df['Category'].value_counts().head(10)
        fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            labels={'x': 'Número de Apps', 'y': 'Categoria'},
            color=category_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir com os filtros atuais")

with col2:
    st.subheader(" Distribuição de Ratings")
    if len(filtered_df) > 0:
        fig = px.histogram(
            filtered_df, 
            x='Rating', 
            nbins=20,
            labels={'Rating': 'Avaliação', 'count': 'Número de Apps'},
            color_discrete_sequence=['#FF6B6B']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir")

# Gráficos - Segunda linha
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Distribuição de Preços")
    paid_apps_filtered = filtered_df[filtered_df['Type'] == 'Paid']
    if len(paid_apps_filtered) > 0:
        fig = px.histogram(
            paid_apps_filtered, 
            x='Price', 
            nbins=20,
            labels={'Price': 'Preço (USD)', 'count': 'Número de Apps'},
            color_discrete_sequence=['#4ECDC4']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há apps pagos nos filtros selecionados")

with col2:
    st.subheader(" Top 10 Apps por Instalações")
    if len(filtered_df) > 0:
        top_apps = filtered_df.nlargest(10, 'Installs')
        fig = px.bar(
            top_apps,
            x='Installs',
            y='App',
            orientation='h',
            labels={'Installs': 'Instalações', 'App': 'Aplicativo'},
            color='Installs',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir")

# Gráfico de pizza para Type
st.subheader("Free vs Paid Distribuição Gratuito/Pago")
if len(filtered_df) > 0:
    free_vs_paid = filtered_df['Type'].value_counts()
    fig = px.pie(
        values=free_vs_paid.values,
        names=free_vs_paid.index,
        color=free_vs_paid.index,
        color_discrete_map={'Free': '#2ECC71', 'Paid': '#E74C3C'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir")

# Scatter plot: Rating vs Price
st.subheader(" Relação: Rating vs Preço")
if len(filtered_df) > 0:
    fig = px.scatter(
        filtered_df,
        x='Price',
        y='Rating',
        color='Type',
        size='Installs',
        hover_data=['App', 'Category'],
        labels={'Price': 'Preço (USD)', 'Rating': 'Avaliação'},
        color_discrete_map={'Free': '#2ECC71', 'Paid': '#E74C3C'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Tabela com dados
st.subheader(" Dados Filtrados")
if len(filtered_df) > 0:
    st.dataframe(
        filtered_df[['App', 'Category', 'Rating', 'Reviews', 'Installs', 'Price', 'Type']].head(20),
        height=300,
        use_container_width=True
    )
else:
    st.warning("Nenhum dado para exibir na tabela")

# Estatísticas detalhadas
st.subheader(" Estatísticas Detalhadas")
if len(filtered_df) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Categoria Mais Popular:**")
        st.write(filtered_df['Category'].value_counts().index[0])
        
    with col2:
        st.write("**App Mais Caro:**")
        most_expensive = filtered_df[filtered_df['Price'] == filtered_df['Price'].max()]
        if len(most_expensive) > 0:
            st.write(f"{most_expensive['App'].iloc[0]} (${most_expensive['Price'].iloc[0]:.2f})")
        else:
            st.write("Nenhum app pago")
        
    with col3:
        st.write("**App Melhor Avaliado:**")
        best_rated = filtered_df[filtered_df['Rating'] == filtered_df['Rating'].max()]
        if len(best_rated) > 0:
            st.write(f"{best_rated['App'].iloc[0]} ({best_rated['Rating'].iloc[0]}/5)")
        else:
            st.write("Nenhum app com rating")

# Informações do dataset
st.sidebar.markdown("---")
st.sidebar.info("""
** Estatísticas do Dataset:**
- Total de Apps: {:,}
- Apps Gratuitos: {:,}
- Apps Pagos: {:,}
- Rating Médio: {:.2f}
""".format(len(df), 
          len(df[df['Type'] == 'Free']), 
          len(df[df['Type'] == 'Paid']), 
          df['Rating'].mean()))


st.markdown("---")
st.caption("Dashboard criado com Streamlit | Análise de Dados da Google Play Store | Dados transformados e limpos")

# Botão para download dos dados filtrados
if len(filtered_df) > 0:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download dos Dados Filtrados",
        data=csv,
        file_name="google_play_filtered_data.csv",
        mime="text/csv"
    )