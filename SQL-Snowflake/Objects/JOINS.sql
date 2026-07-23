/* All types of JOINS (Inner, Left, Right, Full, Cross and LEFT with IS NOT DISTINCT) */
-- 1. CREATE TABLES
/* All types of JOINS (Inner, Left, Right, Full, Cross and LEFT with IS NOT DISTINCT) */

-- 1. CREATE TABLES
CREATE OR REPLACE TABLE Table_A (id INT, val VARCHAR(50));
CREATE OR REPLACE TABLE Table_B (id INT, val VARCHAR(50));

-- 2. INSERT TEST DATA WITH NULL VALUES
INSERT INTO Table_A (id, val) VALUES (1, 'Apple'), (2, 'Banana'), (NULL, 'Cherry'), (4, 'Date');
INSERT INTO Table_B (id, val) VALUES (1, 'Red'), (3, 'Green'), (NULL, 'No Color'), (5, 'Blue');


SELECT * FROM Table_A;
/*
+------+--------+
| ID   | VAL    |
+------+--------+
| 1    | Apple  |
| 2    | Banana |
| NULL | Cherry |
| 4    | Date   |
+------+--------+
*/

SELECT * FROM Table_B;
/*
+------+----------+
| ID   | VAL      |
+------+----------+
| 1    | Red      |
| 3    | Green    |
| NULL | No Color |
| 5    | Blue     |
+------+----------+
*/

-- INNER JOIN
SELECT *
FROM Table_A a 
INNER JOIN Table_B b 
   ON a.id = b.id;
/*
+------+-------+------+------+
| ID   | VAL   | ID   | VAL  |
+------+-------+------+------+
| 1    | Apple | 1    | Red  |
+------+-------+------+------+
*/

-- LEFT JOIN
SELECT *
FROM Table_A a 
LEFT JOIN Table_B b 
   ON a.id = b.id;
/*
+------+--------+------+------+
| ID   | VAL    | ID   | VAL  |
+------+--------+------+------+
| 1    | Apple  | 1    | Red  |
| 2    | Banana | NULL | NULL |
| NULL | Cherry | NULL | NULL |
| 4    | Date   | NULL | NULL |
+------+--------+------+------+
*/

-- RIGHT JOIN
SELECT *
FROM Table_A a 
RIGHT JOIN Table_B b 
   ON a.id = b.id;
/*
+------+-------+------+----------+
| ID   | VAL   | ID   | VAL      |
+------+-------+------+----------+
| 1    | Apple | 1    | Red      |
| NULL | NULL  | 3    | Green    |
| NULL | NULL  | NULL | No Color |
| NULL | NULL  | 5    | Blue     |
+------+-------+------+----------+
*/

-- INNER JOIN WITH IS NOT DISTINCT FROM (Matches NULL as a valid value)
SELECT *
FROM Table_A a 
INNER JOIN Table_B b ON a.id IS NOT DISTINCT FROM b.id;
/*
+------+--------+------+----------+
| ID   | VAL    | ID   | VAL      |
+------+--------+------+----------+
| 1    | Apple  | 1    | Red      |
| NULL | Cherry | NULL | No Color |
+------+--------+------+----------+
*/

-------------------------------------------------------------------------------------------------------------------------

-- Cross Join
SELECT *
FROM Table_A a 
CROSS JOIN Table_B b;
/*
+------+--------+------+----------+
| ID   | VAL    | ID   | VAL      |
+------+--------+------+----------+
| 1    | Apple  | 1    | Red      |
| 1    | Apple  | 3    | Green    |
| 1    | Apple  | NULL | No Color |
| 1    | Apple  | 5    | Blue     |
| 2    | Banana | 1    | Red      |
| 2    | Banana | 3    | Green    |
| ...  | ...    | ...  | ...      |
+------+--------+------+----------+
(16 Rows total: 4 * 4)
*/

-- Full Join
SELECT *
FROM Table_A a 
FULL JOIN Table_B b ON a.ID = b.ID;
/*
+------+--------+------+----------+
| ID   | VAL    | ID   | VAL      |
+------+--------+------+----------+
| 1    | Apple  | 1    | Red      |
| 2    | Banana | NULL | NULL     |
| NULL | Cherry | NULL | NULL     |
| 4    | Date   | NULL | NULL     |
| NULL | NULL   | 3    | Green    |
| NULL | NULL   | NULL | No Color |
| NULL | NULL   | 5    | Blue     |
+------+--------+------+----------+
*/
-- All from Left, all from Right -- and single row where Matched
