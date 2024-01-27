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
from pytz import timezone
from typing import Union
from datetime import datetime
from operator import itemgetter

from config.defines import API_HOST, GET_CLOTHES_ROUTE, GET_REQUESTS_ROUTE

def run() -> None:
    """
    This function sets session_state.run to True, to disable the usage of the button "Chercher vêtements"
    while the API is requested.
    :return: None
    """
    logging.info("Acquiring clothes")
    st.session_state.run = True

def get_clothes(port: int,
                selected_requests: list) -> Union[str, requests.models.Response]:
    """Main function called when we click on the "Chercher vêtements" button.
    Acquires Vinted clothes using our API.
    :param port: int, API port to use
    :param selected_requests: list of str, list of requests names to apply
    :return: clothes, str (in case of error) or requests.models.Response (if the call was successful)"""
    corresponding_requests = []
    try:
        clothes = []

        # Case no selected request
        if not selected_requests:
            logging.warning("No selected clothes requests")
            # State is not run anymore
            st.session_state.run = False
            return "Aucune recherche sélectionnée !", corresponding_requests

        for request_name in selected_requests:
            # Find the whole request
            found_request = {}
            for request in st.session_state.requests:
                if request_name == request["name"]:
                    found_request = request
                    break
            request_clothes = requests.get(f"{API_HOST}:{port}/{GET_CLOTHES_ROUTE}", data=json.dumps(found_request))
            clothes = format_clothes(clothes, request_clothes)
            corresponding_requests.extend([found_request["name"]] * (len(clothes) - len(corresponding_requests)))

        # Keep copy of the original order
        clothes_orig = clothes.copy()
        # Sort clothes by datetime
        clothes = sorted(clothes, key=itemgetter('created_at_datetime'), reverse=True)
        # Get the indices of the sorted order from the clothes_orig list
        indices = [clothes_orig.index(item) for item in clothes]
        # Finally sort requests the same way
        corresponding_requests = [corresponding_requests[i] for i in indices]

    except requests.exceptions.ConnectionError:
        logging.error("API is down! Cannot proceed further")
        clothes = "Oops ! L'API semble down."

    # State is not run anymore
    st.session_state.run = False

    logging.info(f"Successfully retrieved {len(clothes)} clothes")

    return clothes, corresponding_requests

def format_clothes(clothes: list,
                   request_clothes: requests.models.Response) -> list:
    """
    Formats clothes from the API response
    :param clothes: list, all the current clothes
    :param request_clothes: requests.models.Response, API response for the given request
    :return: list, formatted clothes with unique values
    """
    request_clothes = json.loads(request_clothes.json()["data"])
    for item in request_clothes:
        # Means there is no associated picture -> we don't consider these
        if item["created_at_ts"] == "NA":
            logging.warning(f"Encountered item with no picture, skipping: {item}")
            continue
        # Format str to datetime and apply local time
        item["created_at_datetime"] = (datetime.strptime(item["created_at_ts"], f"%Y-%m-%dT%H:%M:%S%z")
                                       .astimezone(timezone("Europe/Brussels")))
        if item not in clothes:
            clothes.append(item)
        else:
            logging.warning(f"Item encountered more than once, skipping: {item}")

    return clothes

