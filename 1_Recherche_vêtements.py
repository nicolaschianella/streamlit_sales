import streamlit as st
import requests
import json

def run():
    st.session_state.run = True

def expensive_process():
    with st.spinner('Acquisition des vêtements...'):
        data = requests.get("http://127.0.0.1:8000/api/operations/get_clothes", data=json.dumps({}))
    st.session_state.run = False
    return data

def main():
    if 'run' not in st.session_state:
        st.session_state.run = False

    st.button('Chercher vêtements', on_click=run, disabled=st.session_state.run)

    if st.session_state.run:
        data = expensive_process()
        # With expensive_process we have to put variables into st.session_state not to delete them
        # See: https://discuss.streamlit.io/t/hide-button-during-inference-time/43826/4
        st.write(data.json())
        st.rerun()


if __name__ == '__main__':
    st.set_page_config(
        page_title="Recherche vêtements",
    )

    main()
