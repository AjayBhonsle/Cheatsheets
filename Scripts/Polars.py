import polars as pl
import polars.selectors as cs

# ==============================================================================
# 0. SETUP COMPLETE UNIFIED MOCK DATASETS
# ==============================================================================
print("==============================================================================")
print("0. SETUP MOCK DATA FOR ALL PIPELINE STEPS")
print("==============================================================================")

raw_data = {
    "id": [1, 2, 3, 4],
    "name": ["alpha", "beta", "gamma", "delta"],
    "salary": [5000, 11000, 9500, None],
    "dept": ["IT", "HR", "IT", "HR"],
    "timestamp_str": ["2026-01-15", "2026-02-20", "2026-03-05", "2026-04-12"],
    "items_list": [["apple", "banana"], ["orange"], ["grape", "mango"], []],
    "num_col1": [10, 20, 30, 40]
}

raw_data_2 = {"emp_id": [3, 4, 5], "manager": ["Alice", "Bob", "Charlie"]}
raw_data_cat = {"id": [5, 6], "name": ["epsilon", "zeta"], "salary": [8000, 12000], "dept": ["FI", "IT"]}
raw_pivot = {"id": [1, 1, 2, 2], "metric": ["A", "B", "A", "B"], "value": [10, 20, 30, 40]}
raw_json = {"id": [1, 2], "json_str": ['{"age":25,"city":"NY"}', '{"age":30,"city":"SF"}']}

raw_advanced = {
    "emp_id": [1, 2, 2, 3, 4, 5],
    "version": [1, 1, 2, 1, 1, 1],
    "skills": ["SQL,Python", "Java", "Python,Spark,AWS", "SQL", None, "Docker,K8s"],
    "salary": [5000, 6000, 7500, 10000, 4000, 12000],
    "dept": ["IT", "HR", "HR", "IT", "Sales", "IT"],
    "entry_date": ["2026-01-01", "2026-01-15", "2026-02-01", "2026-02-15", "2026-03-01", "2026-03-15"]
}

raw_dates = {"start_date": ["2026-01-01", "2026-01-15", "2026-05-01"], "end_date": ["2026-01-10", "2026-02-20", "2026-05-01"]}
raw_skewed = {"id": [1, 2, 3, 4, 5, 6], "key": ["A", "B", "A", "A", "B", "C"], "val_x": [100, 200, 150, 110, 220, 300]}
raw_lookup = {"key": ["A", "B"], "val_y": [10, 20]}
raw_transactions = {
    "user_id": [101, 101, 101, 102, 102],
    "tx_time": ["2026-05-20 10:00:00", "2026-05-20 10:02:00", "2026-05-20 10:15:00", "2026-05-20 11:00:00", "2026-05-20 11:01:00"],
    "amount": [50, 120, 30, 200, 250]
}
raw_wide = {"id": [1], "rev_2025": [100], "rev_2026": [120], "cost_2025": [40], "cost_2026": [50]}
raw_nodes = {"emp": ["A", "B", "C"], "mgr": ["B", "C", None]}

df_pl = pl.DataFrame(raw_data)


# ==============================================================================
# 1. CREATING DATAFRAMES
# ==============================================================================
print("\n--> 1. CREATING DATAFRAMES")
print("[Formula/Operation Standard]: pl.DataFrame(raw_dict)")
print("[Formula/Operation Actual  ]: pl.DataFrame(raw_data)")
print("[Polars BEFORE]: Source data is a raw Python dictionary.")
df_pl_m1 = pl.DataFrame(raw_data)
list_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
df_pl_m2 = pl.DataFrame(list_dicts)
print("[Polars AFTER]: Created Dataframe:\n", df_pl_m1.head(3))


# ==============================================================================
# 2. SELECTING COLUMNS
# ==============================================================================
print("\n--> 2. SELECTING COLUMNS")
print("[Formula/Operation Standard]: df.select(['col1', 'col2'])")
print("[Formula/Operation Actual  ]: df_pl.select(['id', 'name'])")
print("[Polars BEFORE]: Available columns:", df_pl.columns)
df_pl_sel1 = df_pl.select(["id", "name"])
df_pl_sel2 = df_pl.select(pl.col("id"), pl.col("name"))
df_pl_sel3 = df_pl.select(cs.by_name("id", "name"))
print("[Polars AFTER]: Selected subset:\n", df_pl_sel1.head(3))


