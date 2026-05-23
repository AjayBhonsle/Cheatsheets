# ==============================================================================
# ADVANCED PYTHON ARCHITECTURES: REFERENCE MASTER SCRIPT
# ==============================================================================

import time
import functools
from typing import Generator, List, Any

print("==============================================================================")
print("1. GENERATORS & COMPUTATIONAL MEMORY STREAMING (YIELD)")
print("==============================================================================")


# Use Case: Processing data files or streams containing millions of rows.
# Normal lists load everything into RAM. Generators stream 1 item at a time (O(1) memory).

# Way A: Generator Function using the 'yield' keyword
def pipeline_log_streamer(limit: int) -> Generator[str, None, None]:
    """Streams mock unstructured log strings on-demand without memory buildup."""
    current_row = 1
    while current_row <= limit:
        # yield pauses execution and returns the current value.
        # When called again, it resumes exactly where it left off.
        yield f"2026-05-23 16:10:00 | BATCH_RECORD_{current_row} | STATUS: SUCCESS"
        current_row += 1


print("--- Way A: Streaming via Yield Generator Function ---")
# Initializing does NOT run the code; it creates a generator object memory pointer
stream_generator = pipeline_log_streamer(limit=1000000)
print(f"Generator Object Initialized: {stream_generator}")

# Pull items on demand using next() or a loop
print(f"First Streamed Element : {next(stream_generator)}")
print(f"Second Streamed Element: {next(stream_generator)}")

# Way B: Generator Expression (Inline shorthand matching comprehension styles)
# Uses parentheses () instead of square brackets []
print("\n--- Way B: Inline Generator Expressions ---")
square_generator = (num ** 2 for num in range(1, 6))

for squared_value in square_generator:
    print(f" -> Next Dynamic Yielded Square: {squared_value}")

print("\n==============================================================================")
print("2. METADATA DECORATORS & LIFE CYCLE TIMERS (@WRAPPER)")
print("==============================================================================")


# Use Case: Standardizing structural boundary logs, metrics tracking, and
# start/end execution snapshots across production pipeline components.

def log_lifecycle(func):
    """Decorator that wraps a function with common start/end lines and execution metrics."""

    @functools.wraps(func)  # Prevents losing original function docstrings/names
    def wrapper_lifecycle_manager(*args, **kwargs):
        # === FIRST LINE / COMMON START STAGE ===
        start_time = time.perf_counter()
        print(f"==================== START: {func.__name__.upper()} ====================")

        # Execute target core function
        result = func(*args, **kwargs)

        # === LAST LINE / COMMON END STAGE ===
        end_time = time.perf_counter()
        print(f"Execution Duration: {end_time - start_time:.6f} seconds")
        print(f"==================== END: {func.__name__.upper()} ====================\n")

        return result

    return wrapper_lifecycle_manager


# Applying the structural boundary decorator syntax
@log_lifecycle
def high_volume_transformation_engine(data_batch: List[int]) -> List[int]:
    """Simulates resource-heavy data pipeline indexing computations."""
    print(" -> Processing and transforming warehouse batch arrays...")
    time.sleep(0.15)  # Simulate latency delay
    return [x * 10 for x in data_batch]


@log_lifecycle
def export_analytics_to_parquet():
    """Simulates compressing and writing files out to cloud object store staging environments."""
    print(" -> Compressing binary chunks and updating storage ledger metadata...")
    time.sleep(0.08)  # Simulate latency delay


print("--- Executing Lifecycles via Wrapped Decorators ---")
output_dataset = high_volume_transformation_engine([1, 2, 3, 4, 5])
export_analytics_to_parquet()

print("==============================================================================")
print("3. ROBUST EXCEPTION MANAGEMENT (TRY / EXCEPT / ELSE / FINALLY)")
print("==============================================================================")


# Use Case: Gracefully handling failures (network dropouts, database down)
# and ensuring external system handles/connections close properly no matter what.

def transactional_pipeline_runner(denominator: int) -> None:
    print(f"--- Starting Transaction Lifecycle with Denominator = {denominator} ---")
    try:
        # Step 1: Attempt operational business logic execution
        scale_factor = 1000
        calculation_result = scale_factor / denominator
        print(f" -> Math Operation Calculation complete: {calculation_result}")

    except ZeroDivisionError as err_zero:
        # Step 2: Handle explicitly known targeted failure anomalies
        print(f" -> CRITICAL FAILURE: Handled specialized dividing by zero logic discrepancy: {err_zero}")

    except Exception as err_generic:
        # Step 3: Catchall unexpected systemic framework errors
        print(f" -> UNEXPECTED FAILURE: Generic runtime system glitch: {err_generic}")

    else:
        # Step 4: Executes ONLY if the try block succeeds with zero faults thrown
        print(" -> TRANSACTION VALIDATION: Chain fully passed without anomalies.")

    finally:
        # Step 5: ALWAYS executes regardless of failure or success.
        # Crucial for dropping database locks, files handles, or network states.
        print(" -> ENVIRONMENT TEARDOWN: Disposing session locks. Cleaning operational workspace.")


# Test Case 1: Triggering explicit zero handling exception path
transactional_pipeline_runner(denominator=0)

# Test Case 2: Triggering smooth execution path
print()
transactional_pipeline_runner(denominator=5)

print("\n==============================================================================")
print("4. ADVANCED PATTERNS: LIST COMPREHENSIONS & CONTEXT MANAGERS")
print("==============================================================================")

# --- A. Advanced Conditional List Comprehension ---
# Syntax: [expression_if_true if condition else expression_if_false for item in iterable]
raw_scores = [12, 85, 43, 90, 60]
audited_tiers = ["ELITE" if score >= 80 else "STANDARD" for score in raw_scores]
print("List Comprehension Mapping Tiers:")
print(f" -> Scores: {raw_scores}")
print(f" -> Result: {audited_tiers}")


# --- B. Custom Native Class Context Managers ---
# Use Case: Customizing connection pool initializers or transactional boundaries.
class PipelineSessionManager:
    """Manages transactional stage connections using 'with' block hooks."""

    def __enter__(self):
        print("\n[CONTEXT START] Connecting to analytical cluster engine database...")
        return "LIVE_DB_SESSION_TOKEN_XYZ"

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("[CONTEXT CLOSE] Committing records. Safely disconnecting from host.")
        # Returning True suppresses any internal exception raised inside the 'with' block
        return False


# Triggering the custom context manager structure lifecycle
with PipelineSessionManager() as live_session:
    print(f" -> Executing data queries within context using: {live_session}")

print("\n==============================================================================")
print("ALL ADVANCED ARCHITECTURES EXECUTED CLEANLY")
print("==============================================================================")
