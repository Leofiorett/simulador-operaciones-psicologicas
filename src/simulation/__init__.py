"""Simulador de Operaciones Psicologicas - motor multiagente."""

from .engine import run_simulation, validate_campaign
from .channels import CHANNELS
from .biases import BIASES

__all__ = ["run_simulation", "validate_campaign", "CHANNELS", "BIASES"]
