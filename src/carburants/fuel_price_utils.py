import urllib
import gzip
import os
import urllib.request


# download file from URL:https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/csv?use_labels=true
def download_csv_file(url, path):
    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/prix-des-carburants-en-france-flux-instantane-v2.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    req = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    response = urllib.request.urlopen(req)
    raw = response.read()
    with open(file_path, "wb") as f_out:
        if raw[:2] == b"\x1f\x8b":
            f_out.write(gzip.decompress(raw))
        else:
            f_out.write(raw)
    return file_path

def read_csv_file(file, spark, schema):
    return spark\
    .read\
    .option("header", "true")\
    .schema(schema)\
    .option("inferSchema","true")\
    .option("delimiter", ";")\
    .option("mode", "PERMISSIVE")\
    .option("escape", '"')\
    .option("quote", '"')\
    .option("columnNameOfCorruptRecord", "_corrupt_record")\
    .csv(file)


def download_json_file():
    pass


def get_watermark(spark, control_table, source_table):
    if not spark.catalog.tableExists(control_table):
        return None
    row = (
        spark.read.table(control_table)
        .where(f"table_name = '{source_table}'")
        .select("date_maj")
        .collect()
    )
    return row[0]["date_maj"] if row else None


def update_watermark(spark, control_table, source_table, new_watermark):
    if new_watermark is None:
        return
    new_row = spark.createDataFrame(
        [(source_table, new_watermark)], schema=["table_name", "date_maj"]
    )
    if spark.catalog.tableExists(control_table):
        from delta.tables import DeltaTable
        DeltaTable.forName(spark, control_table).alias("t").merge(
            new_row.alias("s"), "t.table_name = s.table_name"
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    else:
        new_row.write.format("delta").saveAsTable(control_table)


def full_keys(spark, table_name, delta_df, key_cols):
    delta_keys = delta_df.select(*key_cols).distinct()
    if spark.catalog.tableExists(table_name):
        return spark.read.table(table_name).select(*key_cols).distinct().unionByName(delta_keys).distinct()
    return delta_keys


def merge_dimension(spark, df, target_table, key_cols):
    from delta.tables import DeltaTable
    if not spark.catalog.tableExists(target_table):
        df.write.format("delta").saveAsTable(target_table)
        return
    condition = " AND ".join([f"t.{k} = s.{k}" for k in key_cols])
    DeltaTable.forName(spark, target_table).alias("t").merge(
        df.alias("s"), condition
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()