# ==============================================================================
# 3. ADDING COLUMNS
# ==============================================================================
print("\n--> 3. ADDING COLUMNS")
print("[Formula/Operation Standard]: df.with_columns(new_col = pl.col('col1') * scale)")
print("[Formula/Operation Actual  ]: df_pl.with_columns(bonus = pl.col('salary') * 0.2)")
print("[Polars BEFORE]: Columns before addition:", df_pl.columns)
df_pl_add = df_pl.with_columns(bonus = pl.col("salary") * 0.2)
df_pl_add = df_pl_add.with_columns([
    (pl.col("salary") * 0.1).alias("tax"),
    pl.lit("India").alias("country")
])
print("[Polars AFTER]: New columns appended:\n", df_pl_add.select(["id", "bonus", "tax", "country"]).head(3))


# ==============================================================================
# 4. DROPPING COLUMNS
# ==============================================================================
print("\n--> 4. DROPPING COLUMNS")
print("[Formula/Operation Standard]: df.drop(['col1', 'col2'])")
print("[Formula/Operation Actual  ]: df_pl_add.drop(['bonus', 'tax'])")
print("[Polars BEFORE]: Target layout columns:", df_pl_add.columns)
df_pl_drp1 = df_pl_add.drop("bonus")
df_pl_drp2 = df_pl_add.drop(["bonus", "tax"])
df_pl_drp3 = df_pl_add.select(cs.all().exclude("bonus", "tax"))
print("[Polars AFTER]: Specified columns removed:\n", df_pl_drp2.head(3))


# ==============================================================================
# 5. FILTERING ROWS
# ==============================================================================
print("\n--> 5. FILTERING ROWS")
print("[Formula/Operation Standard]: df.filter(pl.col('col1') > val)")
print("[Formula/Operation Actual  ]: df_pl.filter(pl.col('salary') > 6000)")
print("[Polars BEFORE]: Pre-filtered row total count:", len(df_pl))
df_pl_flt1 = df_pl.filter(pl.col("salary") > 6000)
df_pl_flt2 = df_pl.filter((pl.col("salary") > 6000) & (pl.col("dept") == "IT"))
print("[Polars AFTER]: Condition matching row output:\n", df_pl_flt1.head(3))


# ==============================================================================
# 6. GROUPING & AGGREGATION
# ==============================================================================
print("\n--> 6. GROUPING & AGGREGATION")
print("[Formula/Operation Standard]: df.group_by('col1').agg(new_name = pl.col('col2').func())")
print("[Formula/Operation Actual  ]: df_pl.group_by('dept').agg(avg_sal = pl.col('salary').mean(), max_sal = pl.col('salary').max())")
print("[Polars BEFORE]: Granular raw metrics tracking matrix:\n", df_pl.select(["dept", "salary"]))
df_pl_agg1 = df_pl.group_by("dept").agg([
    pl.col("salary").mean().alias("mean"),
    pl.col("salary").max().alias("max")
])
df_pl_agg2 = df_pl.group_by("dept").agg([
    pl.col("salary").mean().alias("avg_sal"),
    pl.col("salary").max().alias("max_sal")
])
print("[Polars AFTER]: Rolled-up metric summary records:\n", df_pl_agg2)


# ==============================================================================
# 7. SORTING
# ==============================================================================
print("\n--> 7. SORTING")
print("[Formula/Operation Standard]: df.sort(['col1', 'col2'], descending=[True, False])")
print("[Formula/Operation Actual  ]: df_pl.sort(['dept', 'salary'], descending=[False, True])")
print("[Polars BEFORE]: Unordered positioning values:\n", df_pl.select(["name", "salary"]))
df_pl_srt1 = df_pl.sort("salary", descending=True)
df_pl_srt2 = df_pl.sort(["dept", "salary"], descending=[False, True])
print("[Polars AFTER]: Ordered descending arrangement layout:\n", df_pl_srt1.head(3))


