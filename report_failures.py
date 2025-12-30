import asyncio
import sys
import io
from test_agent import AIOptumTestSuite

async def run_and_report():
    # Redirect stdout to capture results
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        suite = AIOptumTestSuite()
        await suite.run_all_tests()
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    
    print("AI OPTUM TEST FAILURE REPORT")
    print("-" * 80)
    for line in output.splitlines():
        if "FAIL" in line or "Expected:" in line or "Got:" in line:
            print(line)
    print("-" * 80)
    print(f"Summary: {output.splitlines()[-1] if output.splitlines() else 'No output'}")

if __name__ == "__main__":
    asyncio.run(run_and_report())
