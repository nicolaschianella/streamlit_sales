###############################################################################
#
# File:      rsync_dev.sh
# Author(s): Nico
# Scope:     Send the project in the dev folder
#
# Created:   22 January 2024
#
###############################################################################

branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$branch" =~ (dev)$ ]]; then
    rsync -e "ssh" --exclude=".idea/" --exclude='.git/' --exclude="__pycache__/" \
    --exclude="/venv" --exclude="*.csv" --exclude="*.log" --exclude=".gitignore" \
    -rav . guys@guysmachine:/home/guys/streamlit_sales/streamlit_sales_dev
else
    echo "Branch is not dev. Skipping rsync command."
fi