# ==============================================================================
# 8. NULL HANDLING
# ==============================================================================
print("\n--> 8. NULL HANDLING")
print("[Formula/Operation Standard]: df.with_columns(pl.col('col1').fill_null(fallback_val))")
print("[Formula/Operation Actual  ]: df_pl.with_columns(pl.col('salary').fill_null(0))")
print("[Polars BEFORE]: Missing value locations summary:\n", df_pl.select(["id", "salary"]))
df_pl_nul1 = df_pl.with_columns(pl.col("salary").fill_null(0))
df_pl_nul2 = df_pl.with_columns(pl.col("salary").fill_null(strategy="forward"))
print("[Polars AFTER]: Null positions replaced:\n", df_pl_nul1.tail(3))


# ==============================================================================
# 9. STRING CONVERSIONS
# ==============================================================================
print("\n--> 9. STRING CONVERSIONS")
print("[Formula/Operation Standard]: df.with_columns(pl.col('col1').str.to_uppercase())")
print("[Formula/Operation Actual  ]: df_pl.with_columns(pl.col('name').str.to_uppercase())")
print("[Polars BEFORE]: Base lowercase labels raw formatting:\n", df_pl.select(["id", "name"]).head(3))
df_pl_str1 = df_pl.with_columns(pl.col("name").str.to_uppercase())
df_pl_str2 = df_pl.with_columns(pl.col("name").str.starts_with("a").alias("is_alpha"))
print("[Polars AFTER]: Evaluated string conversion structures:\n", df_pl_str1.select(["id", "name"]).head(3))


# ==============================================================================
# 10. CONDITIONAL UPDATES (IF-THEN-ELSE)
# ==============================================================================
print("\n--> 10. CONDITIONAL UPDATES")
print("[Formula/Operation Standard]: pl.when(condition).then(true_val).otherwise(false_val)")
print("[Formula/Operation Actual  ]: pl.when(pl.col('salary') > 10000).then(pl.lit('High')).otherwise(pl.lit('Low')).alias('type')")
print("[Polars BEFORE]: Base target boundary tracking limits:\n", df_pl.select(["id", "salary"]).head(3))
df_pl_cnd1 = df_pl.with_columns(
    pl.when(pl.col("salary") > 10000).then(pl.lit("High")).otherwise(pl.lit("Low")).alias("type")
)
print("[Polars AFTER]: Categorized label tags generated:\n", df_pl_cnd1.select(["id", "type"]).head(3))


# ==============================================================================
# 11. JOINS & MERGES
# ==============================================================================
print("\n--> 11. JOINS & MERGES")
df_pl2 = pl.DataFrame(raw_data_2)
print("[Formula/Operation Standard]: df1.join(df2, left_on='col1', right_on='col2', how='left')")
print("[Formula/Operation Actual  ]: df_pl.join(df_pl2, left_on='id', right_on='emp_id', how='left')")
print("[Polars BEFORE]: Left Table:\n", df_pl.head(2), "\nRight Table:\n", df_pl2.head(2))
df_pl_jn1 = df_pl.join(df_pl2, left_on="id", right_on="emp_id", how="left")
print("[Polars AFTER]: Joined lookup dimensions result:\n", df_pl_jn1.head(3))


# ==============================================================================
# 12. CONCATENATION (UNION)
# ==============================================================================
print("\n--> 12. CONCATENATION")
df_pl_csrc = pl.DataFrame(raw_data_cat)
print("[Formula/Operation Standard]: pl.concat([df1, df2], how='diagonal')")
print("[Formula/Operation Actual  ]: pl.concat([df_pl, df_pl_csrc], how='diagonal')")
print("[Polars BEFORE]: Table 1 Count:", len(df_pl), "| Table 2 Count:", len(df_pl_csrc))
df_pl_cat1 = pl.concat([df_pl, df_pl_csrc], how="diagonal")
df_pl_right_renamed = df_pl.select(pl.all().name.suffix("_right"))
df_pl_cat2 = pl.concat([df_pl, df_pl_right_renamed], how="horizontal")
print("[Polars AFTER]: Multi-dataset appended blocks unified:\n", df_pl_cat1.tail(3))


