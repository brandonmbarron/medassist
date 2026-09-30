"""Week 1, Block 4: PySpark ETL pipeline.

Goal: read raw CSVs, clean them, join claims to members, and write
partitioned Parquet to data/curated/.

Run:
    python -m src.etl.pipeline

Learn first (Week 1, Block 3):
    - SparkSession, DataFrame, lazy evaluation
    - transformations (select, filter, withColumn, join) vs actions (count, show, write)
    - partitionBy when writing Parquet
"""

from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F  # noqa: F401  (you will use F in the TODOs)

RAW = Path("data/raw")
CURATED = Path("data/curated")


def get_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("medassist-etl")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")  # small data, fewer partitions
        .getOrCreate()
    )


def read_raw(spark: SparkSession) -> tuple[DataFrame, DataFrame]:
    members = spark.read.csv(str(RAW / "members.csv"), header=True, inferSchema=True)
    claims = spark.read.csv(str(RAW / "claims.csv"), header=True, inferSchema=True)
    return members, claims


def clean_claims(claims: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Split claims into (good_rows, rejected_rows).

    TODO (you):
      1. Reject rows where member_id is null or empty.
      2. Reject rows where billed_amount < 0.
      3. Cast service_date and received_date to DateType with F.to_date.
      4. Add a column `service_month` = first day of the service_date month
         (hint: F.trunc).
      5. Return both DataFrames so you can report how many were rejected.
    """
    raise NotImplementedError("Week 1, Block 4: implement clean_claims")


def enrich(claims: DataFrame, members: DataFrame) -> DataFrame:
    """Join claims to members to add plan_id and state.

    TODO (you):
      - Inner join on member_id.
      - Keep only the columns the agent needs later.
      - Bonus: use F.broadcast(members) and explain in your learning log
        why broadcasting the smaller table avoids a shuffle.
    """
    raise NotImplementedError("Week 1, Block 4: implement enrich")


def quality_report(good: DataFrame, rejected: DataFrame) -> dict:
    """Return simple data quality numbers. Print them and save to docs later."""
    total = good.count() + rejected.count()
    return {
        "total_rows": total,
        "rejected_rows": rejected.count(),
        "reject_rate": round(rejected.count() / total, 4) if total else 0.0,
    }


def run() -> None:
    spark = get_spark()
    members, claims = read_raw(spark)
    good, rejected = clean_claims(claims)
    curated = enrich(good, members)  # noqa: F841  (write this in the TODO below)

    # TODO (you): write `curated` to CURATED / "claims" as Parquet,
    # partitioned by plan_id, mode="overwrite".

    print(quality_report(good, rejected))
    spark.stop()


if __name__ == "__main__":
    run()
