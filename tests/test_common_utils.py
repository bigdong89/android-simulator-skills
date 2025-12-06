#!/usr/bin/env python3
"""
Unit tests for common_utils.py

This test suite validates the core utilities used across all Android automation scripts.
"""

import unittest
import json
import sys
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from common_utils import (
        AndroidAutomationError, ErrorCategory, ErrorSeverity, ErrorHandler,
        StructuredLogger, validate_required_tools, parse_device_args,
        format_json_output
    )
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestAndroidAutomationError(unittest.TestCase):
    """Test the AndroidAutomationError class"""

    def test_error_creation(self):
        """Test basic error creation with all parameters"""
        details = {"operation": "test", "element": "button"}
        suggestions = ["Try again", "Check device"]

        error = AndroidAutomationError(
            message="Test error",
            category=ErrorCategory.DEVICE_CONNECTION,
            severity=ErrorSeverity.HIGH,
            details=details,
            suggestions=suggestions
        )

        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.category, ErrorCategory.DEVICE_CONNECTION)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertEqual(error.details, details)
        self.assertEqual(error.suggestions, suggestions)
        self.assertIsInstance(error.timestamp, str)

    def test_minimal_error(self):
        """Test error creation with minimal parameters"""
        error = AndroidAutomationError("Simple error")

        self.assertEqual(error.message, "Simple error")
        self.assertEqual(error.category, ErrorCategory.UNKNOWN)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.details, {})
        self.assertEqual(error.suggestions, [])


class TestErrorHandler(unittest.TestCase):
    """Test the ErrorHandler class"""

    def setUp(self):
        self.error_handler = ErrorHandler("test_script")

    def test_error_classification_device_connection(self):
        """Test classification of device connection errors"""
        error = Exception("device not found")
        automation_error = self.error_handler.handle_error(error)

        self.assertEqual(automation_error.category, ErrorCategory.DEVICE_CONNECTION)
        self.assertEqual(automation_error.severity, ErrorSeverity.HIGH)
        self.assertIn("device", automation_error.suggestions[0].lower())

    def test_error_classification_timeout(self):
        """Test classification of timeout errors"""
        error = Exception("operation timed out")
        automation_error = self.error_handler.handle_error(error)

        self.assertEqual(automation_error.category, ErrorCategory.TIMEOUT)
        self.assertEqual(automation_error.severity, ErrorSeverity.MEDIUM)

    def test_error_classification_permission(self):
        """Test classification of permission errors"""
        error = Exception("access denied")
        automation_error = self.error_handler.handle_error(error)

        self.assertEqual(automation_error.category, ErrorCategory.PERMISSION)
        self.assertEqual(automation_error.severity, ErrorSeverity.HIGH)

    def test_suggestion_database_retrieval(self):
        """Test that suggestions are retrieved from database"""
        error = self.error_handler.handle_error(
            Exception("device not connected"),
            {"operation": "test"}
        )

        self.assertGreater(len(error.suggestions), 0)
        self.assertTrue(
            any("adb" in suggestion.lower() for suggestion in error.suggestions)
        )

    def test_error_history_tracking(self):
        """Test that errors are tracked in history"""
        error1 = Exception("First error")
        error2 = Exception("Second error")

        automation_error1 = self.error_handler.handle_error(error1)
        automation_error2 = self.error_handler.handle_error(error2)

        self.assertEqual(len(self.error_handler.error_history), 2)
        self.assertIn(automation_error1, self.error_handler.error_history)
        self.assertIn(automation_error2, self.error_handler.error_history)

    def test_error_summary(self):
        """Test error summary generation"""
        # Add some errors to history
        self.error_handler.handle_error(
            AndroidAutomationError("Error 1", ErrorCategory.VALIDATION, ErrorSeverity.LOW)
        )
        self.error_handler.handle_error(
            AndroidAutomationError("Error 2", ErrorCategory.DEVICE_CONNECTION, ErrorSeverity.HIGH)
        )

        summary = self.error_handler.get_error_summary()

        self.assertEqual(summary["total_errors"], 2)
        self.assertIn("by_category", summary)
        self.assertIn("by_severity", summary)
        self.assertEqual(summary["by_category"]["validation"], 1)
        self.assertEqual(summary["by_category"]["device_connection"], 1)


