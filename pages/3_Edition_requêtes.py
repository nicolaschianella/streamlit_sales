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
import pandas as pd

from utils.utils import set_basic_config, get_requests
from utils.defines import MAPPER_REQUESTS


def display_requests() -> None:
    """
    Display the available requests in a pandas DataFrame with a deletion option
    :return: None
    """
    # Format requests
    for_reqs = format_requests()
    # Build the corresponding DataFrame and display it
    df_req = pd.DataFrame(for_reqs)
    edited_df = st.data_editor(df_req, num_rows="dynamic")

def format_requests() -> list[dict]:
    """
    Format the st.session_state.requests using the MAPPER_REQUESTS dictionary
    :return: list[dict], list of formatted requests dictionary
    """
    requests = st.session_state.requests.copy()
    for_reqs = []

    # Use mapper to get proper displayed names
    for request in requests:
        for_reqs.append({MAPPER_REQUESTS[key]: request[key] for key in MAPPER_REQUESTS})

    return for_reqs

def main(port: int) -> None:
    """
    Main function running this page.
    :param port: int, API port to use
    :return: None
    """
    # Load requests if this is the first visited page
    if "requests" not in st.session_state:
        get_requests(port)

    display_requests()


if __name__ == '__main__':
    api_port, _ = set_basic_config("Edition requêtes")
    main(api_port)
