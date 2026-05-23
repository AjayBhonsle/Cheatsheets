import numpy as np
import pandas as pd

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

df_pd = pd.DataFrame(raw_data)


# ==============================================================================
# 1. CREATING DATAFRAMES
# ==============================================================================
print("\n--> 1. CREATING DATAFRAMES")
print("[Formula/Operation Standard]: pd.DataFrame(raw_dict)")
print("[Formula/Operation Actual  ]: pd.DataFrame(raw_data)")
print("[Pandas BEFORE]: Source data is a raw Python dictionary.")
df_pd_m1 = pd.DataFrame(raw_data)
list_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
df_pd_m2 = pd.DataFrame(list_dicts)
print("[Pandas AFTER]: Created Dataframe:\n", df_pd_m1.head(5))


# ==============================================================================
# 2. SELECTING COLUMNS
# ==============================================================================
print("\n--> 2. SELECTING COLUMNS")
print("[Formula/Operation Standard]: df[['col1', 'col2']] OR df.loc[:, ['col1', 'col2']]")
print("[Formula/Operation Actual  ]: df_pd[['id', 'name']] OR df_pd.loc[:, ['id', 'name']]")
print("[Pandas BEFORE]: Available columns:", list(df_pd.columns))
df_pd_sel1 = df_pd[["id", "name"]]
df_pd_sel2 = df_pd.loc[:, ["id", "name"]]
df_pd_sel3 = df_pd.filter(items=["id", "name"])
print("[Pandas AFTER]: Selected subset:\n", df_pd_sel1.head(5))


# ==============================================================================
# 3. ADDING COLUMNS
# ==============================================================================
print("\n--> 3. ADDING COLUMNS")
print("[Formula/Operation Standard]: df['new_col'] = df['col1'] * scale OR df.assign(new_col=...)")
print("[Formula/Operation Actual  ]: df_pd_add['bonus'] = df_pd_add['salary'] * 0.2")
print("[Pandas BEFORE]: Columns before addition:", list(df_pd.columns))
df_pd_add = df_pd.copy()
df_pd_add["bonus"] = df_pd_add["salary"] * 0.2
df_pd_add = df_pd_add.assign(tax=df_pd_add["salary"] * 0.1)
print("[Pandas AFTER]: New columns appended:\n", df_pd_add[["id", "bonus", "tax"]].head(5))


# ==============================================================================
# 4. DROPPING COLUMNS
# ==============================================================================
print("\n--> 4. DROPPING COLUMNS")
print("[Formula/Operation Standard]: df.drop(columns=['col1', 'col2'])")
print("[Formula/Operation Actual  ]: df_pd_add.drop(columns=['bonus', 'tax'])")
print("[Pandas BEFORE]: Target layout columns:", list(df_pd_add.columns))
df_pd_drp1 = df_pd_add.drop(columns=["bonus", "tax"])
df_pd_drp2 = df_pd_add.drop(["bonus", "tax"], axis=1)
print("[Pandas AFTER]: Specified columns removed:\n", df_pd_drp1.head(5))


# ==============================================================================
# 5. FILTERING ROWS
# ==============================================================================
print("\n--> 5. FILTERING ROWS")
print("[Formula/Operation Standard]: df[df['col1'] > val] OR df.query('col1 > val')")
print("[Formula/Operation Actual  ]: df_pd[df_pd['salary'] > 6000]")
print("[Pandas BEFORE]: Pre-filtered row total count:", len(df_pd))
df_pd_flt1 = df_pd[df_pd["salary"] > 6000]
df_pd_flt2 = df_pd.query("salary > 6000")
df_pd_flt3 = df_pd.loc[df_pd["salary"] > 6000]
print("[Pandas AFTER]: Condition matching row output:\n", df_pd_flt1.head(5))


# ==============================================================================
# 6. GROUPING & AGGREGATION
# ==============================================================================
print("\n--> 6. GROUPING & AGGREGATION")
print("[Formula/Operation Standard]: df.groupby('col1').agg(new_name=('col2', 'func')).reset_index()")
print("[Formula/Operation Actual  ]: df_pd.groupby('dept').agg(avg_sal=('salary', 'mean'), max_sal=('salary', 'max')).reset_index()")
print("[Pandas BEFORE]: Granular raw metrics tracking matrix:\n", df_pd[["dept", "salary"]])
df_pd_agg1 = df_pd.groupby("dept")["salary"].agg(["mean", "max"]).reset_index()
df_pd_agg2 = df_pd.groupby("dept").agg(avg_sal=("salary", "mean"), max_sal=("salary", "max")).reset_index()
print("[Pandas AFTER]: Rolled-up metric summary records:\n", df_pd_agg2)