# ==============================================================================
# 13. WINDOW FUNCTIONS
# ==============================================================================
print("\n--> 13. WINDOW FUNCTIONS")
print("[Formula/Operation Standard]: pl.col('col1').func().over('partition_col')")
print("[Formula/Operation Actual  ]: pl.col('salary').mean().over('dept').alias('mean_dept')")
print("[Polars BEFORE]: Base data metrics positioning layout:\n", df_pl.select(["id", "dept", "salary"]))
df_pl_wn = df_pl.with_columns([
    pl.col("salary").rank(method="ordinal", descending=True).over("dept").alias("rank"),
    pl.col("salary").mean().over("dept").alias("mean_dept")
])
print("[Polars AFTER]: Partition tracking partition layers appended:\n", df_pl_wn.select(["id", "rank", "mean_dept"]).head(3))


# ==============================================================================
# 14. DATETIME PARSING & TYPE CASTING
# ==============================================================================
print("\n--> 14. DATETIME PARSING & CASTING")
print("[Formula/Operation Standard]: pl.col('col1').str.to_datetime(format=...) AND pl.col('col2').cast(target_type)")
print("[Formula/Operation Actual  ]: pl.col('timestamp_str').str.to_datetime(format='%Y-%m-%d')")
print("[Polars BEFORE]: Column raw operational schema dtypes:\n", df_pl.select(["id", "timestamp_str"]).dtypes)
df_pl_cst = df_pl.with_columns([
    pl.col("timestamp_str").str.to_datetime(format="%Y-%m-%d").alias("timestamp"),
    pl.col("id").cast(pl.Float64)
])
print("[Polars AFTER]: Processed parsed date structures layout:\n", df_pl_cst.select(["id", "timestamp"]).head(3))


# ==============================================================================
# 15. DUPLICATE HANDLING (DEDUPLICATION)
# ==============================================================================
print("\n--> 15. DUPLICATE HANDLING")
print("[Formula/Operation Standard]: df.unique(subset=['col1'], keep='first')")
print("[Formula/Operation Actual  ]: df_pl.unique(subset=['dept'], keep='first')")
print("[Polars BEFORE]: Initial rows trace trace total count:", len(df_pl))
df_pl_ded = df_pl.unique(subset=["dept"], keep="first")
print("[Polars AFTER]: Unique subset matrix partitions isolated:\n", df_pl_ded)


# ==============================================================================
# 16. PIVOT & UNPIVOT (MELT)
# ==============================================================================
print("\n--> 16. PIVOT & UNPIVOT")
df_pl_pvt_src = pl.DataFrame(raw_pivot)
print("[Formula/Operation Standard]: df.pivot(index='col1', on='col2', values='col3')")
print("[Formula/Operation Actual  ]: df_pl_pvt_src.pivot(index='id', on='metric', values='value')")
print("[Polars BEFORE]: Long/Transactional format input frame:\n", df_pl_pvt_src)
df_pl_pvt = df_pl_pvt_src.pivot(index="id", on="metric", values="value")
print("[Polars AFTER]: Wide cross-tabulated structure:\n", df_pl_pvt)


# ==============================================================================
# 17. HANDLING JSON / STRUCT COLUMNS
# ==============================================================================
print("\n--> 17. EXPLODE & JSON UNNEST")
df_pl_jsn_src = pl.DataFrame(raw_json)
print("[Formula/Operation Standard]: df.with_columns(pl.col('col1').str.json_decode(dtype=schema)).unnest('col1')")
print("[Formula/Operation Actual  ]: df_pl_jsn_src.with_columns(pl.col('json_str').str.json_decode(dtype=j_schema)).unnest('json_str')")
print("[Polars BEFORE]: Raw input containing serialized JSON strings:\n", df_pl_jsn_src)
j_schema = pl.Struct([pl.Field("age", pl.Int64), pl.Field("city", pl.String)])
df_pl_st = df_pl_jsn_src.with_columns(pl.col("json_str").str.json_decode(dtype=j_schema)).unnest("json_str")
print("[Polars AFTER]: Flattened key-value dimension layout records:\n", df_pl_st)