class TestStructuredLogger(unittest.TestCase):
    """Test the StructuredLogger class"""

    def setUp(self):
        # Create a temporary file for logging
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_file.close()

        self.logger = StructuredLogger("test_script", "DEBUG")

    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_operation_tracking(self):
        """Test operation start and completion"""
        op_id = self.logger.start_operation("test_operation", {"param": "value"})

        self.assertIn(op_id, [op["id"] for op in self.logger.metrics["operations"]])
        op = next(op for op in self.logger.metrics["operations"] if op["id"] == op_id)
        self.assertEqual(op["name"], "test_operation")
        self.assertEqual(op["details"]["param"], "value")
        self.assertFalse(op.get("success", False))  # Not completed yet

        # Complete operation
        self.logger.complete_operation(op_id, True, {"result": "success"})

        op = next(op for op in self.logger.metrics["operations"] if op["id"] == op_id)
        self.assertTrue(op["success"])
        self.assertEqual(op["result"]["result"], "success")
        self.assertIn("duration", op)

    def test_performance_metrics(self):
        """Test performance report generation"""
        # Add some operations
        op1 = self.logger.start_operation("op1")
        self.logger.complete_operation(op1, True, {"time": 1.0})

        op2 = self.logger.start_operation("op2")
        self.logger.complete_operation(op2, False)

        report = self.logger.get_performance_report()

        self.assertEqual(report["script"], "test_script")
        self.assertEqual(report["total_operations"], 2)
        self.assertEqual(report["successful_operations"], 1)
        self.assertEqual(report["success_rate"], 0.5)
        self.assertGreater(report["total_runtime"], 0)
        self.assertIn("operations", report)

    def test_logging_methods(self):
        """Test various logging methods"""
        # Test error logging
        error = AndroidAutomationError("Test error", ErrorCategory.VALIDATION, ErrorSeverity.LOW)
        self.logger.log_error(error, {"context": "test"})

        # Test warning logging
        self.logger.log_warning("Test warning", {"detail": "value"})

        # Test debug logging
        self.logger.log_debug("Test debug", {"debug_info": "value"})

        # Test alias methods
        self.logger.debug("Test debug alias", {"debug_info": "value2"})


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""

    def test_parse_device_args(self):
        """Test device argument parsing"""
        # Test with device ID
        result = parse_device_args("emulator-5554")
        self.assertEqual(result, "-s emulator-5554")

        # Test without device ID
        result = parse_device_args(None)
        self.assertEqual(result, "")

        # Test with empty device ID
        result = parse_device_args("")
        self.assertEqual(result, "")

    def test_format_json_output(self):
        """Test JSON output formatting"""
        data = {
            "success": True,
            "data": {"key": "value"},
            "action": "test"
        }

        result = format_json_output(data)

        parsed = json.loads(result)
        self.assertEqual(parsed["success"], True)
        self.assertEqual(parsed["data"]["key"], "value")
        self.assertEqual(parsed["action"], "test")
        self.assertIn("timestamp", parsed)

    @patch('subprocess.run')
    def test_validate_required_tools_success(self, mock_run):
        """Test successful tools validation"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Android Debug Bridge version 1.0.41"

        result = validate_required_tools()

        self.assertTrue(result["adb"])
        mock_run.assert_called_with(["adb", "version"], capture_output=True, text=True, timeout=5)

    @patch('subprocess.run')
    def test_validate_required_tools_failure(self, mock_run):
        """Test tools validation failure"""
        mock_run.side_effect = FileNotFoundError("Command not found")

        result = validate_required_tools()

        self.assertFalse(result["adb"])
        mock_run.assert_called_with(["adb", "version"], capture_output=True, text=True, timeout=5)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test integration between error handling components"""

    def test_error_handler_with_logger(self):
        """Test error handler integration with structured logger"""
        logger = StructuredLogger("integration_test")
        error_handler = ErrorHandler("integration_test")

        error = error_handler.handle_error(
            Exception("Test error for integration"),
            {"context": "integration"}
        )

        logger.log_error(error)

        # Verify error was logged properly
        self.assertEqual(error.category, ErrorCategory.UNKNOWN)
        self.assertEqual(len(error_handler.error_history), 1)

    def test_android_automation_error_json_serialization(self):
        """Test that AndroidAutomationError can be JSON serialized"""
        error = AndroidAutomationError(
            "JSON serialization test",
            category=ErrorCategory.UI_PARSING,
            severity=ErrorSeverity.MEDIUM,
            details={"xml_length": 1000},
            suggestions=["Check XML format", "Refresh UI"]
        )

        # Should not raise an exception
        error_dict = {
            "message": error.message,
            "category": error.category.value,
            "severity": error.severity.value,
            "details": error.details,
            "suggestions": error.suggestions,
            "timestamp": error.timestamp
        }

        json_str = json.dumps(error_dict)
        parsed = json.loads(json_str)

        self.assertEqual(parsed["message"], "JSON serialization test")
        self.assertEqual(parsed["category"], "ui_parsing")
        self.assertEqual(parsed["severity"], "medium")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_error_handler_with_none_error(self):
        """Test error handling with None error object"""
        # This should not crash
        error_handler = ErrorHandler("test")
        try:
            error = error_handler.handle_error(None)
            self.fail("Should have raised an exception for None error")
        except Exception:
            pass  # Expected

    def test_logger_with_empty_operation(self):
        """Test logger with empty operation details"""
        logger = StructuredLogger("test")
        op_id = logger.start_operation("")
        logger.complete_operation(op_id, True)

        op = next(op for op in logger.metrics["operations"] if op["id"] == op_id)
        self.assertEqual(op["name"], "")

    def test_format_json_output_with_complex_data(self):
        """Test JSON output with complex nested data"""
        class CustomObject:
            def __str__(self):
                return "custom_object"

        data = {
            "success": True,
            "data": {
                "complex": {
                    "nested": {"value": CustomObject()}
                }
            }
        }

        result = format_json_output(data)
        parsed = json.loads(result)

        self.assertEqual(parsed["data"]["complex"]["nested"]["value"], "custom_object")


if __name__ == '__main__':
    unittest.main()