# ==============================================================================
# 7. SORTING
# ==============================================================================
print("\n--> 7. SORTING")
print("[Formula/Operation Standard]: df.sort_values(by=['col1', 'col2'], ascending=[True, False])")
print("[Formula/Operation Actual  ]: df_pd.sort_values(['dept', 'salary'], ascending=[True, False])")
print("[Pandas BEFORE]: Unordered positioning values:\n", df_pd[["name", "salary"]])
df_pd_srt1 = df_pd.sort_values("salary", ascending=False)
df_pd_srt2 = df_pd.sort_values(["dept", "salary"], ascending=[True, False])
print("[Pandas AFTER]: Ordered descending arrangement layout:\n", df_pd_srt1.head(5))


# ==============================================================================
# 8. NULL HANDLING
# ==============================================================================
print("\n--> 8. NULL HANDLING")
print("[Formula/Operation Standard]: df.fillna({'col1': fallback_val}) OR df.ffill()")
print("[Formula/Operation Actual  ]: df_pd.fillna({'salary': 0})")
print("[Pandas BEFORE]: Missing value locations summary:\n", df_pd[["id", "salary"]])
df_pd_nul1 = df_pd.fillna({"salary": 0})
df_pd_nul2 = df_pd.ffill()
print("[Pandas AFTER]: Null positions replaced:\n", df_pd_nul1.tail(5))


# ==============================================================================
# 9. STRING CONVERSIONS
# ==============================================================================
print("\n--> 9. STRING CONVERSIONS")
print("[Formula/Operation Standard]: df['col1'].str.upper() OR df['col1'].str.startswith('str')")
print("[Formula/Operation Actual  ]: df_pd_str1['name'].str.upper()")
print("[Pandas BEFORE]: Base lowercase labels raw formatting:\n", df_pd[["id", "name"]].head(5))
df_pd_str1 = df_pd.copy()
df_pd_str1["name"] = df_pd_str1["name"].str.upper()
df_pd_str2 = df_pd.copy()
df_pd_str2["is_alpha"] = df_pd_str2["name"].str.startswith("a")
print("[Pandas AFTER]: Evaluated string conversion structures:\n", df_pd_str1[["id", "name"]].head(5))


# ==============================================================================
# 10. CONDITIONAL UPDATES (IF-THEN-ELSE)
# ==============================================================================
print("\n--> 10. CONDITIONAL UPDATES")
print("[Formula/Operation Standard]: np.where(condition, true_val, false_val)")
print("[Formula/Operation Actual  ]: np.where(df_pd_cnd1['salary'] > 10000, 'High', 'Low')")
print("[Pandas BEFORE]: Base target boundary tracking limits:\n", df_pd[["id", "salary"]].head(5))
df_pd_cnd1 = df_pd.copy()
df_pd_cnd1["type"] = np.where(df_pd_cnd1["salary"] > 10000, "High", "Low")
df_pd_cnd2 = df_pd.copy()
df_pd_cnd2.loc[df_pd_cnd2["salary"] > 10000, "type"] = "High"
print("[Pandas AFTER]: Categorized label tags generated:\n", df_pd_cnd1[["id", "type"]].head(5))


# ==============================================================================
# 11. JOINS & MERGES
# ==============================================================================
print("\n--> 11. JOINS & MERGES")
df_pd2 = pd.DataFrame(raw_data_2)
print("[Formula/Operation Standard]: pd.merge(df1, df2, left_on='col1', right_on='col2', how='left')")
print("[Formula/Operation Actual  ]: pd.merge(df_pd, df_pd2, left_on='id', right_on='emp_id', how='left')")
print("[Pandas BEFORE]: Left Table:\n", df_pd.head(5), "\nRight Table:\n", df_pd2.head(5))
df_pd_jn1 = pd.merge(df_pd, df_pd2, left_on="id", right_on="emp_id", how="left")
df_pd_jn2 = df_pd.set_index("id").join(df_pd2.set_index("emp_id"), how="left")
print("[Pandas AFTER]: Joined lookup dimensions result:\n", df_pd_jn1.head(5))


