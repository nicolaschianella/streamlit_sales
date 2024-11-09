###############################################################################
#
# File:      run_dev.sh
# Author(s): Nico
# Scope:     Run project in dev mode
#
# Created:   25 January 2024
#
###############################################################################
export PYTHONPATH="$PWD"

if [ ! -d "venv" ]; then
  echo "Virtualenv (venv) not found in ${DIR}"
  echo "Installing virtualenv in ${DIR}/venv ..."
  python3.11 -m venv venv
fi
source venv/bin/activate
echo "Checking venv..."
pip install -U pip
pip install -r requirements.txt
echo "DONE!"
echo "Running main.py script - dev mode (API port 5000)"
nohup streamlit run 1_Recherche_vêtements.py -- -p 5000 -l streamlit_sales_dev.log &
