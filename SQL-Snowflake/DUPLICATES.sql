-- WAY - 1 (Smaller Tables)
-- If your entire row is duplicated across all columns, you can clear the table and replace it with unique rows using a single command

INSERT OVERWRITE INTO your_table 
SELECT DISTINCT * FROM your_table;

-- WAY - 2 (Massive datasets)
-- For massive datasets, it is often faster and safer to create a clean, deduplicated staging table and then swap it with the original table

CREATE OR REPLACE TABLE your_table_clean AS 
SELECT DISTINCT * 
FROM your_table;
-- QUALIFY ROW_NUMBER() OVER (PARTITION BY unique_id_column ORDER BY optional_timestamp_column DESC) = 1;
-- Use Qualify if some identifier are there for unique row

ALTER TABLE your_table SWAP WITH your_table_clean;

DROP TABLE your_table_clean;

-- WAY - 3 (General Delete)
DELETE FROM target_table tgt
USING reference_table ref
WHERE tgt.join_column = ref.join_column
  AND ref.filter_column = 'some_value'; -- Optional filter

-- OR
DELETE FROM target_table tgt
WHERE EXISTS (
    SELECT 1 
    FROM reference_table ref 
    WHERE tgt.join_column = ref.join_column
      AND ref.filter_column = 'some_value' -- Optional filter
);
