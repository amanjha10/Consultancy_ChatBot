#!/usr/bin/env python3
"""
Progress Checker
==============

Simple script to check the progress of crawling operations.
"""

import os
import glob
from datetime import datetime

def check_crawling_progress():
    """Check progress of current crawling operations"""
    print("📊 Firecrawl Q&A Module - Progress Check")
    print("=" * 50)
    print(f"📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check log file for progress
    log_file = "firecrawl_qa_module.log"
    if os.path.exists(log_file):
        print(f"\n📋 Recent log entries:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Show last 10 lines
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            for line in recent_lines:
                if line.strip():
                    print(f"   {line.strip()}")
    else:
        print("\n📋 No log file found")
    
    # Check output directories
    print(f"\n📁 Output directories:")
    output_dirs = [d for d in os.listdir('.') if d.endswith('_output') and os.path.isdir(d)]
    
    if output_dirs:
        for dir_name in output_dirs:
            files = os.listdir(dir_name)
            print(f"   📂 {dir_name}: {len(files)} files")
            
            # Check for recent files
            json_files = [f for f in files if f.endswith('.json')]
            csv_files = [f for f in files if f.endswith('.csv')]
            
            if json_files:
                print(f"      📊 JSON files: {len(json_files)}")
            if csv_files:
                print(f"      📈 CSV files: {len(csv_files)}")
    else:
        print("   📂 No output directories found")
    
    # Check if crawling is still running
    print(f"\n🔍 Process status:")
    print("   Check terminal for active crawling processes")
    print("   Look for INFO logs showing URL processing")

def show_latest_results():
    """Show latest crawling results"""
    print("\n📈 Latest Results:")
    
    # Find most recent output directory
    output_dirs = [d for d in os.listdir('.') if d.endswith('_output') and os.path.isdir(d)]
    
    if not output_dirs:
        print("   📂 No output directories found")
        return
    
    # Sort by modification time
    output_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_dir = output_dirs[0]
    
    print(f"   📂 Latest directory: {latest_dir}")
    
    # Look for summary report
    summary_files = glob.glob(f"{latest_dir}/*summary_report*.json")
    if summary_files:
        import json
        latest_summary = max(summary_files, key=os.path.getmtime)
        
        try:
            with open(latest_summary, 'r') as f:
                summary = json.load(f)
                
            print(f"   📊 Summary from: {latest_summary}")
            
            if 'qa_generation_statistics' in summary:
                qa_stats = summary['qa_generation_statistics']
                print(f"      Total Q&A pairs: {qa_stats.get('total_qa_pairs', 'N/A')}")
                print(f"      Average confidence: {qa_stats.get('average_confidence_score', 'N/A')}")
                
                if 'qa_pairs_by_category' in qa_stats:
                    print("      Categories:")
                    for category, count in qa_stats['qa_pairs_by_category'].items():
                        print(f"        - {category}: {count}")
            
            if 'crawl_statistics' in summary:
                crawl_stats = summary['crawl_statistics']
                print(f"      Success rate: {crawl_stats.get('success_rate', 'N/A')}")
                print(f"      URLs processed: {crawl_stats.get('total_urls_processed', 'N/A')}")
                
        except Exception as e:
            print(f"   ❌ Error reading summary: {e}")
    else:
        print("   📊 No summary reports found")

if __name__ == "__main__":
    check_crawling_progress()
    show_latest_results()
