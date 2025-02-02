import streamlit as st
import ollama
from time import sleep

st.set_page_config(
    page_title="Model management",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.subheader("⚙️ Gerenciamento de Modelos", divider="red", anchor=False)

    st.subheader("Download Models", anchor=False)
    model_name = st.text_input(
        "Entre com o nome do modelo que deseja baixar:", placeholder="mistral"
    )
    if st.button(f"📥 :green[**Baixar**] :red[{model_name}]"):
        if model_name:
            try:
                ollama.pull(model_name)
                st.success(f"Downloaded model: {model_name}", icon="🎉")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Ocorreu um erro ao baixar modelo: {
                    model_name}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Por favor entre com o nome do modelo.", icon="⚠️")

    st.divider()

    st.subheader("Criar modelo", anchor=False)
    modelfile = st.text_area(
        "Entre com arquivo de modelo",
        height=100,
        placeholder="""FROM mistral
SYSTEM Você é Cebolinha dos quadrinhos da Turma da Mônica.""",
    )
    model_name = st.text_input(
        "Entre com o nome do modelo que deseja criar", placeholder="mario"
    )
    if st.button(f"🆕 Criar Modelo {model_name}"):
        if model_name and modelfile:
            try:
                ollama.create(model=model_name, modelfile=modelfile)
                st.success(f"Modelo criado: {model_name}", icon="✅")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Falaha ao criar modelo: {
                         model_name}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Entre o **model name** and **modelfile**", icon="⚠️")

    st.divider()

    st.subheader("Deletar Modelos", anchor=False)
    models_info = ollama.list()
    available_models = [m["name"] for m in models_info["models"]]

    if available_models:
        selected_models = st.multiselect("Escolha os modelos que deseja apagar:", available_models)
        if st.button("🗑️ :red[**Apagar Modelo(s)**]"):
            for model in selected_models:
                try:
                    ollama.delete(model)
                    st.success(f"Modelo apagado: {model}", icon="🎉")
                    st.balloons()
                    sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(
                        f"""Falha ao apagar modelo: {
                        model}. Erro: {str(e)}""",
                        icon="😳",
                    )
    else:
        st.info("Sem modelos disponíveis para apagar.", icon="🦗")


if __name__ == "__main__":
    main()