# ==============================================================================
# 12. CONCATENATION (UNION)
# ==============================================================================
print("\n--> 12. CONCATENATION")
df_pd_csrc = pd.DataFrame(raw_data_cat)
print("[Formula/Operation Standard]: pd.concat([df1, df2], axis=0, ignore_index=True)")
print("[Formula/Operation Actual  ]: pd.concat([df_pd, df_pd_csrc], axis=0, ignore_index=True)")
print("[Pandas BEFORE]: Table 1 Count:", len(df_pd), "| Table 2 Count:", len(df_pd_csrc))
df_pd_cat1 = pd.concat([df_pd, df_pd_csrc], axis=0, ignore_index=True)
df_pd_cat2 = pd.concat([df_pd, df_pd], axis=1)
print("[Pandas AFTER]: Multi-dataset appended blocks unified:\n", df_pd_cat1.tail(5))


# ==============================================================================
# 13. WINDOW FUNCTIONS
# ==============================================================================
print("\n--> 13. WINDOW FUNCTIONS")
print("[Formula/Operation Standard]: df.groupby('col1')['col2'].transform('func') OR .rank()")
print("[Formula/Operation Actual  ]: df_pd_wn.groupby('dept')['salary'].transform('mean')")
print("[Pandas BEFORE]: Base data metrics positioning layout:\n", df_pd[["id", "dept", "salary"]])
df_pd_wn = df_pd.copy()
df_pd_wn["rank"] = df_pd_wn.groupby("dept")["salary"].rank(method="first", ascending=False)
df_pd_wn["mean_dept"] = df_pd_wn.groupby("dept")["salary"].transform("mean")
print("[Pandas AFTER]: Partition tracking partition layers appended:\n", df_pd_wn[["id", "rank", "mean_dept"]].head(5))


# ==============================================================================
# 14. DATETIME PARSING & TYPE CASTING
# ==============================================================================
print("\n--> 14. DATETIME PARSING & CASTING")
print("[Formula/Operation Standard]: pd.to_datetime(df['col1'], format=...) AND df['col2'].astype(target_type)")
print("[Formula/Operation Actual  ]: pd.to_datetime(df_pd_cst['timestamp_str'], format='%Y-%m-%d')")
print("[Pandas BEFORE]: Column raw operational schema dtypes:\n", df_pd[["id", "timestamp_str"]].dtypes)
df_pd_cst = df_pd.copy()
df_pd_cst["timestamp"] = pd.to_datetime(df_pd_cst["timestamp_str"], format="%Y-%m-%d")
df_pd_cst["id"] = df_pd_cst["id"].astype(np.float64)
print("[Pandas AFTER]: Processed parsed date structures layout:\n", df_pd_cst[["id", "timestamp"]].head(5))


# ==============================================================================
# 15. DUPLICATE HANDLING (DEDUPLICATION)
# ==============================================================================
print("\n--> 15. DUPLICATE HANDLING")
print("[Formula/Operation Standard]: df.drop_duplicates(subset=['col1'], keep='first')")
print("[Formula/Operation Actual  ]: df_pd.drop_duplicates(subset=['dept'], keep='first')")
print("[Pandas BEFORE]: Initial rows trace trace total count:", len(df_pd))
df_pd_ded = df_pd.drop_duplicates(subset=["dept"], keep="first")
print("[Pandas AFTER]: Unique subset matrix partitions isolated:\n", df_pd_ded)


# ==============================================================================
# 16. PIVOT & UNPIVOT (MELT)
# ==============================================================================
print("\n--> 16. PIVOT & UNPIVOT")
df_pd_pvt_src = pd.DataFrame(raw_pivot)
print("[Formula/Operation Standard]: df.pivot(index='col1', columns='col2', values='col3').reset_index()")
print("[Formula/Operation Actual  ]: df_pd_pvt_src.pivot(index='id', columns='metric', values='value').reset_index()")
print("[Pandas BEFORE]: Long/Transactional format input frame:\n", df_pd_pvt_src)
df_pd_pvt = df_pd_pvt_src.pivot(index="id", columns="metric", values="value").reset_index()
print("[Pandas AFTER]: Wide cross-tabulated structure:\n", df_pd_pvt)


