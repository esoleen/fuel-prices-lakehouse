import urllib
import shutil
import gzip 
import os
import urllib.request


# download file from URL:https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/csv?use_labels=true
def download_csv_file(url, path):
    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/prix-des-carburants-en-france-flux-instantane-v2.csv"
    req = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    response = urllib.request.urlopen(req)
    with gzip.GzipFile(fileobj=response) as gz_in, open(file_path, "wb") as f_out:
        shutil.copyfileobj(response, f_out)
    return file_path

def read_csv_file(file, spark):
    return spark\
    .read\
    .option("header", "true")\
    .option("inferSchema","true")\
    .option("delimiter", ";")\
    .option("mode", "PERMISSIVE")\
    .option("escape", '"')\
    .option("quote", '"')\
    .option("columnNameOfCorruptRecord", "_corrupt_record")\
    .csv(file)


def download_json_file():
    pass