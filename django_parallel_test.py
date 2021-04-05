"""
Custom Django test runner
"""
from __future__ import annotations

import logging
import os

from django.conf import settings
from django.test.runner import DiscoverRunner

logger = logging.getLogger(__name__)


__all__ = ["ParallelRunner"]


class ParallelRunner(DiscoverRunner):
    """
    Django test runner that runs the test suite in parallel on different machines

    It divides the entire test suite into different subsets and runs one particular
    subset on each of the dynos. It uses the variables `CI_NODE_TOTAL, CI_NODE_INDEX` in
    django settings or environment variables to select which subset to run on which
    machine.
    """

    @property
    def ci_node_total(self) -> int:
        """
        Return total number of dynos that will run the tests.
        """
        if hasattr(settings, "CI_NODE_TOTAL"):
            return int(settings.CI_NODE_TOTAL)

        return int(os.environ.get("CI_NODE_TOTAL", 1))

    @property
    def ci_node_index(self) -> int:
        """
        Return index number of the current machine out of total machines available.
        """
        if hasattr(settings, "CI_NODE_INDEX"):
            return int(settings.CI_NODE_INDEX)

        return int(os.environ.get("CI_NODE_INDEX", 0))

    def split_suite(self, suite):
        """
        Return a subset of the test classes in the suite to be run on the current node.
        """

        def get_class_name(test_method):
            return str(test_method.__class__)

        # Get a list of all test classes we found in the suite.
        classes = sorted({get_class_name(test_method) for test_method in suite})
        # Only select a subset of the test classes to be run on the node.
        classes_subset = [
            test_class
            for idx, test_class in enumerate(classes)
            if idx % self.ci_node_total == self.ci_node_index
        ]

        # Create a new test suite with only test methods from the subset of classes.
        suite_class = type(suite)
        new_suite = suite_class()
        count = 0
        for test_method in suite:
            if get_class_name(test_method) in classes_subset:
                count += 1
                new_suite.addTest(test_method)
        logger.info(
            f"{count} tests will be run on this node from the following classes:"
            f"\n{classes_subset}"
        )
        return new_suite

    def run_suite(self, suite, **kwargs):
        """
        Run the entire test suite.
        """
        if self.parallel > 1:
            logger.warning(
                "--parallel is not supported by this runner. "
                "Please use `quantity` key in app.json to increase number of "
                "nodes instead, if using Heroku"
            )
            raise ValueError("Unsupported parameter passed `--parallel`.")

        suite_with_subset = self.split_suite(suite)
        return super().run_suite(suite_with_subset, **kwargs)
