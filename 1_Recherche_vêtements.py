###############################################################################
#
# File:      1_Recherche_vêtements.py
# Author(s): Nico
# Scope:     Entry point - page to look for clothes
#
# Created:   23 January 2024
#
###############################################################################
import streamlit as st
import requests
import json
import logging
import argparse
import os
import time
from typing import Union
from datetime import datetime
from operator import itemgetter

from config.defines import API_HOST, GET_CLOTHES_ROUTE

def run() -> None:
    """
    This function sets session_state.run to True, to disable the usage of the button "Chercher vêtements"
    while the API is requested.
    :return: None
    """
    st.session_state.run = True

def get_clothes(port: int) -> Union[str, requests.models.Response]:
    """Main function called when we click on the "Chercher vêtements" button.
    Acquires Vinted clothes using our API.
    :param port: int, API port to use
    :return: clothes, str (in case of error) or requests.models.Response (if the call was successful)"""
    # Loading spinner
    with st.spinner('Acquisition des vêtements...'):
        try:
            # TODO: load selected requests and loop over them instead
            clothes = []
            for _ in range(2):
                request_clothes = requests.get(f"{API_HOST}:{port}/{GET_CLOTHES_ROUTE}", data=json.dumps({}))
                clothes = format_clothes(clothes, request_clothes)

            # Finally sort by datetime
            clothes = sorted(clothes, key=itemgetter('created_at_datetime'), reverse=True)

        except requests.exceptions.ConnectionError:
            clothes = "Oops! L'API semble down."
    # State is not run anymore
    st.session_state.run = False
    return clothes

def format_clothes(clothes: list, request_clothes: requests.models.Response) -> list:
    """
    Formats clothes from the API response
    :param clothes: list, all the current clothes
    :param request_clothes: requests.models.Response, API response for the given request
    :return: list, formatted clothes with unique values
    """
    request_clothes = json.loads(request_clothes.json()["data"])
    for  item in request_clothes:
        # Format str to datetime
        # TODO: change timezoneo Europe/Brussels and handle case where we have "NA" in item["created_at_ts"] (interpolation)
        item["created_at_datetime"] = datetime.strptime(item["created_at_ts"], f"%Y-%m-%dT%H:%M:%S%z")
        if item not in clothes:
            clothes.append(item)

    return clothes

def main(port: int) -> None:
    """Main function running this page.
    :param port: int, API port to use
    :return: None
    """
    # Deactivate button when running get_clothes
    if 'run' not in st.session_state:
        st.session_state.run = False
        st.session_state.result = None

    st.button('Chercher vêtements', on_click=run, disabled=st.session_state.run, type="primary")

    # Put clothes in session_state and rerun the app to make the button clickable again
    if st.session_state.run:
        st.session_state.result = get_clothes(port)
        st.rerun()

    # Once we finish getting clothes (successful or not), we need to rewrite them since we rerun the app
    if st.session_state.result is not None:
        if type(st.session_state.result) is str:
            # Case call not successful -> print error message for the user
            st.write(st.session_state.result)

        else:
            # Case call successful -> TODO: format data and display
            st.write(st.session_state.result)



if __name__ == '__main__':
    # Page name
    st.set_page_config(
        page_title="Recherche vêtements",
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
        level=logging.INFO, # TODO: INFO or DEBUG? DEBUG -> log file very large
        format="%(asctime)s -- %(funcName)s -- %(levelname)s -- %(message)s"
    )

    main(args.port)
