from dataclasses import dataclass
from statistics import median
from typing import Dict, Iterable, Iterator, Set, Tuple


@dataclass(frozen=True)
class ApproachCoverage:
    trials: Dict[str, Set[str]]

    @property
    def edges(self) -> Set[str]:
        covered: Set[str] = set()
        for trial_edges in self.trials.values():
            covered.update(trial_edges)
        return covered

    def relcov(self, reference: "ApproachCoverage") -> float:
        reference_edges = reference.edges
        if not reference_edges:
            return 0.0
        if not self.trials:
            return 0.0
        return float(
            median(
                len(trial_edges & reference_edges) / len(reference_edges)
                for trial_edges in self.trials.values()
            )
        )


class DifferentialCoverage:
    def __init__(self, campaign: Dict[str, Dict[str, Set[str]]]) -> None:
        self.approaches = {
            approach: ApproachCoverage(trials)
            for approach, trials in sorted(campaign.items())
        }

    def relscores(self) -> Iterable[Tuple[str, float]]:
        if len(self.approaches) < 2:
            return ((approach, 0.0) for approach in self.approaches)

        edge_approaches: Dict[str, Set[str]] = {}
        for approach, coverage in self.approaches.items():
            for edge in coverage.edges:
                edge_approaches.setdefault(edge, set()).add(approach)

        def scores() -> Iterator[Tuple[str, float]]:
            for approach, coverage in self.approaches.items():
                exclusive_edges = sum(
                    1
                    for edge in coverage.edges
                    if edge_approaches.get(edge) == {approach}
                )
                yield approach, float(exclusive_edges)

        return scores()
