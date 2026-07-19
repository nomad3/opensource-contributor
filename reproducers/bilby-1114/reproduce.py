#!/usr/bin/env python3
"""Reproduce the Bilby #1114 tidal-parameter round-trip failure."""

from __future__ import annotations

import json


MASS_1 = 7.320188129088971
MASS_2 = 1.4957247709090036
LAMBDA_1 = 0.0
LAMBDA_2 = 1097.4026147742702


def symmetric_mass_ratio(mass_1: float, mass_2: float) -> float:
    """Return Bilby's bounded component-mass symmetric ratio."""
    return min((mass_1 * mass_2) / (mass_1 + mass_2) ** 2, 0.25)


def components_to_derived(
    lambda_1: float,
    lambda_2: float,
    mass_1: float,
    mass_2: float,
) -> tuple[float, float]:
    """Convert component lambdas to lambda_tilde and delta_lambda_tilde."""
    eta = symmetric_mass_ratio(mass_1, mass_2)
    lambda_plus = lambda_1 + lambda_2
    lambda_minus = lambda_1 - lambda_2
    lambda_tilde = (
        8
        / 13
        * (
            (1 + 7 * eta - 31 * eta**2) * lambda_plus
            + (1 - 4 * eta) ** 0.5 * (1 + 9 * eta - 11 * eta**2) * lambda_minus
        )
    )
    delta_lambda_tilde = (
        1
        / 2
        * (
            (1 - 4 * eta) ** 0.5
            * (1 - 13272 / 1319 * eta + 8944 / 1319 * eta**2)
            * lambda_plus
            + (1 - 15910 / 1319 * eta + 32850 / 1319 * eta**2 + 3380 / 1319 * eta**3)
            * lambda_minus
        )
    )
    return lambda_tilde, delta_lambda_tilde


def derived_to_components(
    lambda_tilde: float,
    delta_lambda_tilde: float,
    mass_1: float,
    mass_2: float,
) -> tuple[float, float]:
    """Convert lambda_tilde and delta_lambda_tilde back to components."""
    eta = symmetric_mass_ratio(mass_1, mass_2)
    coefficient_1 = 1 + 7 * eta - 31 * eta**2
    coefficient_2 = (1 - 4 * eta) ** 0.5 * (1 + 9 * eta - 11 * eta**2)
    coefficient_3 = (1 - 4 * eta) ** 0.5 * (
        1 - 13272 / 1319 * eta + 8944 / 1319 * eta**2
    )
    coefficient_4 = (
        1 - 15910 / 1319 * eta + 32850 / 1319 * eta**2 + 3380 / 1319 * eta**3
    )
    lambda_1 = (
        13 * lambda_tilde / 8 * (coefficient_3 - coefficient_4)
        - 2 * delta_lambda_tilde * (coefficient_1 - coefficient_2)
    ) / (
        (coefficient_1 + coefficient_2) * (coefficient_3 - coefficient_4)
        - (coefficient_1 - coefficient_2) * (coefficient_3 + coefficient_4)
    )
    lambda_2 = (
        13 * lambda_tilde / 8 * (coefficient_3 + coefficient_4)
        - 2 * delta_lambda_tilde * (coefficient_1 + coefficient_2)
    ) / (
        (coefficient_1 - coefficient_2) * (coefficient_3 + coefficient_4)
        - (coefficient_1 + coefficient_2) * (coefficient_3 - coefficient_4)
    )
    return lambda_1, lambda_2


def reproduce() -> dict[str, float]:
    """Return the complete deterministic evidence record."""
    eta = symmetric_mass_ratio(MASS_1, MASS_2)
    lambda_tilde, delta_lambda_tilde = components_to_derived(
        LAMBDA_1,
        LAMBDA_2,
        MASS_1,
        MASS_2,
    )
    roundtrip_lambda_1, roundtrip_lambda_2 = derived_to_components(
        lambda_tilde,
        delta_lambda_tilde,
        MASS_1,
        MASS_2,
    )
    return {
        "mass_1": MASS_1,
        "mass_2": MASS_2,
        "input_lambda_1": LAMBDA_1,
        "input_lambda_2": LAMBDA_2,
        "symmetric_mass_ratio": eta,
        "lambda_tilde": lambda_tilde,
        "delta_lambda_tilde": delta_lambda_tilde,
        "roundtrip_lambda_1": roundtrip_lambda_1,
        "roundtrip_lambda_2": roundtrip_lambda_2,
    }


def main() -> None:
    result = reproduce()
    if result["input_lambda_1"] < 0:
        raise AssertionError("the input lambda must be physically valid")
    if result["roundtrip_lambda_1"] >= 0:
        raise AssertionError("expected the Bilby #1114 negative roundoff")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
