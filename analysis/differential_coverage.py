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

        all_edges: Set[str] = set()
        for coverage in self.approaches.values():
            all_edges.update(coverage.edges)

        approaches_that_never_hit_edge = {
            edge: {
                approach
                for approach, coverage in self.approaches.items()
                if edge not in coverage.edges
            }
            for edge in all_edges
        }

        def scores() -> Iterator[Tuple[str, float]]:
            for approach, coverage in self.approaches.items():
                non_empty_trials = [
                    trial_edges for trial_edges in coverage.trials.values() if trial_edges
                ]
                if not non_empty_trials:
                    yield approach, 0.0
                    continue

                score = 0.0
                for edge in all_edges:
                    trials_that_hit_edge = sum(
                        1 for trial_edges in non_empty_trials if edge in trial_edges
                    )
                    score += (
                        len(approaches_that_never_hit_edge[edge])
                        * trials_that_hit_edge
                        / len(non_empty_trials)
                    )
                yield approach, score

        return scores()