# ==============================================================================
# 17. HANDLING JSON / STRUCT COLUMNS
# ==============================================================================
print("\n--> 17. EXPLODE & JSON UNNEST")
df_pd_jsn_src = pd.DataFrame(raw_json)
print("[Formula/Operation Standard]: pd.json_normalize(df['col1'].apply(eval))")
print("[Formula/Operation Actual  ]: pd.json_normalize(df_pd_jsn_src['json_str'].apply(eval))")
print("[Pandas BEFORE]: Raw input containing serialized JSON strings:\n", df_pd_jsn_src)
df_pd_jsn = pd.json_normalize(df_pd_jsn_src["json_str"].apply(eval))
print("[Pandas AFTER]: Flattened key-value dimension layout records:\n", df_pd_jsn)


# ==============================================================================
# 18. SCD TYPE 1 / UPSERT (FIND LATEST RECORD PER ID)
# ==============================================================================
print("\n--> 18. SCD TYPE 1 / UPSERT")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.sort_values(['col1', 'col2']).drop_duplicates(subset=['col1'], keep='last')")
print("[Formula/Operation Actual  ]: df_pd_adv.sort_values(['emp_id', 'version']).drop_duplicates(subset=['emp_id'], keep='last')")
print("[Pandas BEFORE]: Historical multi-version data records tracking updates:\n", df_pd_adv[["emp_id", "version", "salary"]].head(5))
df_pd_lat = df_pd_adv.sort_values(["emp_id", "version"]).drop_duplicates(subset=["emp_id"], keep="last")
print("[Pandas AFTER]: Latest active record state profile snapshot:\n", df_pd_lat.head(5))


# ==============================================================================
# 19. STRING SPLITTING TO ARRAY & EXPLODE
# ==============================================================================
print("\n--> 19. STRING SPLITTING & EXPLODE")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.assign(col1=df['col1'].str.split(',')).explode('col1')")
print("[Formula/Operation Actual  ]: df_pd_adv.assign(skills=df_pd_adv['skills'].str.split(',')).explode('skills')")
print("[Pandas BEFORE]: Rows containing delimited compound string metrics:\n", df_pd_adv[["emp_id", "skills"]].head(5))
df_pd_fl = df_pd_adv.assign(skills=df_pd_adv["skills"].str.split(",")).explode("skills")
print("[Pandas AFTER]: Normalized granular single-value transactional entries:\n", df_pd_fl[["emp_id", "skills"]].head(5))


# ==============================================================================
# 20. CONDITIONAL AGGREGATION / CASE WHEN INSIDE AGG
# ==============================================================================
print("\n--> 20. CONDITIONAL AGGREGATION")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.assign(matched_val=np.where(cond, col1, 0)).groupby('col2')['matched_val'].sum()")
print("[Formula/Operation Actual  ]: df_pd_adv.assign(it_sal=np.where(df_pd_adv['dept'] == 'IT', df_pd_adv['salary'], 0)).groupby('version')['it_sal'].sum().reset_index()")
print("[Pandas BEFORE]: Mixed dimensional profile context targets:\n", df_pd_adv[["version", "dept", "salary"]].head(5))
df_pd_cag = df_pd_adv.assign(it_sal=np.where(df_pd_adv["dept"] == "IT", df_pd_adv["salary"], 0)).groupby("version")["it_sal"].sum().reset_index()
print("[Pandas AFTER]: Segmented partition totals matrix output:\n", df_pd_cag)


# ==============================================================================
# 21. DATE DIFFERENCES & DURATION CALCULATION
# ==============================================================================
print("\n--> 21. DATE DIFFERENCES")
df_pd_dt = pd.DataFrame(raw_dates).apply(pd.to_datetime)
print("[Formula/Operation Standard]: (df['col1'] - df['col2']).dt.days")
print("[Formula/Operation Actual  ]: (df_pd_dt['end_date'] - df_pd_dt['start_date']).dt.days")
print("[Pandas BEFORE]: Boundaries dates dataset columns inputs:\n", df_pd_dt.head(5))
df_pd_dt["days_diff"] = (df_pd_dt["end_date"] - df_pd_dt["start_date"]).dt.days
print("[Pandas AFTER]: Evaluated integer days values intervals:\n", df_pd_dt.head(5))


