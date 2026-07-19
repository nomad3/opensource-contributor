"""Regression-oracle tests for the Bilby #1114 standalone reproducer."""

import unittest

from reproduce import (
    LAMBDA_1,
    LAMBDA_2,
    MASS_1,
    MASS_2,
    components_to_derived,
    derived_to_components,
    reproduce,
)


class Bilby1114ReproducerTest(unittest.TestCase):
    def test_reported_derived_values(self) -> None:
        lambda_tilde, delta_lambda_tilde = components_to_derived(
            LAMBDA_1,
            LAMBDA_2,
            MASS_1,
            MASS_2,
        )
        self.assertAlmostEqual(lambda_tilde, 11.340939966673643)
        self.assertAlmostEqual(delta_lambda_tilde, 5.98106544849901)

    def test_zero_component_round_trips_negative(self) -> None:
        result = reproduce()
        self.assertEqual(result["input_lambda_1"], 0.0)
        self.assertAlmostEqual(
            result["roundtrip_lambda_1"],
            -2.45587692656649e-14,
            delta=1e-27,
        )
        self.assertLess(result["roundtrip_lambda_1"], 0.0)

    def test_second_component_only_changes_by_roundoff(self) -> None:
        lambda_tilde, delta_lambda_tilde = components_to_derived(
            LAMBDA_1,
            LAMBDA_2,
            MASS_1,
            MASS_2,
        )
        _, roundtrip_lambda_2 = derived_to_components(
            lambda_tilde,
            delta_lambda_tilde,
            MASS_1,
            MASS_2,
        )
        self.assertAlmostEqual(roundtrip_lambda_2, LAMBDA_2, places=11)


if __name__ == "__main__":
    unittest.main()
