###############################################################################
#
# File:      rsync_prod.sh
# Author(s): Nico
# Scope:     Send the project in the prod folder
#
# Created:   22 January 2024
#
###############################################################################

branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$branch" =~ (main)$ ]]; then
    rsync -e "ssh" --exclude=".idea/" --exclude='.git/' --exclude="__pycache__/" \
    --exclude="/venv" --exclude="*.csv" --exclude="*.log" --exclude=".gitignore"\
    -rav . guys@guysmachine:/home/guys/streamlit_sales/streamlit_sales_prod
else
    echo "Branch is not main. Skipping rsync command."
fi
