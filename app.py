
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import io

def extrair_texto_pdf(arquivo_pdf):
    texto = ""
    with fitz.open(stream=arquivo_pdf.read(), filetype="pdf") as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

def extrair_disciplinas_e_notas(texto):
    padrao = re.compile(r"(?P<disciplina>[\wçãáéíóú\s\.\(\)-]{3,}):?\s+(?P<notas>(?:\d{1,2}(?:\.\d{1,2})?\s*)+)")
    dados = []
    for match in padrao.finditer(texto):
        disciplina = match.group("disciplina").strip()
        notas = match.group("notas").strip().split()
        dados.append({"Disciplina": disciplina, **{f"Nota {i+1}": nota for i, nota in enumerate(notas)}})
    return pd.DataFrame(dados)

st.set_page_config(page_title="Gerador de Histórico Escolar", layout="wide")
st.title("📄 Gerador de Histórico Escolar")

st.sidebar.header("🔧 Cadastro prévio")
disciplinas_padrao = st.sidebar.multiselect("Disciplinas padrão", [
    "Português", "Matemática", "História", "Geografia", "Ciências", "Educação Física",
    "Arte", "Filosofia", "Sociologia", "Física", "Química", "Biologia", "Redação",
    "Língua Inglesa", "Língua Espanhola", "Literatura", "Cooperativismo"
], default=["Português", "Matemática", "História"])

escolas = st.sidebar.text_area("Escolas cadastradas (uma por linha)",
    "COOPEB - Barreiras/BA\nEscola de Aplicação César Macedo - Barreiras/MG")
escolas_lista = escolas.strip().splitlines()

guia = st.expander("📎 Instruções")
guia.markdown("""
1. Faça upload do histórico em PDF;
2. O app vai extrair as disciplinas e notas;
3. Você pode editar as informações e selecionar a escola referente;
4. Ao final, exporte para Excel.
""")

arquivo_pdf = st.file_uploader("📤 Envie um histórico em PDF", type="pdf")

if arquivo_pdf:
    texto_extraido = extrair_texto_pdf(arquivo_pdf)
    df_notas = extrair_disciplinas_e_notas(texto_extraido)

    st.success("Texto extraído com sucesso!")
    st.subheader("🧾 Notas encontradas:")
    st.dataframe(df_notas, use_container_width=True)

    st.subheader("🏫 Selecione a escola referente:")
    escola_escolhida = st.selectbox("Escola:", escolas_lista)

    st.subheader("📝 Observações finais:")
    obs = st.text_area("Campo de observação:", "Código de segurança: _____\nMédia mínima: 7,0\nData de nascimento: ___/___/____")

    if st.button("⬇️ Exportar para Excel"):
        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_notas.to_excel(writer, sheet_name="Notas", index=False)
                obs_df = pd.DataFrame({"Observações": [obs]})
                obs_df.to_excel(writer, sheet_name="Observações", index=False)
                writer.save()
            st.download_button(
                label="📥 Baixar planilha Excel",
                data=buffer.getvalue(),
                file_name="historico_extraido.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Por favor, envie um arquivo PDF para continuar.")
