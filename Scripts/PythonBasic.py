# ==============================================================================
# PYTHON CORE FOUNDATIONS: REFERENCE MASTER CHEAT SHEET
# ==============================================================================

print("==============================================================================")
print("1. OPERATORS (ARITHMETIC, COMPARISON, LOGICAL, ASSIGNMENT)")
print("==============================================================================")

# Baseline values for demonstration
a = 15
b = 4

# --- Arithmetic Operators ---
print("--- Arithmetic Results ---")
print(f"Addition (a + b)        = {a + b}")
print(f"Subtraction (a - b)     = {a - b}")
print(f"Multiplication (a * b)  = {a * b}")
print(f"Division (a / b)        = {a / b}")  # Returns float
print(f"Floor Division (a // b) = {a // b}")  # Truncates decimal point
print(f"Modulus/Remainder (a%b) = {a % b}")  # Remainder of division
print(f"Exponentiation (b ** 3) = {b ** 3}")  # 4 raised to power 3

# --- Comparison Operators ---
print("\n--- Comparison Results (Returns True/False) ---")
print(f"Is equal to? (a == b)      -> {a == b}")
print(f"Not equal to? (a != b)     -> {a != b}")
print(f"Greater than? (a > b)      -> {a > b}")
print(f"Less than or equal? (a<=b) -> {a <= b}")

# --- Logical Operators (Combining Conditions) ---
print("\n--- Logical Results ---")
is_valid = True
is_admin = False
print(f"AND Logic (is_valid and is_admin) -> {is_valid and is_admin}")
print(f"OR Logic  (is_valid or is_admin)  -> {is_valid or is_admin}")
print(f"NOT Logic (not is_valid)          -> {not is_valid}")

# --- Compound Assignment Operators ---
print("\n--- Inline Assignment Results ---")
counter = 10
counter += 5  # Equivalent to: counter = counter + 5
print(f"Value after counter += 5 -> {counter}")
counter *= 2  # Equivalent to: counter = counter * 2
print(f"Value after counter *= 2 -> {counter}")

print("\n==============================================================================")
print("2. CONDITIONAL LOGIC (IF / ELIF / ELSE & TERNARY EXPRESSIONS)")
print("==============================================================================")

# Real-World Use Case: Automated Transaction Alert System
transaction_amount = 4500
account_status = "ACTIVE"
suspicious_activity = False

print("--- Evaluating Transaction Security Rules ---")
if account_status != "ACTIVE":
    print("ALERT: Transaction rejected. Account is currently locked.")
elif suspicious_activity:
    print("ALERT: Transaction flagged by risk assessment engine.")
elif transaction_amount >= 5000:
    print("ALERT: High-value transaction requires manual manager authorization.")
elif transaction_amount >= 1000 and transaction_amount < 5000:
    print("NOTIFICATION: Transaction approved. Standard SMS alert dispatched.")
else:
    print("NOTIFICATION: Low-value transaction approved silently.")

# --- Modern Inline Ternary Assignment Shortcut ---
# Syntax: value_if_true if condition else value_if_false
risk_profile = "HIGH_RISK" if transaction_amount > 2000 else "STANDARD_RISK"
print(f"Inline Ternary Evaluation Result -> Assigned Profile: {risk_profile}")

print("\n==============================================================================")
print("3. FOR LOOPS & ITERATION CONSTRUCTS (RANGE, ENUMERATE, ZIP)")
print("==============================================================================")

# Sample records array tracking pipeline jobs
data_pipelines = ["Ingest_Sales", "Clean_Users", "Load_Warehouse", "Build_Cube"]
execution_times = [45, 12, 120, 35]

print("Way A: Simple Flat Array Iteration:")
for pipeline in data_pipelines:
    print(f" -> Processing Target: {pipeline}")

print("\nWay B: Index Bound Iteration using range(start, stop, step):")
# range(5) yields 0 to 4. range(1, 6, 2) yields 1, 3, 5.
for i in range(0, len(data_pipelines), 2):
    print(f" -> Skipping Step Index {i}: {data_pipelines[i]}")

print("\nWay C: Enumerate Loop (Tracks index tracking and value simultaneously):")
for index, pipeline in enumerate(data_pipelines, start=1):
    print(f" -> Job #{index} Position Name: {pipeline}")

print("\nWay D: Zip Loop (Parallel iteration across two matching array structures):")
for name, duration in zip(data_pipelines, execution_times):
    print(f" -> Pipeline Matrix Check: {name} ran in {duration} seconds.")

print("\n==============================================================================")
print("4. WHILE LOOPS (STATE CONDITIONAL ITERATION)")
print("==============================================================================")

# Real-World Use Case: Simulating network exponential backoff retry logic
retry_attempts = 1
max_allowed_retries = 3
connection_established = False

print("--- Launching Infrastructure Database Connection Loop ---")
while retry_attempts <= max_allowed_retries and not connection_established:
    print(f" -> Connection Attempt #{retry_attempts} in progress...")

    # Simulate a successful connection event on the 3rd try
    if retry_attempts == 3:
        connection_established = True
        print(" -> Network acknowledgement received safely.")
    else:
        print(" -> Warning: Timeout detected. Increasing backoff wait state.")

    retry_attempts += 1  # Increment state to avoid falling into infinite loop

print(f"Final Loop Resolution State -> Connection Active: {connection_established}")

print("\n==============================================================================")
print("5. LOOP CONTROL STATEMENTS (BREAK, CONTINUE, ELSE BLOCKS)")
print("==============================================================================")

# Real-World Use Case: Scanning system file blocks for a fatal error token
log_events = ["INFO: Init", "DEBUG: Parsing", "SKIP: Null row", "WARN: Memory", "FATAL: Crash", "INFO: Done"]

print("--- Scanning Log Array Streams ---")
for event in log_events:
    if "SKIP" in event:
        # continue immediately skips the remaining lines of the current loop iteration
        continue

    print(f"Processing Event Log Entry: {event}")

    if "FATAL" in event:
        print("ALERT: Termination sequence encountered. Stopping file scan immediately.")
        break  # break completely breaks out of the loop infrastructure immediately

print("\n--- Understanding Loop Else Blocks ---")
# The 'else' block on a loop executes ONLY if the loop finishes normally without striking a 'break'
for number in [1, 3, 5]:
    if number % 2 == 0:
        print("Found an even number!")
        break
else:
    print("Loop Else Triggered: Iteration completed fully. No even numbers found.")

print("\n==============================================================================")
print("ALL FOUNDATION BASICS EXECUTED CLEANLY")
print("==============================================================================")
