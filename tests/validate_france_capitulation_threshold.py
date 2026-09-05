from pathlib import Path
import re
import sys


event_file = Path(__file__).parents[1] / "events" / "FRA.txt"
source = event_file.read_text(encoding="utf-8-sig")

match = re.search(
    r"id\s*=\s*TODfrance\.1.*?surrender_progress\s*>\s*([0-9.]+)",
    source,
    flags=re.DOTALL,
)

if not match:
    print("FAIL: TODfrance.1 has no surrender_progress trigger")
    sys.exit(1)

threshold = float(match.group(1))
if threshold != 0.8:
    print(f"FAIL: expected French capitulation threshold 0.8, found {threshold:g}")
    sys.exit(1)

print("PASS: French capitulation threshold is 0.8")
