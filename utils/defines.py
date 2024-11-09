###############################################################################
#
# File:      defines.py
# Author(s): Nico
# Scope:     Global variables to use within the project
#
# Created:   24 January 2024
#
###############################################################################
import streamlit as st
from datetime import datetime


# API Host (port handled in entry point parameters)
API_HOST = "http://127.0.0.1"
# Route to get_clothes
GET_CLOTHES_ROUTE = "api/operations/get_clothes"
# Route to get_requests
GET_REQUESTS_ROUTE = "api/operations/get_requests"
# Route to update_requests
UPDATE_REQUESTS_ROUTE = "api/operations/update_requests"
# Mapper {fields_to_be_displayed: displayed_value} for requests edition
# These will also be the available fields to fill in to create a new request
MAPPER_REQUESTS = {
    # _id is the only exception and will not be displayed
    "_id": "_id",
    "name": "Nom",
    "creation_date": "Date de création",
    "per_page": "Nb articles",
    "search_text": "Mots clés",
    "brand_ids": "Marque",
    "price_from": "Prix minimum",
    "price_to": "Prix maximum",
    "state": "Etat recherche"
}
# status_ids is an exception since we want multiple checkbox columns, one for each clothe state
STATUS_IDS_KEY = "status_ids"
# brand_ids as well because we need to map id -> brand name
BRAND_IDS_KEY = "brand_ids"
# Define clothes states
MAPPER_STATUS_IDS = {
    "Neuf avec étiquette": "6",
    "Neuf sans étiquette": "1",
    "Très bon état": "2",
    "Bon état": "3"
}
# Define referenced brands
BRANDS = {
    "adidas": "14",
    "Arc'Teryx": "319730",
    "arte": "271932",
    "Burberry": "364",
    "Carhartt": "362",
    "C.P. Company": "73952",
    "Lacoste": "304",
    "Nike": "53",
    "Ralph Lauren": "88",
    "Stone Island": "73306",
    "Stüssy": "441",
    "The North Face": "2319",
}
# Define config to display requests in "Edition requêtes" - checkboxes automatically added for every key
# in MAPPER_STATUS_IDS
CONFIG = {
    "Nom": st.column_config.TextColumn("Nom",
                                       help="Nom de la recherche dans 'Recherche vêtements' (DEFAULT si vide)"),

    "Date de création": st.column_config.TextColumn("Date de création",
                                                    disabled=True,
                                                    help="Timezone UTC - màj auto",
                                                    default=""),

    "Nb articles": st.column_config.NumberColumn("Nb articles",
                                                 help="Nombre d'articles par recherche (max 96)",
                                                 min_value=1,
                                                 max_value=96,
                                                 default=10),

    "Mots clés": st.column_config.TextColumn("Mots clés",
                                             help="Recherche mots clés comme sur le site"),

    "Marque": st.column_config.SelectboxColumn("Marque",
                                               options=list(BRANDS.keys()),
                                               help="Limité à une seule marque"),

    "Prix minimum": st.column_config.NumberColumn("Prix minimum",
                                                  min_value=0,
                                                  help="Prix minimum à appliquer (hors fee)"),

    "Prix maximum": st.column_config.NumberColumn("Prix maximum",
                                                  min_value=0,
                                                  help="Prix maximum à appliquer (hors fee)"),

    "Etat recherche": st.column_config.SelectboxColumn("Etat recherche",
                                                       options=["active", 'inactive'],
                                                       help="Si la recherche doit apparaître dans la page "
                                                          "'Recherche vêtements'",
                                                       default="active",
                                                       required=True)
}
