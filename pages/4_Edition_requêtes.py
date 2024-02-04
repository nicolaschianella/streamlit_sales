###############################################################################
#
# File:      3_Edition_requêtes.py
# Author(s): Nico
# Scope:     Page to edit clothes searches
#
# Created:   23 January 2024
#
###############################################################################
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import logging

from utils.utils import set_basic_config, get_requests
from utils.defines import MAPPER_REQUESTS, MAPPER_STATUS_IDS, STATUS_IDS_KEY, BRAND_IDS_KEY, CONFIG, BRANDS


def display_requests() -> None:
    """
    Put DataFrame to be displayed, config and columns in st.session_state
    :return: None
    """
    # Format requests
    for_reqs = format_requests()
    logging.info(f"Displaying requests: {for_reqs}")

    # Build the corresponding DataFrame and display it
    columns = [MAPPER_REQUESTS[key] for key in MAPPER_REQUESTS] + list(MAPPER_STATUS_IDS.keys())
    df_req = pd.DataFrame(for_reqs) if for_reqs else pd.DataFrame({},
                                                                  columns=columns)

    # Add values for clothes states
    config = CONFIG.copy()
    for key, value in MAPPER_STATUS_IDS.items():
        config[key] = st.column_config.CheckboxColumn(key,
                                                      help="Cocher pour appliquer dans la recherche",
                                                      default=True)

    # Put the final editable DataFrame, config and columns in st.session_state
    st.session_state.displayed = df_req
    st.session_state.config, st.session_state.columns = config, columns

def format_requests() -> list[dict]:
    """
    Format the st.session_state.requests using the MAPPER_REQUESTS dictionary
    :return: list[dict], list of formatted requests dictionary
    """
    try:
        requests = st.session_state.requests.copy()
        for_reqs = []

        logging.info(f"Formatting requests: {requests}")

        # Use mapper to get proper displayed names
        for request in requests:
            for_req = {}

            # Add regular columns
            for key in MAPPER_REQUESTS:
                # Case for brands - use mapper to display brand
                if key == BRAND_IDS_KEY:
                    inv_brands = {v: k for k, v in BRANDS.items()}
                    for_req[MAPPER_REQUESTS[key]] = inv_brands[request[key]] if request[key] != "" else ""
                    continue
                # Other cases
                for_req[MAPPER_REQUESTS[key]] = request[key]

            # Add clothes states keys
            clothes_states = request[STATUS_IDS_KEY].split(",")
            for key, value in MAPPER_STATUS_IDS.items():
                for_req[key] = value in clothes_states

            for_reqs.append(for_req)

        logging.info(f"Successfully formatted requests: {for_reqs}")

    except AttributeError:
        logging.warning("No requests found")
        for_reqs = None

    return for_reqs

def run_save() -> None:
    """
    Disables editing of the DataFrame and the corresponding save button
    :return: None
    """
    logging.info("Saving requests in Mongo")
    st.session_state.not_modified = True
    st.session_state.run_save = True

def modify_df() -> None:
    """
    Enables save button
    :return: None
    """
    st.session_state.not_modified = False

def format_requests_back() -> None:
    """
    Formats the DataFrame back to its original format to be sent to the API
    :return: None
    """
    # Get DataFrame and modified/added/deleted rows
    displayed, df = st.session_state.displayed, st.session_state.df

    # Build the edited DataFrame
    displayed_edited = displayed.copy()

    # First remove all the rows removed
    if df["deleted_rows"]:
        index = displayed_edited.iloc[df["deleted_rows"]].index
        displayed_edited.drop(index, inplace=True)

    # Now edit rows
    if df["edited_rows"]:
        # Locate changes for one row
        for key, value in df["edited_rows"].items():
            # Locate all columns changes and apply them
            for col, new_value in df["edited_rows"][key].items():
                displayed_edited.loc[key, col] = new_value

    # Finally add new rows
    if df["added_rows"]:
        for new_row in df["added_rows"]:
            displayed_edited.loc[len(displayed_edited)+1] = new_row
            displayed_edited.fillna("", inplace=True)

    # Check if "Name" row contains None: if yes, write error message and enable button/editing again
    if "" in list(displayed_edited["Nom"]):
        logging.warning("Names missing in DataFrame! Not performing save into Mongo")
        st.session_state.df_empty_name = True
        st.session_state.run_save = False
        st.session_state.not_modified = False
        st.rerun()

def save_requests() -> None:
    """
    Performs the saving of requests in DB after formatting them
    :return: None
    """
    format_requests_back()

    # Reload page
    streamlit_js_eval(js_expressions="parent.window.location.reload()")


def main(port: int) -> None:
    """
    Main function running this page.
    :param port: int, API port to use
    :return: None
    """
    if 'run_save' not in st.session_state:
        # Reset requests and reload them
        st.session_state.requests = None
        # Disable DataFrame editing
        st.session_state.run_save = False
        # Whether the DataFrame has been modified or not (enables save button)
        st.session_state.not_modified = True
        # Edited DataFrame to be saved
        st.session_state.displayed = None
        # Whether new added rows have empty names
        st.session_state.df_empty_name = False

    # Display only if everything is OK or if we have no requests in DB
    if st.session_state.displayed is None and get_requests(port):
        display_requests()

    if st.session_state.displayed is not None:

        # Hide DataFrame when saving
        if not st.session_state.run_save:
            st.data_editor(st.session_state.displayed,
                           column_config=st.session_state.config,
                           on_change=modify_df,
                           # Hide _id column, but we need the info to update our DB
                           column_order=[col for col in st.session_state.columns if col != "_id"],
                           num_rows="dynamic",
                           hide_index=True,
                           key="df")

        # Add button to save changes
        st.button("Sauver les recherches",
                  on_click=run_save,
                  type="primary",
                  disabled=st.session_state.not_modified)

        if st.session_state.df_empty_name:
            st.write('Certains noms sont manquants !')

        if st.session_state.run_save:
            save_requests()


if __name__ == '__main__':
    api_port, _ = set_basic_config("Edition requêtes")
    main(api_port)
