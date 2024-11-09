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
import argparse
import os
import time

from utils.defines import API_HOST, GET_REQUESTS_ROUTE

def set_basic_config(page_name: str) -> tuple[int, str]:
    """
    Sets basic config such as page name, logs, etc

    Args:
        page_name (str): name of page to be displayed

    Returns:
        tuple, (int, str), (API port used, logs filename)
    """
    # Page name
    st.set_page_config(
        page_title=page_name,
        layout="wide"
    )

    # Get arguments
    parser = argparse.ArgumentParser(description="StreamlitSales")
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        default=8000,
        help="Specify API port",
        required=False
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store",
        default="streamlit_sales.log",
        help="Specify output log file",
        required=False
    )

    args = parser.parse_args()

    # Set timezone to UTC
    os.environ["TZ"] = "UTC"
    time.tzset()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s -- %(filename)s -- %(funcName)s -- %(levelname)s -- %(message)s"
    )

    logging.info(f"Changed to page {page_name}")

    return args.port, args.log

def get_requests(port: int,
                 filter_on_active: bool = True) -> bool:
    """
    Acquires available clothes requests using our API and put them in st.session_state.

    Args:
        port (int): API port in use
        filter_on_active (bool): whether to only filter on active requests (page "Recherche vêtements")

    Returns:
        bool, whether we display requests data_editor or not (page "Edition requêtes")
    """
    logging.info("Getting requests")

    try:
        available_requests = requests.get(f"{API_HOST}:{port}/{GET_REQUESTS_ROUTE}")

        # Case error
        if available_requests.status_code != 200:
            logging.error(f"There was an issue while acquiring requests: {available_requests.json()['message']}")
            st.write(f"Oops ! Il y a eu un souci avec l'acquisition des recherches : {available_requests.json()['message']}")
            return True if available_requests.status_code == 404 else False

        # Case all good
        else:
            logging.info(f"Successfully retrieved requests: {available_requests.json()['data']['requests']}")

            if filter_on_active:
                filtered_on_active = []

                for request in json.loads(available_requests.json()['data']['requests']):
                    if request["state"] == "active":
                        filtered_on_active.append(request)

                if not filtered_on_active:
                    st.write("Aucune recherche active !")

                st.session_state.requests = filtered_on_active

            else:
                st.session_state.requests = json.loads(available_requests.json()["data"]["requests"])

            return True

    except requests.exceptions.ConnectionError:
        logging.error("API is down! Cannot proceed further")
        st.write(f"Oops ! L'API semble down.")
        return False

def clear_session_state() -> None:
    """
    Clears all session state variables

    Returns:
        None
    """
    for key in st.session_state:
        del st.session_state[key]

    logging.info("Successfully cleared session state")
