#!/usr/bin/env python3
"""
Coverage analysis and reporting tool for SQL SysHub tests.

This script provides detailed analysis of test coverage, identifies
gaps, and generates reports for continuous monitoring.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple


class CoverageAnalyzer:
    """Analyzes test coverage and generates reports."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.coverage_data = {}
        self.test_results = {}
    
    def run_coverage_analysis(self) -> Dict:
        """Run complete coverage analysis."""
        print("🔍 Running Coverage Analysis...")
        
        # Run tests with coverage
        coverage_result = self._run_tests_with_coverage()
        
        # Analyze coverage data
        coverage_data = self._analyze_coverage_data()
        
        # Generate reports
        reports = self._generate_reports(coverage_data)
        
        return {
            'coverage_result': coverage_result,
            'coverage_data': coverage_data,
            'reports': reports,
            'timestamp': time.time()
        }
    
    def _run_tests_with_coverage(self) -> Dict:
        """Run tests with coverage measurement."""
        print("  📊 Running tests with coverage...")
        
        # Run different test categories
        test_categories = {
            'unit': 'tests/unit/',
            'integration': 'tests/integration/',
            'property': 'tests/property/',
            'performance': 'tests/performance/'
        }
        
        results = {}
        
        for category, path in test_categories.items():
            if os.path.exists(path):
                print(f"    Testing {category}...")
                
                cmd = [
                    sys.executable, '-m', 'pytest',
                    path,
                    '--cov=refactored_sqltools',
                    '--cov-report=json',
                    '--cov-report=term-missing',
                    '--tb=short',
                    '-q'
                ]
                
                try:
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=300  # 5 minute timeout
                    )
                    
                    results[category] = {
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'success': result.returncode == 0
                    }
                    
                except subprocess.TimeoutExpired:
                    results[category] = {
                        'returncode': -1,
                        'stdout': '',
                        'stderr': 'Test timeout',
                        'success': False
                    }
        
        return results
    
    def _analyze_coverage_data(self) -> Dict:
        """Analyze coverage data from JSON report."""
        coverage_file = self.project_root / 'coverage.json'
        
        if not coverage_file.exists():
            return {'error': 'Coverage data not found'}
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            # Extract key metrics
            totals = coverage_data.get('totals', {})
            files = coverage_data.get('files', {})
            
            analysis = {
                'overall_coverage': totals.get('percent_covered', 0),
                'lines_covered': totals.get('covered_lines', 0),
                'lines_total': totals.get('num_statements', 0),
                'missing_lines': totals.get('missing_lines', 0),
                'file_coverage': {},
                'low_coverage_files': [],
                'high_coverage_files': [],
                'uncovered_files': []
            }
            
            # Analyze per-file coverage
            for file_path, file_data in files.items():
                if 'refactored_sqltools' in file_path:
                    coverage_percent = file_data['summary']['percent_covered']
                    
                    analysis['file_coverage'][file_path] = {
                        'coverage': coverage_percent,
                        'lines_covered': file_data['summary']['covered_lines'],
                        'lines_total': file_data['summary']['num_statements'],
                        'missing_lines': file_data['summary']['missing_lines']
                    }
                    
                    # Categorize files by coverage level
                    if coverage_percent == 0:
                        analysis['uncovered_files'].append(file_path)
                    elif coverage_percent < 50:
                        analysis['low_coverage_files'].append((file_path, coverage_percent))
                    elif coverage_percent > 90:
                        analysis['high_coverage_files'].append((file_path, coverage_percent))
            
            # Sort lists
            analysis['low_coverage_files'].sort(key=lambda x: x[1])
            analysis['high_coverage_files'].sort(key=lambda x: x[1], reverse=True)
            
            return analysis
            
        except Exception as e:
            return {'error': f'Failed to analyze coverage data: {e}'}
    
    def _generate_reports(self, coverage_data: Dict) -> Dict:
        """Generate various coverage reports."""
        reports = {}
        
        # Summary report
        reports['summary'] = self._generate_summary_report(coverage_data)
        
        # Detailed report
        reports['detailed'] = self._generate_detailed_report(coverage_data)
        
        # Recommendations
        reports['recommendations'] = self._generate_recommendations(coverage_data)
        
        return reports
    
    def _generate_summary_report(self, coverage_data: Dict) -> str:
        """Generate summary coverage report."""
        if 'error' in coverage_data:
            return f"❌ Coverage Analysis Failed: {coverage_data['error']}"
        
        overall = coverage_data.get('overall_coverage', 0)
        lines_covered = coverage_data.get('lines_covered', 0)
        lines_total = coverage_data.get('lines_total', 0)
        
        # Determine status emoji
        if overall >= 90:
            status = "🟢 Excellent"
        elif overall >= 75:
            status = "🟡 Good"
        elif overall >= 50:
            status = "🟠 Fair"
        else:
            status = "🔴 Poor"
        
        report = f"""
📊 COVERAGE SUMMARY REPORT
{'='*50}

Overall Coverage: {overall:.1f}% {status}
Lines Covered: {lines_covered:,} / {lines_total:,}

Coverage Breakdown:
• High Coverage (>90%): {len(coverage_data.get('high_coverage_files', []))} files
• Low Coverage (<50%): {len(coverage_data.get('low_coverage_files', []))} files  
• Uncovered Files: {len(coverage_data.get('uncovered_files', []))} files

Status: {'✅ PASS' if overall >= 75 else '⚠️ NEEDS IMPROVEMENT' if overall >= 50 else '❌ CRITICAL'}
"""
        return report.strip()
    
    def _generate_detailed_report(self, coverage_data: Dict) -> str:
        """Generate detailed coverage report."""
        if 'error' in coverage_data:
            return f"Error: {coverage_data['error']}"
        
        report = ["📋 DETAILED COVERAGE REPORT", "="*50, ""]
        
        # Low coverage files
        low_coverage = coverage_data.get('low_coverage_files', [])
        if low_coverage:
            report.append("🔴 LOW COVERAGE FILES (<50%):")
            for file_path, coverage in low_coverage[:10]:  # Top 10
                short_path = file_path.split('refactored_sqltools/')[-1]
                report.append(f"  • {short_path}: {coverage:.1f}%")
            if len(low_coverage) > 10:
                report.append(f"  ... and {len(low_coverage) - 10} more files")
            report.append("")
        
        # Uncovered files
        uncovered = coverage_data.get('uncovered_files', [])
        if uncovered:
            report.append("⚫ UNCOVERED FILES (0%):")
            for file_path in uncovered[:5]:  # Top 5
                short_path = file_path.split('refactored_sqltools/')[-1]
                report.append(f"  • {short_path}")
            if len(uncovered) > 5:
                report.append(f"  ... and {len(uncovered) - 5} more files")
            report.append("")
        
        # High coverage files
        high_coverage = coverage_data.get('high_coverage_files', [])
        if high_coverage:
            report.append("🟢 HIGH COVERAGE FILES (>90%):")
            for file_path, coverage in high_coverage[:5]:  # Top 5
                short_path = file_path.split('refactored_sqltools/')[-1]
                report.append(f"  • {short_path}: {coverage:.1f}%")
            report.append("")
        
        return "\n".join(report)
    
    def _generate_recommendations(self, coverage_data: Dict) -> List[str]:
        """Generate recommendations for improving coverage."""
        if 'error' in coverage_data:
            return ["Fix coverage analysis errors first"]
        
        recommendations = []
        overall = coverage_data.get('overall_coverage', 0)
        
        # Overall coverage recommendations
        if overall < 50:
            recommendations.append("🚨 CRITICAL: Overall coverage is below 50%. Prioritize adding basic tests.")
        elif overall < 75:
            recommendations.append("⚠️ WARNING: Overall coverage is below 75%. Add more comprehensive tests.")
        elif overall < 90:
            recommendations.append("📈 GOOD: Coverage is good but can be improved. Focus on edge cases.")
        else:
            recommendations.append("✅ EXCELLENT: Coverage is excellent. Maintain current quality.")
        
        # Specific file recommendations
        low_coverage = coverage_data.get('low_coverage_files', [])
        uncovered = coverage_data.get('uncovered_files', [])
        
        if uncovered:
            recommendations.append(f"🎯 Add basic tests for {len(uncovered)} uncovered files")
        
        if low_coverage:
            recommendations.append(f"📊 Improve tests for {len(low_coverage)} low-coverage files")
        
        # Specific recommendations based on file types
        file_coverage = coverage_data.get('file_coverage', {})
        
        core_files = [f for f in file_coverage.keys() if '/core/' in f]
        ui_files = [f for f in file_coverage.keys() if '/ui/' in f]
        utils_files = [f for f in file_coverage.keys() if '/utils/' in f]
        
        if core_files:
            core_avg = sum(file_coverage[f]['coverage'] for f in core_files) / len(core_files)
            if core_avg < 80:
                recommendations.append("🔧 Core modules need better test coverage (business logic priority)")
        
        if ui_files:
            ui_avg = sum(file_coverage[f]['coverage'] for f in ui_files) / len(ui_files)
            if ui_avg < 60:
                recommendations.append("🖥️ UI components need more integration tests")
        
        if utils_files:
            utils_avg = sum(file_coverage[f]['coverage'] for f in utils_files) / len(utils_files)
            if utils_avg < 90:
                recommendations.append("🛠️ Utility functions should have near-complete coverage")
        
        return recommendations
    
    def generate_coverage_badge(self, coverage_percent: float) -> str:
        """Generate coverage badge markdown."""
        if coverage_percent >= 90:
            color = "brightgreen"
        elif coverage_percent >= 75:
            color = "green"
        elif coverage_percent >= 50:
            color = "yellow"
        else:
            color = "red"
        
        return f"![Coverage](https://img.shields.io/badge/coverage-{coverage_percent:.1f}%25-{color})"
    
    def save_reports(self, analysis_result: Dict) -> None:
        """Save reports to files."""
        reports_dir = self.project_root / 'coverage_reports'
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save summary report
        summary_file = reports_dir / f'coverage_summary_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write(analysis_result['reports']['summary'])
        
        # Save detailed report
        detailed_file = reports_dir / f'coverage_detailed_{timestamp}.txt'
        with open(detailed_file, 'w') as f:
            f.write(analysis_result['reports']['detailed'])
        
        # Save recommendations
        recommendations_file = reports_dir / f'coverage_recommendations_{timestamp}.txt'
        with open(recommendations_file, 'w') as f:
            f.write("COVERAGE IMPROVEMENT RECOMMENDATIONS\n")
            f.write("="*40 + "\n\n")
            for i, rec in enumerate(analysis_result['reports']['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        # Save JSON data
        json_file = reports_dir / f'coverage_data_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        print(f"📁 Reports saved to: {reports_dir}")


def main():
    """Main function to run coverage analysis."""
    print("🚀 SQL SysHub Coverage Analysis Tool")
    print("="*40)
    
    analyzer = CoverageAnalyzer()
    
    try:
        # Run analysis
        result = analyzer.run_coverage_analysis()
        
        # Print reports
        print(result['reports']['summary'])
        print("\n" + result['reports']['detailed'])
        
        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(result['reports']['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # Save reports
        analyzer.save_reports(result)
        
        # Generate badge
        coverage_data = result['coverage_data']
        if 'overall_coverage' in coverage_data:
            badge = analyzer.generate_coverage_badge(coverage_data['overall_coverage'])
            print(f"\n🏷️ Coverage Badge: {badge}")
        
        print("\n✅ Coverage analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Coverage analysis failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())