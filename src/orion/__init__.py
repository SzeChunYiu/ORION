"""ORION: evidence-governed recursive research operating system."""

from orion.core.problem import Problem
from orion.core.solution import Solution, SolutionStatus
from orion.engine.paper_parity_solver import PaperParityOrionSolver as OrionSolver
from orion.engine.solver import OrionSolver as KernelOrionSolver
from orion.engine.solver import SolverConfig

__all__ = [
    "KernelOrionSolver",
    "OrionSolver",
    "Problem",
    "Solution",
    "SolutionStatus",
    "SolverConfig",
]
