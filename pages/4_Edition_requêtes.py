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
import requests

from utils.utils import set_basic_config, get_requests
from utils.defines import (MAPPER_REQUESTS, MAPPER_STATUS_IDS, STATUS_IDS_KEY, BRAND_IDS_KEY, CONFIG, BRANDS,
                           API_HOST, UPDATE_REQUESTS_ROUTE)


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

def concat_clothe_states(row):
    """
    Small function to format back clothe states to its original format
    :param row: DataFrame row to be reformatted
    :return: new reformatted column value
    """
    final_value = ""

    for key, value in MAPPER_STATUS_IDS.items():
        if row[key]:
            final_value += value
            final_value += ","

    final_value = final_value[:-1]

    return final_value

def format_requests_back() -> None:
    """
    Formats the DataFrame back to its original format to be sent to the API
    :return: None
    """
    logging.info("Starting formatting requests")

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

    # If everything is good, proceed with reformatting
    # 1. Concatenate all clothes status into one column
    displayed_edited[STATUS_IDS_KEY] = displayed_edited.apply(lambda row: concat_clothe_states(row), axis=1)
    displayed_edited.drop(MAPPER_STATUS_IDS.keys(), axis=1, inplace=True)
    logging.info("Successfully formatted clothe states")
    # 2. Change brands to corresponding id
    displayed_edited[BRAND_IDS_KEY] = displayed_edited[MAPPER_REQUESTS[BRAND_IDS_KEY]].map(BRANDS)
    displayed_edited.drop(MAPPER_REQUESTS[BRAND_IDS_KEY], axis=1, inplace=True)
    logging.info("Successfully formatted brands names")
    # 3. Change remaining column names
    displayed_edited.rename(columns={v: k for k, v in MAPPER_REQUESTS.items()}, inplace=True)
    st.session_state.requests_to_be_saved = displayed_edited.fillna("").to_json(orient="records")

    logging.info(f"Requests successfully formatted: {st.session_state.requests_to_be_saved}")

def save_requests(port) -> None:
    """
    Performs the saving of requests in DB after formatting them
    :param port: int, API port to use
    :return: None
    """
    try:
        # Format requests
        format_requests_back()

        # Call the API
        r = requests.post(f"{API_HOST}:{port}/{UPDATE_REQUESTS_ROUTE}", data=st.session_state.requests_to_be_saved)

        if r.status_code == 200:
            logging.info("Requests updated successfully, reloading page")
            # Reload page
            streamlit_js_eval(js_expressions="parent.window.location.reload()")

        else:
            # Error message
            st.write("Il y a eu un souci avec la mise à jour des requêtes. Merci de contacter les administrateurs.")

    except Exception as e:
        logging.error(f"An error occurred while saving requests: {e}")


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
        # Final requests to be sent to the API
        st.session_state.requests_to_be_saved = None

    # Display only if everything is OK or if we have no requests in DB
    if st.session_state.displayed is None and get_requests(port):
        display_requests()

    if st.session_state.displayed is not None:

        # Display DataFrame
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
            save_requests(port)


if __name__ == '__main__':
    api_port, _ = set_basic_config("Edition requêtes")
    main(api_port)
