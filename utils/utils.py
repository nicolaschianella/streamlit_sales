###############################################################################
#
# File:      utils.py
# Author(s): Nico
# Scope:     Utils functions to use within the project
#
# Created:   29 January 2024
#
###############################################################################
import streamlit as st
import logging
import requests
import json

from utils.defines import API_HOST, GET_REQUESTS_ROUTE

def get_requests(port: int) -> None:
    """
    Acquires available clothes requests using our API and put them in st.session_state.
    :param port: int, API port to use
    :return: None
    """
    logging.info("Getting requests")

    try:
        available_requests = requests.get(f"{API_HOST}:{port}/{GET_REQUESTS_ROUTE}")

        # Case error
        if available_requests.status_code != 200:
            logging.error(f"There was an issue while acquiring requests: {available_requests.json()['message']}")
            st.write(f"Oops ! Il y a eu un souci avec l'acquisition des recherches : {available_requests.json()['message']}")

        # Case all good
        else:
            logging.info(f"Successfully retrieved requests: {available_requests.json()['data']['requests']}")
            st.session_state.requests = json.loads(available_requests.json()["data"]["requests"])

    except requests.exceptions.ConnectionError:
        logging.error("API is down! Cannot proceed further")
        st.write(f"Oops ! L'API semble down.")
