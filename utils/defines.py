###############################################################################
#
# File:      defines.py
# Author(s): Nico
# Scope:     Global variables to use within the project
#
# Created:   24 January 2024
#
###############################################################################
# API Host (port handled in entry point parameters)
API_HOST = "http://127.0.0.1"
# Route to get_clothes
GET_CLOTHES_ROUTE = "api/operations/get_clothes"
# Route to get_requests
GET_REQUESTS_ROUTE = "api/operations/get_requests"
# Mapper {fields_to_be_displayed: displayed_value} for requests edition
# These will also be the available fields to fill in to create a new request
MAPPER_REQUESTS = {
    "name": "Nom de la recherche",
    "creation_date": "Date de création",
    "per_page": "Nb d'articles à chercher",
    "search_text": "Mots clés",
    "brand_ids": "Marque",
    "price_from": "Prix minimum",
    "price_to": "Prix maximum",
    "status_ids": "Etat de l'article"
}
