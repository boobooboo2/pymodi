#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `modi` package."""

# must
import modi
import unittest
import time

from modi.module.speaker import Speaker


class TestSpeaker(unittest.TestCase):
    modi_inst = None
    speaker = None

    def setUp(self):
        """Set up test fixtures, if any."""
        self.modi_inst = modi.MODI()
        self.speaker = self.modi_inst.speakers[0]

    def tearDown(self):
        """Tear down test fixtures, if any."""
        self.modi_inst.exit()
        self.speaker.tune(0, 0)
        time.sleep(1)

    def test_init(self):
        """Test initialization of speaker module"""
        self.assertIsInstance(self.speaker, Speaker)

    def test_basic_tune(self):
        """Test tune method with pre-defined inputs"""
        expected_values = (self.speaker.Scale.F_RA_6.value, 50)
        self.speaker.tune(*expected_values)
        # TODO: remove delaying function
        time.sleep(3)
        actual_values = self.speaker.tune()
        self.assertEqual(expected_values, actual_values)

    def test_custom_tune(self):
        """Test tune method with custom inputs"""
        expected_values = (2350, 50)
        self.speaker.tune(*expected_values)
        time.sleep(3)
        actual_values = self.speaker.tune()
        self.assertEqual(expected_values, actual_values)

    # def test_get_volume(self):
    #    """Test something."""

    # def test_get_frequency(self):
    #    """Test something."""


if __name__ == "__main__":
    unittest.main()