# ==============================================================================
# 22. CUMULATIVE AGGREGATIONS (RUNNING TOTAL)
# ==============================================================================
print("\n--> 22. CUMULATIVE AGGREGATIONS")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df['col1'].cumsum()")
print("[Formula/Operation Actual  ]: df_pd_adv['salary'].cumsum()")
print("[Pandas BEFORE]: Transaction sequences base metrics ledger:\n", df_pd_adv[["emp_id", "salary"]].head(5))
df_pd_adv["running_total"] = df_pd_adv["salary"].cumsum()
print("[Pandas AFTER]: Progression tracking continuous sum metrics:\n", df_pd_adv[["emp_id", "running_total"]].head(5))


# ==============================================================================
# 23. COALESCE VALUES (MISSING VALUE FALLBACKS)
# ==============================================================================
print("\n--> 23. COALESCE VALUES")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df['col1'].combine_first(df['col2'])")
print("[Formula/Operation Actual  ]: df_pd_adv['skills'].combine_first(df_pd_adv['dept'])")
print("[Pandas BEFORE]: Hierarchical values sources containing sparse empty entries:\n", df_pd_adv[["skills", "dept"]].tail(5))
df_pd_adv["valid_skills"] = df_pd_adv["skills"].combine_first(df_pd_adv["dept"])
print("[Pandas AFTER]: Unified non-null strategic data layer:\n", df_pd_adv[["emp_id", "valid_skills"]].tail(5))


# ==============================================================================
# 24. NTH HIGHEST VALUE
# ==============================================================================
print("\n--> 24. NTH HIGHEST VALUE")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df['col1'].dropna().drop_duplicates().nlargest(N).iloc[-1]")
print("[Formula/Operation Actual  ]: df_pd_adv['salary'].dropna().drop_duplicates().nlargest(2).iloc[-1]")
print("[Pandas BEFORE]: Raw sample list source scope records:\n", df_pd_adv["salary"].tolist())
nth_pd = df_pd_adv["salary"].dropna().drop_duplicates().nlargest(2).iloc[-1]
print(f"[Pandas AFTER]: Extracted target scalar element metric: {nth_pd}")


# ==============================================================================
# 25. TOP N PER GROUP
# ==============================================================================
print("\n--> 25. TOP N PER GROUP")
df_pd_adv = pd.DataFrame(raw_advanced)
print("[Formula/Operation Standard]: df.sort_values('col1', ascending=False).groupby('col2').head(N)")
print("[Formula/Operation Actual  ]: df_pd_adv.sort_values('salary', ascending=False).groupby('dept').head(5)")
print("[Pandas BEFORE]: Unsorted historical grouping records:\n", df_pd_adv[["dept", "salary"]].head(5))
df_pd_top1 = df_pd_adv.sort_values("salary", ascending=False).groupby("dept").head(5)
print("[Pandas AFTER]: Extracted highest records limits per partition context:\n", df_pd_top1[["dept", "salary"]])


# ==============================================================================
# 26. BROADCAST JOIN / MAP-SIDE JOIN
# ==============================================================================
print("\n--> 26. BROADCAST JOIN")
df_pd_skw, df_pd_lk = pd.DataFrame(raw_skewed), pd.DataFrame(raw_lookup)
print("[Formula/Operation Standard]: df_large['col1'].map(df_small.set_index('col1')['col2'])")
print("[Formula/Operation Actual  ]: df_pd_skw['key'].map(df_pd_lk.set_index('key')['val_y'])")
print("[Pandas BEFORE]: Large Skewed Table:\n", df_pd_skw.head(5), "\nSmall Lookup Table:\n", df_pd_lk)
df_pd_skw["val_y"] = df_pd_skw["key"].map(df_pd_lk.set_index("key")["val_y"])
print("[Pandas AFTER]: Completed execution map-side inline assignment:\n", df_pd_skw.head(5))


# ==============================================================================
# 27. SESSIONIZATION / TIME-BASED THRESHOLD WINDOWING
# ==============================================================================
print("\n--> 27. SESSIONIZATION")
df_pd_txs = pd.DataFrame(raw_transactions).assign(tx_time=lambda df: pd.to_datetime(df["tx_time"]))
print("[Formula/Operation Standard]: Flag breaks -> df.groupby('col1')['col2'].diff() > threshold -> .cumsum()")
print("[Formula/Operation Actual  ]: df_pd_txs.groupby('user_id')['tx_time'].diff() > pd.Timedelta(minutes=5)")
print("[Pandas BEFORE]: Sequenced transaction timestamps ledger:\n", df_pd_txs[["user_id", "tx_time"]].head(5))
df_pd_txs["time_diff"] = df_pd_txs.groupby("user_id")["tx_time"].diff()
df_pd_txs["new_session"] = df_pd_txs["time_diff"].isna() | (df_pd_txs["time_diff"] > pd.Timedelta(minutes=5))
df_pd_txs["session_id"] = df_pd_txs.groupby("user_id")["new_session"].cumsum()
print("[Pandas AFTER]: Evaluated session group block tracking boundaries:\n", df_pd_txs[["user_id", "session_id"]].head(5))