# ==============================================================================
# 18. SCD TYPE 1 / UPSERT (FIND LATEST RECORD PER ID)
# ==============================================================================
print("\n--> 18. SCD TYPE 1 / UPSERT")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.sort(['col1', 'col2']).unique(subset=['col1'], keep='last')")
print("[Formula/Operation Actual  ]: df_pl_adv.sort(['emp_id', 'version']).unique(subset=['emp_id'], keep='last')")
print("[Polars BEFORE]: Historical multi-version data records tracking updates:\n", df_pl_adv.select(["emp_id", "version", "salary"]).head(4))
df_pl_lat = df_pl_adv.sort(["emp_id", "version"]).unique(subset=["emp_id"], keep="last")
print("[Polars AFTER]: Latest active record state profile snapshot:\n", df_pl_lat.head(3))


# ==============================================================================
# 19. STRING SPLITTING TO ARRAY & EXPLODE
# ==============================================================================
print("\n--> 19. STRING SPLITTING & EXPLODE")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.with_columns(pl.col('col1').str.split(',')).explode('col1')")
print("[Formula/Operation Actual  ]: df_pl_adv.with_columns(pl.col('skills').str.split(',')).explode('skills')")
print("[Polars BEFORE]: Rows containing delimited compound string metrics:\n", df_pl_adv.select(["emp_id", "skills"]).head(3))
df_pl_fl = df_pl_adv.with_columns(pl.col("skills").str.split(",")).explode("skills")
print("[Polars AFTER]: Normalized granular single-value transactional entries:\n", df_pl_fl.select(["emp_id", "skills"]).head(3))


# ==============================================================================
# 20. CONDITIONAL AGGREGATION / CASE WHEN INSIDE AGG
# ==============================================================================
print("\n--> 20. CONDITIONAL AGGREGATION")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.group_by('col1').agg(pl.col('col2').filter(condition).sum())")
print("[Formula/Operation Actual  ]: df_pl_adv.group_by('version').agg(pl.col('salary').filter(pl.col('dept') == 'IT').sum().alias('it_sal'))")
print("[Polars BEFORE]: Mixed dimensional profile context targets:\n", df_pl_adv.select(["version", "dept", "salary"]).head(4))
df_pl_cag = df_pl_adv.group_by("version").agg(pl.col("salary").filter(pl.col("dept") == "IT").sum().alias("it_sal"))
print("[Polars AFTER]: Segmented partition totals matrix output:\n", df_pl_cag)


# ==============================================================================
# 21. DATE DIFFERENCES & DURATION CALCULATION
# ==============================================================================
print("\n--> 21. DATE DIFFERENCES")
df_pl_dt = pl.DataFrame(raw_dates).with_columns(pl.col("^.*_date$").str.to_datetime())
print("[Formula/Operation Standard]: (df['col1'] - df['col2']).dt.total_days()")
print("[Formula/Operation Actual  ]: (pl.col('end_date') - pl.col('start_date')).dt.total_days()")
print("[Polars BEFORE]: Boundaries dates dataset columns inputs:\n", df_pl_dt.head(2))
df_pl_dt = df_pl_dt.with_columns((pl.col("end_date") - pl.col("start_date")).dt.total_days().alias("days_diff"))
print("[Polars AFTER]: Evaluated integer days values intervals:\n", df_pl_dt.head(3))


# ==============================================================================
# 22. CUMULATIVE AGGREGATIONS (RUNNING TOTAL)
# ==============================================================================
print("\n--> 22. CUMULATIVE AGGREGATIONS")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: pl.col('col1').cum_sum()")
print("[Formula/Operation Actual  ]: pl.col('salary').cum_sum()")
print("[Polars BEFORE]: Transaction sequences base metrics ledger:\n", df_pl_adv.select(["emp_id", "salary"]).head(3))
df_pl_adv = df_pl_adv.with_columns(pl.col("salary").cum_sum().alias("running_total"))
print("[Polars AFTER]: Progression tracking continuous sum metrics:\n", df_pl_adv.select(["emp_id", "running_total"]).head(3))


