#!/usr/bin/env python3
# AI Optum: Main Chat Application
# Comprehensive eye examination system with phoropter integration

import asyncio
import sys
import argparse
from steered_chat import AIOptometrist


async def main():
    """Main application entry point"""
    
    parser = argparse.ArgumentParser(
        description="AI Optum - AI Optometrist Eye Examination System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chat_app.py              # Run interactive examination
  python chat_app.py --patient P001  # Run with patient ID
  python chat_app.py --debug      # Enable debug mode
  python chat_app.py --test       # Run test suite
        """
    )
    
    parser.add_argument(
        "--patient",
        type=str,
        default="ANON",
        help="Patient ID (default: ANON)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (simulated phoropter)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run comprehensive test suite"
    )
    
    args = parser.parse_args()
    
    # Run test suite if requested
    if args.test:
        from test_agent import AIOptumTestSuite
        suite = AIOptumTestSuite()
        await suite.run_all_tests()
        return
    
    # Run interactive examination session
    await AIOptometrist.run_session(
        patient_id=args.patient,
        debug_mode=args.debug
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExamination interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
