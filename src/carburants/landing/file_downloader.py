import urllib
import shutil
import gzip 
import os
import urllib.request


# download file from URL:https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree
def download_csv_file(url, path):
    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/prix-des-carburants-en-france-flux-instantane-v2.csv"
    req = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    response = urllib.request.urlopen(req)
    with gzip.GzipFile(fileobj=response) as gz_in, open(file_path, "wb") as f_out:
        shutil.copyfileobj(gz_in, f_out)
    return file_path

def read_csv_file(file, df_schema, delimiter = ";"):
    return spark.read.csv(file,schema = df_schema,header = True)

def download_json_file():
    pass