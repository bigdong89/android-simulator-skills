#!/usr/bin/env python3
"""
Common utilities for Android Simulator Skills scripts

This module provides shared functionality for error handling, logging,
and other common operations across all Android automation scripts.
"""

import sys
import json
import traceback
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    DEVICE_CONNECTION = "device_connection"
    UI_PARSING = "ui_parsing"
    ELEMENT_NOT_FOUND = "element_not_found"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    VALIDATION = "validation"
    EXECUTION = "execution"
    UNKNOWN = "unknown"


class AndroidAutomationError(Exception):
    """Custom exception for Android automation errors"""

    def __init__(self,
                 message: str,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.suggestions = suggestions or []
        self.timestamp = datetime.now().isoformat()


class ErrorHandler:
    """Centralized error handling and user guidance"""

    def __init__(self, script_name: str):
        self.script_name = script_name
        self.error_history: List[AndroidAutomationError] = []

        # Common error suggestions
        self.suggestion_database = {
            ErrorCategory.DEVICE_CONNECTION: [
                "Check if Android emulator is running: adb devices",
                "Restart ADB server: adb kill-server && adb start-server",
                "Ensure emulator is fully booted before running script",
                "Try specifying device ID with --device parameter"
            ],
            ErrorCategory.UI_PARSING: [
                "Check if device screen is on and unlocked",
                "Try running script again after screen refresh",
                "Ensure current screen has valid UI content",
                "Check if device is responsive to touch/input"
            ],
            ErrorCategory.ELEMENT_NOT_FOUND: [
                "Verify element text/content-description matches visible UI",
                "Try waiting for UI to load before running script",
                "Use more general search terms (partial matching)",
                "Check if element exists on current screen"
            ],
            ErrorCategory.TIMEOUT: [
                "Increase timeout value with --timeout parameter",
                "Check device performance and responsiveness",
                "Ensure stable network connection",
                "Try running script with fewer concurrent operations"
            ],
            ErrorCategory.PERMISSION: [
                "Check ADB permissions: adb devices",
                "Ensure script has necessary file permissions",
                "Run script with appropriate user privileges",
                "Check firewall/antivirus blocking ADB connections"
            ],
            ErrorCategory.VALIDATION: [
                "Check command-line arguments format",
                "Verify input parameter values are valid",
                "Consult script help: --help",
                "Check parameter constraints and requirements"
            ]
        }

    def handle_error(self,
                     error: Exception,
                     context: Optional[Dict[str, Any]] = None) -> AndroidAutomationError:
        """Process and categorize error with user-friendly guidance"""

        # Determine error category and severity
        category, severity = self._classify_error(error)

        # Create structured error
        if isinstance(error, AndroidAutomationError):
            automation_error = error
        else:
            automation_error = AndroidAutomationError(
                message=str(error),
                category=category,
                severity=severity,
                details={
                    "original_exception": error.__class__.__name__,
                    "context": context or {},
                    "traceback": traceback.format_exc() if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
                }
            )

        # Add suggestions if not provided
        if not automation_error.suggestions:
            automation_error.suggestions = self.suggestion_database.get(category, [])

        # Store error for analysis
        self.error_history.append(automation_error)

        return automation_error

    def _classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error into category and severity"""
        error_message = str(error).lower()
        error_type = error.__class__.__name__

        # Device connection errors
        if any(keyword in error_message for keyword in ['device', 'adb', 'connection', 'offline']):
            return ErrorCategory.DEVICE_CONNECTION, ErrorSeverity.HIGH

        # Timeout errors
        if any(keyword in error_message for keyword in ['timeout', 'timed out']):
            return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM

        # Permission errors
        if any(keyword in error_message for keyword in ['permission', 'access denied', 'unauthorized']):
            return ErrorCategory.PERMISSION, ErrorSeverity.HIGH

        # Element not found errors
        if any(keyword in error_message for keyword in ['not found', 'element', 'xpath', 'selector']):
            return ErrorCategory.ELEMENT_NOT_FOUND, ErrorSeverity.MEDIUM

        # Parsing errors
        if any(keyword in error_message for keyword in ['parse', 'xml', 'json', 'format']):
            return ErrorCategory.UI_PARSING, ErrorSeverity.MEDIUM

        # Validation errors
        if any(keyword in error_message for keyword in ['argument', 'parameter', 'invalid']):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW

        # Default classification
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM

    def format_error_output(self, error: AndroidAutomationError, json_output: bool = False) -> str:
        """Format error for user display"""
        if json_output:
            return json.dumps({
                "success": False,
                "error": {
                    "message": error.message,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "details": error.details,
                    "suggestions": error.suggestions,
                    "timestamp": error.timestamp
                }
            }, indent=2)
        else:
            output = []
            output.append(f"❌ Error in {self.script_name}: {error.message}")
            output.append(f"🔍 Category: {error.category.value} | Severity: {error.severity.value}")

            if error.details:
                output.append("📋 Details:")
                for key, value in error.details.items():
                    if key != "traceback":  # Skip traceback for user output
                        output.append(f"  • {key}: {value}")

            if error.suggestions:
                output.append("💡 Suggestions:")
                for i, suggestion in enumerate(error.suggestions, 1):
                    output.append(f"  {i}. {suggestion}")

            return "\n".join(output)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors in current session"""
        if not self.error_history:
            return {"total_errors": 0, "message": "No errors encountered"}

        # Count by category
        category_counts = {}
        severity_counts = {}

        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1

        return {
            "total_errors": len(self.error_history),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "recent_errors": [
                {
                    "message": error.message,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "timestamp": error.timestamp
                }
                for error in self.error_history[-5:]  # Last 5 errors
            ]
        }


class StructuredLogger:
    """Structured logging with performance tracking and debugging support"""

    def __init__(self, script_name: str, level: str = "INFO"):
        self.script_name = script_name
        self.logger = logging.getLogger(script_name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Performance metrics
        self.metrics = {
            "start_time": datetime.now(),
            "operations": [],
            "memory_usage": [],
            "execution_times": []
        }

        # Setup console handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                f'[{script_name}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def start_operation(self, operation_name: str, details: Optional[Dict[str, Any]] = None):
        """Log operation start with performance tracking"""
        start_time = datetime.now()
        operation_id = f"{operation_name}_{int(start_time.timestamp())}"

        self.logger.info(f"▶️ Starting: {operation_name}")
        if details:
            for key, value in details.items():
                self.logger.debug(f"  • {key}: {value}")

        self.metrics["operations"].append({
            "id": operation_id,
            "name": operation_name,
            "start_time": start_time,
            "details": details or {}
        })

        return operation_id

    def complete_operation(self, operation_id: str, success: bool, result: Optional[Dict[str, Any]] = None):
        """Complete operation with performance metrics"""
        completion_time = datetime.now()

        # Find and update operation
        for op in self.metrics["operations"]:
            if op["id"] == operation_id:
                op["end_time"] = completion_time
                op["success"] = success
                op["result"] = result

                duration = (completion_time - op["start_time"]).total_seconds()
                op["duration"] = duration

                status = "✅" if success else "❌"
                self.logger.info(f"{status} Completed: {op['name']} ({duration:.2f}s)")

                if result:
                    self.logger.debug(f"  Result: {result}")

                self.metrics["execution_times"].append(duration)
                break

    def log_error(self, error: AndroidAutomationError, context: Optional[Dict[str, Any]] = None):
        """Log structured error information"""
        self.logger.error(f"❌ {error.category.value.upper()}: {error.message}")

        if context:
            self.logger.debug(f"Context: {context}")

        if error.suggestions:
            self.logger.info("💡 Suggestions available")

    def log_warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log warning with optional details"""
        self.logger.warning(f"⚠️ {message}")
        if details:
            for key, value in details.items():
                self.logger.debug(f"  • {key}: {value}")

    def log_debug(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log debug information"""
        self.logger.debug(f"🔍 {message}")
        if details:
            for key, value in details.items():
                self.logger.debug(f"  • {key}: {value}")

    def debug(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Alias for log_debug for backward compatibility"""
        self.log_debug(message, details)

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance summary report"""
        total_time = (datetime.now() - self.metrics["start_time"]).total_seconds()
        successful_ops = [op for op in self.metrics["operations"] if op.get("success")]

        return {
            "script": self.script_name,
            "total_runtime": total_time,
            "total_operations": len(self.metrics["operations"]),
            "successful_operations": len(successful_ops),
            "success_rate": len(successful_ops) / len(self.metrics["operations"]) if self.metrics["operations"] else 0,
            "average_execution_time": sum(self.metrics["execution_times"]) / len(self.metrics["execution_times"]) if self.metrics["execution_times"] else 0,
            "operations": [
                {
                    "name": op["name"],
                    "duration": op.get("duration", 0),
                    "success": op.get("success", False)
                }
                for op in self.metrics["operations"]
            ]
        }


def validate_required_tools() -> Dict[str, bool]:
    """Validate that required tools are available"""
    tools_status = {}

    try:
        import subprocess
        # Check ADB availability
        result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
        tools_status["adb"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        tools_status["adb"] = False

    return tools_status


def format_json_output(data: Dict[str, Any], success: bool = True) -> str:
    """Format standardized JSON output for all scripts"""
    output = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        **data
    }
    return json.dumps(output, indent=2, default=str)


def parse_device_args(device_id: Optional[str]) -> str:
    """Parse device arguments into ADB device prefix"""
    return f"-s {device_id}" if device_id else ""


# Convenience functions for backward compatibility
def create_error_handler(script_name: str) -> ErrorHandler:
    """Create error handler instance"""
    return ErrorHandler(script_name)


def create_logger(script_name: str, level: str = "INFO") -> StructuredLogger:
    """Create structured logger instance"""
    return StructuredLogger(script_name, level)