# ==============================================================================
# 23. COALESCE VALUES (MISSING VALUE FALLBACKS)
# ==============================================================================
print("\n--> 23. COALESCE VALUES")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: pl.coalesce(['col1', 'col2'])")
print("[Formula/Operation Actual  ]: pl.coalesce(['skills', 'dept'])")
print("[Polars BEFORE]: Hierarchical values sources containing sparse empty entries:\n", df_pl_adv.select(["skills", "dept"]).tail(3))
df_pl_adv = df_pl_adv.with_columns(pl.coalesce(["skills", "dept"]).alias("valid_skills"))
print("[Polars AFTER]: Unified non-null strategic data layer:\n", df_pl_adv.select(["emp_id", "valid_skills"]).tail(3))


# ==============================================================================
# 24. NTH HIGHEST VALUE
# ==============================================================================
print("\n--> 24. NTH HIGHEST VALUE")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.select(pl.col('col1').drop_nulls().unique()).sort('col1', descending=True).item(N-1, 0)")
print("[Formula/Operation Actual  ]: df_pl_adv.select(pl.col('salary').drop_nulls().unique()).sort('salary', descending=True).item(1, 0)")
print("[Polars BEFORE]: Raw sample list source scope records:\n", df_pl_adv["salary"].to_list())
nth_pl = df_pl_adv.select(pl.col("salary").drop_nulls().unique()).sort("salary", descending=True).item(1, 0)
print(f"[Polars AFTER]: Extracted target scalar element metric: {nth_pl}")


# ==============================================================================
# 25. TOP N PER GROUP
# ==============================================================================
print("\n--> 25. TOP N PER GROUP")
df_pl_adv = pl.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.sort('col1', descending=True).group_by('col2').head(N)")
print("[Formula/Operation Actual  ]: df_pl_adv.sort('salary', descending=True).group_by('dept').head(3)")
print("[Polars BEFORE]: Unsorted historical grouping records:\n", df_pl_adv.select(["dept", "salary"]).head(4))
df_pl_top1 = df_pl_adv.sort("salary", descending=True).group_by("dept").head(3)
print("[Polars AFTER]: Extracted highest records limits per partition context:\n", df_pl_top1.select(["dept", "salary"]))


# ==============================================================================
# 26. BROADCAST JOIN / MAP-SIDE JOIN
# ==============================================================================
print("\n--> 26. BROADCAST JOIN")
df_pl_skw, df_pl_lk = pl.DataFrame(raw_skewed), pl.DataFrame(raw_lookup)
print("[Formula/Operation Standard]: df_large.join(df_small, on='col1', how='left')")
print("[Formula/Operation Actual  ]: df_pl_skw.join(df_pl_lk, on='key', how='left')")
print("[Polars BEFORE]: Large Skewed Table:\n", df_pl_skw.head(2), "\nSmall Lookup Table:\n", df_pl_lk)
df_pl_bcast = df_pl_skw.join(df_pl_lk, on="key", how="left")
print("[Polars AFTER]: Completed execution map-side inline assignment:\n", df_pl_bcast.head(3))


# ==============================================================================
# 27. SESSIONIZATION / TIME-BASED THRESHOLD WINDOWING
# ==============================================================================
print("\n--> 27. SESSIONIZATION")
df_pl_txs = pl.DataFrame(raw_transactions).with_columns(pl.col("tx_time").str.to_datetime())
print("[Formula/Operation Standard]: (pl.col('col1').diff().over('col2') > threshold).fill_null(True).cum_sum().over('col2')")
print("[Formula/Operation Actual  ]: (pl.col('tx_time').diff().over('user_id') > pl.duration(minutes=5)).fill_null(True).alias('new_session_flag')")
print("[Polars BEFORE]: Sequenced transaction timestamps ledger:\n", df_pl_txs.select(["user_id", "tx_time"]).head(3))
df_pl_txs = df_pl_txs.with_columns(
    (pl.col("tx_time").diff().over("user_id") > pl.duration(minutes=5)).fill_null(True).alias("new_session_flag")
).with_columns(
    pl.col("new_session_flag").cum_sum().over("user_id").alias("session_id")
)
print("[Polars AFTER]: Evaluated session group block tracking boundaries:\n", df_pl_txs.select(["user_id", "session_id"]).head(3))