def display_clothe(clothe: dict,
                   request_name: str) -> None:
    """
    Given a dict (clothe), displays it on a container
    :param clothe: dict, formatted clothe
    :param request_name, str, the corresponding request name
    :return: None
    """
    logging.info(f"Displaying clothe: {clothe}")

    with st.container(border=True):
        # Generate grid
        tiles = []
        row1 = st.columns(1) # For title
        row2 = st.columns(2) # (Date, Brand, Size, Status, Price, Favourites, Views) + image
        row3 = st.columns(2) # Button to visit link, AutoBuy
        row4 = st.columns(1) # Corresponding request_name

        for col in row1 + row2 + row3 + row4:
            tiles.append(col.container())
        # Display elements
        # Title - add suspicious photo in case
        if not clothe["is_photo_suspicious"]:
            tiles[0].subheader(clothe["title"])
        else:
            tiles[0].subheader(clothe["title"] + " - PHOTO SUSPICIEUSE")
        # Date, Brand, Size, Status, Price, Favourites, Views
        tiles[1].markdown(f"**Date:** {clothe['created_at_datetime']}")
        tiles[1].markdown(f"**Marque:** {clothe['brand_title']}")
        tiles[1].markdown(f"**Taille:** {clothe['size_title']}")
        tiles[1].markdown(f"**Etat:** {clothe['status']}")
        tiles[1].markdown(f"**Prix:** {clothe['total_item_price']} {clothe['currency']}  "
                          f"({clothe['price_no_fee']} + {clothe['service_fee']} fee)")
        tiles[1].markdown(f"**Nombre de vues:** {clothe['view_count']}")
        tiles[1].markdown(f"**Nombre de favoris:** {clothe['favourite_count']}")
        # Image
        tiles[2].image(clothe["photo_url"], width=300)
        # Buttons
        tiles[3].link_button('Voir sur Vinted', clothe["url"])
        tiles[4].button('AutoBuy', type="primary", key=str(clothe["id"]))
        # Corresponding request name
        tiles[5].markdown(f"**Via recherche:** {request_name}")

    return

def get_requests(port: int) -> list:
    """
    Function called to fill the "Recherches à appliquer" multiselect.
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
            logging.info(f"Successfully retrived requests: {available_requests.json()['data']['requests']}")
            st.session_state.requests = json.loads(available_requests.json()["data"]["requests"])

        return

    except requests.exceptions.ConnectionError:
        logging.error("API is down! Cannot proceed further")
        st.write(f"Oops ! L'API semble down.")

        return

def main(port: int) -> None:
    """Main function running this page.
    :param port: int, API port to use
    :return: None
    """
    # Deactivate button and requests selection when running get_clothes
    if 'run' not in st.session_state:
        # API is loading clothes
        st.session_state.run = False
        # Found clothes
        st.session_state.result = None
        # Corresponding clothes requests for each clothe
        st.session_state.corresponding_requests = None
        # All the requests found in MongoDB
        st.session_state.requests = None
        # Current selected requests in the selector
        st.session_state.selected_requests = None

    # get all the available requests
    get_requests(port)

    if st.session_state.requests:
        # Requests selector
        selected_requests = st.multiselect("Recherches à appliquer",
                                           help="Seuls les noms sont affichés. L'ensemble des requêtes se trouve dans la "
                                                "page 'Edition requêtes'",
                                           options=[request["name"] for request in st.session_state.requests],
                                           default=st.session_state.selected_requests \
                                               if st.session_state.selected_requests \
                                               else [request["name"] for request in st.session_state.requests],
                                           disabled=st.session_state.run)

        st.button('Chercher vêtements', on_click=run, disabled=st.session_state.run, type="primary")

        # Put clothes in session_state and rerun the app to make the button clickable again
        # Also keep track of selected requests
        if st.session_state.run:
            st.session_state.selected_requests = selected_requests
            st.session_state.result, st.session_state.corresponding_requests = get_clothes(port, selected_requests)
            st.rerun()

        # Once we finish getting clothes (successful or not), we need to rewrite them since we rerun the app
        if st.session_state.result is not None:
            if type(st.session_state.result) is str:
                # Case call not successful -> print error message for the user
                st.write(st.session_state.result)

            else:
                # Case call successful
                for clothe, request_name in zip(st.session_state.result, st.session_state.corresponding_requests):
                    display_clothe(clothe, request_name)


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
        level=logging.INFO,
        format="%(asctime)s -- %(funcName)s -- %(levelname)s -- %(message)s"
    )

    main(args.port)