# ==============================================================================
# 28. COMPLEX MULTI-COLUMN UNPIVOT (MELT)
# ==============================================================================
print("\n--> 28. MULTI-COLUMN UNPIVOT")
df_pd_wd = pd.DataFrame(raw_wide)
print("[Formula/Operation Standard]: pd.wide_to_long(df, stubnames=['stub1', 'stub2'], i='col1', j='suffix_col', sep='_')")
print("[Formula/Operation Actual  ]: pd.wide_to_long(df_pd_wd, stubnames=['rev', 'cost'], i='id', j='year', sep='_')")
print("[Pandas BEFORE]: Wide layout cross-tab matrix dataset schema:\n", df_pd_wd)
df_pd_long = pd.wide_to_long(df_pd_wd, stubnames=["rev", "cost"], i="id", j="year", sep="_").reset_index()
print("[Pandas AFTER]: Normalized long relational layout data model:\n", df_pd_long)


# ==============================================================================
# 29. SELF JOIN (PARENT-CHILD TRACING)
# ==============================================================================
print("\n--> 29. SELF JOIN")
df_pd_nd = pd.DataFrame(raw_nodes)
print("[Formula/Operation Standard]: df.merge(df, left_on='col1', right_on='col2', suffixes=('', '_suffix'))")
print("[Formula/Operation Actual  ]: df_pd_nd.merge(df_pd_nd, left_on='mgr', right_on='emp', how='left', suffixes=('', '_grand'))")
print("[Pandas BEFORE]: Hierarchical adjacency tree graph relationships data:\n", df_pd_nd)
df_pd_tree = df_pd_nd.merge(df_pd_nd, left_on="mgr", right_on="emp", how="left", suffixes=("", "_grand"))
print("[Pandas AFTER]: Resolved recursive multi-level hierarchy paths mapping:\n", df_pd_tree)


# ==============================================================================
# 30. TIME SERIES GAP FILLING / REINDEXING
# ==============================================================================
print("\n--> 30. TIME SERIES GAP FILLING")
df_pd_ts = pd.DataFrame({"date": pd.to_datetime(["2026-05-20", "2026-05-22"]), "val": [1, 3]})
print("[Formula/Operation Standard]: df.set_index('col1').reindex(pd.date_range(start, end, freq='D')).ffill()")
print("[Formula/Operation Actual  ]: df_pd_ts.set_index('date').reindex(pd.date_range('2026-05-20', '2026-05-22', freq='D')).ffill()")
print("[Pandas BEFORE]: Scattered dates matrix mapping records (gaps detected):\n", df_pd_ts)
df_pd_filled = df_pd_ts.set_index("date").reindex(pd.date_range("2026-05-20", "2026-05-22", freq="D")).ffill().reset_index(names="date")
print("[Pandas AFTER]: Continuous forward-filled timeline execution:\n", df_pd_filled)


# ==============================================================================
# 31. DELTA VARIATIONS (PERCENTAGE CHANGE)
# ==============================================================================
print("\n--> 31. DELTA CHANGE CALCULATIONS")
print("[Formula/Operation Standard]: df.groupby('col1')['col2'].pct_change()")
print("[Formula/Operation Actual  ]: df_pd_txs.groupby('user_id')['amount'].pct_change()")
print("[Pandas BEFORE]: Baseline numeric sequential change targets:\n", df_pd_txs[["user_id", "amount"]].head(5))
df_pd_txs["pct_change"] = df_pd_txs.groupby("user_id")["amount"].pct_change()
print("[Pandas AFTER]: Rolling variance calculations track shifts metrics output:\n", df_pd_txs[["user_id", "pct_change"]].tail(5))

print("\n==============================================================================")
print("ALL 31 PANDAS OPERATIONS COMPLETED CLEANLY WITH REVISED LOGIC")
print("==============================================================================")