# ==============================================================================
# 28. COMPLEX MULTI-COLUMN UNPIVOT (MELT)
# ==============================================================================
print("\n--> 28. MULTI-COLUMN UNPIVOT")
df_pl_wd = pl.DataFrame(raw_wide)
print("[Formula/Operation Standard]: df.unpivot(index=['col1'], on=cs.contains('pattern1') | cs.contains('pattern2'), variable_name='var', value_name='val')")
print("[Formula/Operation Actual  ]: df_pl_wd.unpivot(index=['id'], on=cs.contains('rev') | cs.contains('cost'), variable_name='metric_year', value_name='amount')")
print("[Polars BEFORE]: Wide layout cross-tab matrix dataset schema:\n", df_pl_wd)
df_pl_long = df_pl_wd.unpivot(index=["id"], on=cs.contains("rev") | cs.contains("cost"), variable_name="metric_year", value_name="amount")
print("[Polars AFTER]: Normalized long relational layout data model:\n", df_pl_long)


# ==============================================================================
# 29. SELF JOIN (PARENT-CHILD TRACING)
# ==============================================================================
print("\n--> 29. SELF JOIN")
df_pl_nd = pl.DataFrame(raw_nodes)
print("[Formula/Operation Standard]: df.join(df, left_on='col1', right_on='col2', how='left', suffix='_suffix')")
print("[Formula/Operation Actual  ]: df_pl_nd.join(df_pl_nd, left_on='mgr', right_on='emp', how='left', suffix='_grand')")
print("[Polars BEFORE]: Hierarchical adjacency tree graph relationships data:\n", df_pl_nd)
df_pl_tree = df_pl_nd.join(df_pl_nd, left_on="mgr", right_on="emp", how="left", suffix="_grand")
print("[Polars AFTER]: Resolved recursive multi-level hierarchy paths mapping:\n", df_pl_tree)


# ==============================================================================
# 30. TIME SERIES GAP FILLING / REINDEXING
# ==============================================================================
print("\n--> 30. TIME SERIES GAP FILLING")
df_pl_ts = pl.DataFrame({"date": ["2026-05-20", "2026-05-22"], "val": [1, 3]}).with_columns(pl.col("date").str.to_date())
print("[Formula/Operation Standard]: df.upsample(time_column='col1', every='1d').with_columns(pl.col('col2').forward_fill())")
print("[Formula/Operation Actual  ]: df_pl_ts.upsample(time_column='date', every='1d').with_columns(pl.col('val').forward_fill())")
print("[Polars BEFORE]: Scattered dates matrix mapping records (gaps detected):\n", df_pl_ts)
df_pl_filled = df_pl_ts.upsample(time_column="date", every="1d").with_columns(pl.col("val").forward_fill())
print("[Polars AFTER]: Continuous forward-filled timeline execution:\n", df_pl_filled)


# ==============================================================================
# 31. DELTA VARIATIONS (PERCENTAGE CHANGE)
# ==============================================================================
print("\n--> 31. DELTA CHANGE CALCULATIONS")
print("[Formula/Operation Standard]: (pl.col('col1') - pl.col('col1').shift(1)) / pl.col('col1').shift(1)")
print("[Formula/Operation Actual  ]: (pl.col('amount') - pl.col('amount').shift(1)).over('user_id') / pl.col('amount').shift(1).over('user_id')")
print("[Polars BEFORE]: Baseline numeric sequential change targets:\n", df_pl_txs.select(["user_id", "amount"]).head(3))
df_pl_txs = df_pl_txs.with_columns(
    ((pl.col("amount") - pl.col("amount").shift(1)).over("user_id") / pl.col("amount").shift(1).over("user_id")).alias("pct_change")
)
print("[Polars AFTER]: Rolling variance calculations track shifts metrics output:\n", df_pl_txs.select(["user_id", "pct_change"]).tail(3))

print("\n==============================================================================")
print("ALL 31 POLARS OPERATIONS COMPLETED CLEANLY WITH REVISED LOGIC")
print("==============================================================================")
