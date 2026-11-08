import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import qrcode
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Leilão OPC | Soul (Joe Gardner)",
    page_icon="🎷",
    layout="wide"
)

ARQUIVO_DADOS = "lances_turma.json"

# Funções de persistência compartilhada (todos os celulares gravam no mesmo lugar)
def carregar_lances():
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_lance(novo_lance):
    dados = carregar_lances()
    dados.append(novo_lance)
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def limpar_lances():
    if os.path.exists(ARQUIVO_DADOS):
        os.remove(ARQUIVO_DADOS)

LOTES = [
    {
        "titulo": "Lote 1: O Palco da Dorothea (Prestígio & Fama)",
        "desc": "Aplausos, reconhecimento artístico internacional e viver do jazz.",
        "teoria": "Tipo Artístico Puro (Holland) / Foco no Sucesso Externo"
    },
    {
        "titulo": "Lote 2: A Cadeira Efetiva na Escola (Estabilidade)",
        "desc": "Contrato integral, plano de saúde, previdência e rotina garantida.",
        "teoria": "Mandato Materno (Libba) / Necessidade de Segurança (Super)"
    },
    {
        "titulo": "Lote 3: A Faísca da Connie (Impacto Social & Educação)",
        "desc": "O prazer de ensinar, formar jovens e transformar potenciais.",
        "teoria": "Tipo Social (Holland) / Papel Educador e Generatividade"
    },
    {
        "titulo": "Lote 4: A Alfaiataria da Libba (Autonomia Empresarial)",
        "desc": "Comandar o próprio negócio independente e honrar as raízes.",
        "teoria": "Tipo Empreendedor / Lealdade Familiar (Bohoslavsky)"
    },
    {
        "titulo": "Lote 5: 'Caminhar no Outono' (Equilíbrio & Viver o Presente)",
        "desc": "Apreciar uma fatia de pizza, o vento, a rotina sem cobrança de metas.",
        "teoria": "Papéis de Vida: Cidadão e Lazer (Super) / Vida Integral"
    },
    {
        "titulo": "Lote 6: A Carreira em Mosaico (Equilíbrio Dinâmico)",
        "desc": "Manter a escola durante o dia e os shows à noite de forma sustentável.",
        "teoria": "Maturidade de Carreira / Integração de Múltiplos Papéis"
    }
]

st.title("🎷 Dinâmica Coletiva de OPC: O Leilão de Joe Gardner")
st.caption("Acesse com seu celular, vote no valor que você priorizaria e veja o resultado consolidado da turma!")

aba_voto, aba_telao, aba_reflexao = st.tabs(["📱 Votar pelo Celular", "📊 Telão da Turma (Tempo Real)", "🧠 Discussão Clínica"])

# --- ABA 1: TELA DE VOTO DOS ALUNOS ---
with aba_voto:
    st.subheader("Faça seu Lance no Leilão")
    st.write("Cada participante tem **1.000 moedas simbólicas** para investir no valor mais indispensável.")
    
    with st.form("form_participante"):
        nome = st.text_input("Seu Nome (ou da sua dupla):", placeholder="Ex: Lucas & Marina")
        escolha = st.selectbox("Qual Lote você arremata com prioridade?", [l["titulo"] for l in LOTES])
        moedas = st.slider("Quantas moedas do seu saldo você aposta nesse lote?", 50, 1000, 400, 50)
        
        btn_enviar = st.form_submit_button("🔨 Confirmar e Enviar para o Telão")
        
        if btn_enviar:
            if not nome.strip():
                st.error("Digite seu nome antes de enviar!")
            else:
                salvar_lance({"nome": nome.strip(), "lote": escolha, "moedas": moedas})
                st.success(f"Lance de {moedas} moedas enviado com sucesso! Olhe no telão.")

    st.markdown("---")
    st.write("#### Entenda o que está em jogo nos Lotes:")
    for l in LOTES:
        st.markdown(f"**{l['titulo']}** — *{l['desc']}*  \n`Fundamento:` {l['teoria']}")

# --- ABA 2: TELÃO DO PROFESSOR / TURMA ---
with aba_telao:
    col_qr, col_stats = st.columns([1, 2])
    
    with col_qr:
        st.write("#### 📲 Conecte a Turma")
        url_input = st.text_input("Cole aqui a URL pública do seu app:", placeholder="http://192.168.1.5:8501 ou link da nuvem")
        if url_input:
            qr = qrcode.make(url_input)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="Aponte a câmera do celular para entrar", width=220)
        else:
            st.info("Digite ou cole a URL acima para gerar o QR Code no telão.")

    dados_atuais = carregar_lances()
    
    with col_stats:
        st.write("#### 📈 Painel Geral")
        if not dados_atuais:
            st.warning("Aguardando os primeiros votos dos alunos...")
        else:
            df = pd.DataFrame(dados_atuais)
            m1, m2 = st.columns(2)
            m1.metric("Votos Computados", len(df))
            m2.metric("Total de Moedas em Circulação", f"{df['moedas'].sum():,}")

    if dados_atuais:
        df = pd.DataFrame(dados_atuais)
        
        # Gráfico consolidado
        totais = df.groupby("lote")["moedas"].sum().reset_index()
        fig = px.bar(
            totais,
            x="moedas",
            y="lote",
            orientation="h",
            title="Valores Mais Disputados na Turma",
            labels={"moedas": "Moedas Investidas", "lote": "Lote Ocupacional"},
            color="moedas",
            color_continuous_scale="Purples"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Ver lista de todos os lances individuais"):
            st.dataframe(df, use_container_width=True)
            
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🔄 Atualizar Resultados"):
            st.rerun()
    with col_btn2:
        if st.button("🗑️ Reiniciar Dinâmica (Zerar Votos)"):
            limpar_lances()
            st.rerun()

# --- ABA 3: AMARRAÇÃO CLÍNICA COM O FILME ---
with aba_reflexao:
    st.markdown("""
    ### 🎬 Fechamento Clínico: Devolutiva para o Caso Joe Gardner
    * **Se a sala investiu muito no Lote 1 (Dorothea):** Discuta a armadilha do *mito do propósito único*. Joe acreditava que, ao tocar com Dorothea, todos os problemas dele sumiriam. Quando o show acaba, ele pergunta: *"E agora?"* — e Dorothea conta a parábola do peixinho procurando o oceano.
    * **Se a sala escolheu o Lote 2 ou 4 (Estabilidade/Alfaiataria):** Mostre como as pressões da mãe Libba refletiam o medo da precariedade, algo frequente na clínica de OPC com famílias trabalhadoras.
    * **Se a sala valorizou o Lote 3 ou 5 (Ensino e Apreciação da Vida):** Destaque a virada de Donald Super e Bohoslavsky: vocação não é uma prisão; o trabalho é apenas um dos papéis de vida.
    """)