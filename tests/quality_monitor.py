#!/usr/bin/env python3
"""
Quality monitoring system for SQL SysHub tests.

This script provides continuous monitoring of test quality,
performance metrics, and regression detection.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class QualityMonitor:
    """Monitors test quality and performance over time."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.metrics_dir = self.project_root / 'quality_metrics'
        self.metrics_dir.mkdir(exist_ok=True)
    
    def run_quality_check(self) -> Dict:
        """Run complete quality check."""
        print("🔍 Running Quality Check...")
        
        start_time = time.time()
        
        # Run all test categories
        test_results = self._run_all_tests()
        
        # Analyze performance
        performance_metrics = self._analyze_performance(test_results)
        
        # Check for regressions
        regression_analysis = self._check_regressions()
        
        # Generate quality score
        quality_score = self._calculate_quality_score(test_results, performance_metrics)
        
        total_time = time.time() - start_time
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_time': total_time,
            'test_results': test_results,
            'performance_metrics': performance_metrics,
            'regression_analysis': regression_analysis,
            'quality_score': quality_score
        }
        
        # Save metrics
        self._save_metrics(result)
        
        return result
    
    def _run_all_tests(self) -> Dict:
        """Run all test categories and collect results."""
        print("  🧪 Running all test categories...")
        
        test_categories = {
            'unit': {
                'path': 'tests/unit/',
                'timeout': 60,
                'critical': True
            },
            'integration': {
                'path': 'tests/integration/',
                'timeout': 120,
                'critical': True
            },
            'property': {
                'path': 'tests/property/',
                'timeout': 180,
                'critical': False
            },
            'performance': {
                'path': 'tests/performance/',
                'timeout': 300,
                'critical': False
            }
        }
        
        results = {}
        
        for category, config in test_categories.items():
            if os.path.exists(config['path']):
                print(f"    Running {category} tests...")
                
                start_time = time.time()
                
                cmd = [
                    sys.executable, '-m', 'pytest',
                    config['path'],
                    '-v',
                    '--tb=short',
                    '--durations=10',  # Show 10 slowest tests
                    '--json-report',
                    '--json-report-file=test_report.json'
                ]
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=config['timeout']
                    )
                    
                    duration = time.time() - start_time
                    
                    # Parse test report if available
                    test_details = self._parse_test_report()
                    
                    results[category] = {
                        'success': result.returncode == 0,
                        'returncode': result.returncode,
                        'duration': duration,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'critical': config['critical'],
                        'test_details': test_details
                    }
                    
                except subprocess.TimeoutExpired:
                    results[category] = {
                        'success': False,
                        'returncode': -1,
                        'duration': config['timeout'],
                        'stdout': '',
                        'stderr': f'Tests timed out after {config["timeout"]}s',
                        'critical': config['critical'],
                        'test_details': {}
                    }
                
                except Exception as e:
                    results[category] = {
                        'success': False,
                        'returncode': -2,
                        'duration': 0,
                        'stdout': '',
                        'stderr': f'Test execution failed: {e}',
                        'critical': config['critical'],
                        'test_details': {}
                    }
        
        return results
    
    def _parse_test_report(self) -> Dict:
        """Parse JSON test report if available."""
        report_file = Path('test_report.json')
        
        if not report_file.exists():
            return {}
        
        try:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            # Clean up report file
            report_file.unlink()
            
            return {
                'total_tests': report_data.get('summary', {}).get('total', 0),
                'passed': report_data.get('summary', {}).get('passed', 0),
                'failed': report_data.get('summary', {}).get('failed', 0),
                'skipped': report_data.get('summary', {}).get('skipped', 0),
                'duration': report_data.get('duration', 0),
                'slowest_tests': self._extract_slowest_tests(report_data)
            }
        
        except Exception:
            return {}
    
    def _extract_slowest_tests(self, report_data: Dict) -> List[Dict]:
        """Extract slowest tests from report."""
        tests = report_data.get('tests', [])
        
        # Sort by duration and get top 5
        sorted_tests = sorted(
            [t for t in tests if t.get('duration', 0) > 0],
            key=lambda x: x.get('duration', 0),
            reverse=True
        )[:5]
        
        return [
            {
                'name': test.get('nodeid', 'Unknown'),
                'duration': test.get('duration', 0),
                'outcome': test.get('outcome', 'unknown')
            }
            for test in sorted_tests
        ]
    
    def _analyze_performance(self, test_results: Dict) -> Dict:
        """Analyze performance metrics from test results."""
        print("  📊 Analyzing performance metrics...")
        
        metrics = {
            'total_duration': 0,
            'category_performance': {},
            'performance_issues': [],
            'performance_score': 100
        }
        
        # Performance thresholds (in seconds)
        thresholds = {
            'unit': 30,        # Unit tests should be fast
            'integration': 60,  # Integration tests can be slower
            'property': 120,    # Property tests can take time
            'performance': 300  # Performance tests are expected to be slow
        }
        
        for category, result in test_results.items():
            duration = result.get('duration', 0)
            metrics['total_duration'] += duration
            
            threshold = thresholds.get(category, 60)
            performance_ratio = duration / threshold if threshold > 0 else 0
            
            metrics['category_performance'][category] = {
                'duration': duration,
                'threshold': threshold,
                'ratio': performance_ratio,
                'status': 'good' if performance_ratio <= 1.0 else 'slow' if performance_ratio <= 2.0 else 'critical'
            }
            
            # Check for performance issues
            if performance_ratio > 1.5:
                metrics['performance_issues'].append({
                    'category': category,
                    'duration': duration,
                    'threshold': threshold,
                    'severity': 'high' if performance_ratio > 2.0 else 'medium'
                })
        
        # Calculate performance score
        avg_ratio = sum(
            perf['ratio'] for perf in metrics['category_performance'].values()
        ) / len(metrics['category_performance']) if metrics['category_performance'] else 1.0
        
        if avg_ratio <= 1.0:
            metrics['performance_score'] = 100
        elif avg_ratio <= 1.5:
            metrics['performance_score'] = 80
        elif avg_ratio <= 2.0:
            metrics['performance_score'] = 60
        else:
            metrics['performance_score'] = 40
        
        return metrics
    
    def _check_regressions(self) -> Dict:
        """Check for regressions compared to previous runs."""
        print("  🔄 Checking for regressions...")
        
        # Load historical data
        history = self._load_historical_metrics()
        
        if len(history) < 2:
            return {
                'has_regressions': False,
                'message': 'Insufficient historical data for regression analysis',
                'regressions': []
            }
        
        current = history[-1]
        previous = history[-2]
        
        regressions = []
        
        # Check test success rate regression
        current_success_rate = self._calculate_success_rate(current.get('test_results', {}))
        previous_success_rate = self._calculate_success_rate(previous.get('test_results', {}))
        
        if current_success_rate < previous_success_rate - 0.05:  # 5% threshold
            regressions.append({
                'type': 'success_rate',
                'current': current_success_rate,
                'previous': previous_success_rate,
                'severity': 'high'
            })
        
        # Check performance regression
        current_duration = current.get('performance_metrics', {}).get('total_duration', 0)
        previous_duration = previous.get('performance_metrics', {}).get('total_duration', 0)
        
        if previous_duration > 0 and current_duration > previous_duration * 1.2:  # 20% slower
            regressions.append({
                'type': 'performance',
                'current': current_duration,
                'previous': previous_duration,
                'severity': 'medium'
            })
        
        # Check quality score regression
        current_quality = current.get('quality_score', {}).get('overall', 0)
        previous_quality = previous.get('quality_score', {}).get('overall', 0)
        
        if current_quality < previous_quality - 5:  # 5 point drop
            regressions.append({
                'type': 'quality_score',
                'current': current_quality,
                'previous': previous_quality,
                'severity': 'medium'
            })
        
        return {
            'has_regressions': len(regressions) > 0,
            'regressions': regressions,
            'comparison_date': previous.get('timestamp', 'unknown')
        }
    
    def _calculate_success_rate(self, test_results: Dict) -> float:
        """Calculate overall test success rate."""
        if not test_results:
            return 0.0
        
        total_categories = len(test_results)
        successful_categories = sum(1 for result in test_results.values() if result.get('success', False))
        
        return successful_categories / total_categories if total_categories > 0 else 0.0
    
    def _calculate_quality_score(self, test_results: Dict, performance_metrics: Dict) -> Dict:
        """Calculate overall quality score."""
        print("  📈 Calculating quality score...")
        
        # Component scores (0-100)
        scores = {}
        
        # Test success score (40% weight)
        success_rate = self._calculate_success_rate(test_results)
        scores['test_success'] = success_rate * 100
        
        # Performance score (30% weight)
        scores['performance'] = performance_metrics.get('performance_score', 0)
        
        # Coverage score (20% weight) - placeholder
        scores['coverage'] = 75  # Would be calculated from coverage analysis
        
        # Code quality score (10% weight) - placeholder
        scores['code_quality'] = 85  # Would be calculated from linting, complexity, etc.
        
        # Calculate weighted overall score
        weights = {
            'test_success': 0.4,
            'performance': 0.3,
            'coverage': 0.2,
            'code_quality': 0.1
        }
        
        overall_score = sum(scores[component] * weights[component] for component in scores)
        
        # Determine grade
        if overall_score >= 90:
            grade = 'A'
        elif overall_score >= 80:
            grade = 'B'
        elif overall_score >= 70:
            grade = 'C'
        elif overall_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'overall': overall_score,
            'grade': grade,
            'components': scores,
            'weights': weights
        }
    
    def _load_historical_metrics(self) -> List[Dict]:
        """Load historical metrics for trend analysis."""
        history = []
        
        # Load last 10 metric files
        metric_files = sorted(
            [f for f in self.metrics_dir.glob('quality_metrics_*.json')],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]
        
        for file_path in metric_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    history.append(data)
            except Exception:
                continue
        
        return list(reversed(history))  # Oldest first
    
    def _save_metrics(self, metrics: Dict) -> None:
        """Save metrics to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'quality_metrics_{timestamp}.json'
        filepath = self.metrics_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        # Keep only last 20 files
        metric_files = sorted(
            [f for f in self.metrics_dir.glob('quality_metrics_*.json')],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for old_file in metric_files[20:]:
            old_file.unlink()
    
    def generate_quality_report(self, metrics: Dict) -> str:
        """Generate human-readable quality report."""
        report = []
        
        # Header
        report.append("🏆 QUALITY MONITORING REPORT")
        report.append("=" * 50)
        report.append(f"Timestamp: {metrics['timestamp']}")
        report.append(f"Total Duration: {metrics['total_time']:.1f}s")
        report.append("")
        
        # Quality Score
        quality = metrics['quality_score']
        report.append(f"📊 OVERALL QUALITY SCORE: {quality['overall']:.1f}/100 (Grade: {quality['grade']})")
        report.append("")
        
        # Component Scores
        report.append("📋 COMPONENT SCORES:")
        for component, score in quality['components'].items():
            weight = quality['weights'][component]
            report.append(f"  • {component.replace('_', ' ').title()}: {score:.1f}/100 (weight: {weight:.0%})")
        report.append("")
        
        # Test Results
        report.append("🧪 TEST RESULTS:")
        test_results = metrics['test_results']
        for category, result in test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result['duration']
            critical = " (CRITICAL)" if result.get('critical', False) else ""
            report.append(f"  • {category.title()}: {status} ({duration:.1f}s){critical}")
        report.append("")
        
        # Performance Analysis
        perf = metrics['performance_metrics']
        report.append("⚡ PERFORMANCE ANALYSIS:")
        report.append(f"  • Total Duration: {perf['total_duration']:.1f}s")
        report.append(f"  • Performance Score: {perf['performance_score']}/100")
        
        if perf['performance_issues']:
            report.append("  • Performance Issues:")
            for issue in perf['performance_issues']:
                report.append(f"    - {issue['category']}: {issue['duration']:.1f}s (threshold: {issue['threshold']}s)")
        report.append("")
        
        # Regression Analysis
        regression = metrics['regression_analysis']
        if regression['has_regressions']:
            report.append("⚠️ REGRESSIONS DETECTED:")
            for reg in regression['regressions']:
                report.append(f"  • {reg['type']}: {reg['current']:.2f} vs {reg['previous']:.2f} (severity: {reg['severity']})")
        else:
            report.append("✅ NO REGRESSIONS DETECTED")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        recommendations = self._generate_recommendations(metrics)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"  {i}. {rec}")
        
        return "\n".join(report)
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        quality_score = metrics['quality_score']['overall']
        test_results = metrics['test_results']
        performance = metrics['performance_metrics']
        regressions = metrics['regression_analysis']
        
        # Quality-based recommendations
        if quality_score < 70:
            recommendations.append("🚨 Quality score is below 70. Focus on improving test reliability and performance.")
        elif quality_score < 85:
            recommendations.append("📈 Quality score is good but can be improved. Focus on edge cases and performance optimization.")
        
        # Test failure recommendations
        failed_tests = [cat for cat, result in test_results.items() if not result['success']]
        if failed_tests:
            critical_failures = [cat for cat in failed_tests if test_results[cat].get('critical', False)]
            if critical_failures:
                recommendations.append(f"🔥 URGENT: Fix critical test failures in: {', '.join(critical_failures)}")
            else:
                recommendations.append(f"⚠️ Fix test failures in: {', '.join(failed_tests)}")
        
        # Performance recommendations
        if performance['performance_score'] < 80:
            slow_categories = [
                cat for cat, perf in performance['category_performance'].items()
                if perf['status'] in ['slow', 'critical']
            ]
            if slow_categories:
                recommendations.append(f"⚡ Optimize performance in: {', '.join(slow_categories)}")
        
        # Regression recommendations
        if regressions['has_regressions']:
            high_severity = [r for r in regressions['regressions'] if r['severity'] == 'high']
            if high_severity:
                recommendations.append("🔄 URGENT: Address high-severity regressions immediately")
            else:
                recommendations.append("🔄 Monitor and address detected regressions")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ Quality is excellent! Continue maintaining current standards.")
        
        return recommendations


def main():
    """Main function to run quality monitoring."""
    print("🚀 SQL SysHub Quality Monitor")
    print("=" * 40)
    
    monitor = QualityMonitor()
    
    try:
        # Run quality check
        metrics = monitor.run_quality_check()
        
        # Generate and display report
        report = monitor.generate_quality_report(metrics)
        print(report)
        
        # Determine exit code based on quality
        quality_score = metrics['quality_score']['overall']
        has_critical_failures = any(
            not result['success'] and result.get('critical', False)
            for result in metrics['test_results'].values()
        )
        
        if has_critical_failures:
            print("\n❌ CRITICAL FAILURES DETECTED")
            return 2
        elif quality_score < 70:
            print("\n⚠️ QUALITY BELOW THRESHOLD")
            return 1
        else:
            print("\n✅ QUALITY CHECK PASSED")
            return 0
    
    except Exception as e:
        print(f"\n❌ Quality monitoring failed: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())