# Marginfi Exporter
A Prometheus Exporter for marginfi.com

Exports acccount information for marginfi, run with 
```
# activate virtual enviroment and install packages
python3 -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt

# run 
python main.py

# view metrics 
curl localhost:9000/metrics
```
