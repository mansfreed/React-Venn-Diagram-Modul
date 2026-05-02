"""Public exception hierarchy for venn-diagram-lab.

Every error raised by the package descends from VennDiagramError so callers can
catch a single exception type if they don't care about the subclass.
"""


class VennDiagramError(Exception):
    """Base class for all venn-diagram-lab errors. Catch this to handle any package error."""


class InvalidDatasetError(VennDiagramError):
    """Raised when a Dataset can't be constructed (set count out of range, parsing failed, etc.)."""


class UnknownModelError(VennDiagramError):
    """Raised when an explicit model name isn't in the bundled catalog."""


class IncompatibleModelError(VennDiagramError):
    """Raised when a model is selected that doesn't support the dataset's set count
    (e.g. ``model='proportional'`` with 4+ sets, or a 5-set model with a 3-set dataset).
    """

    def __init__(self, message: str, alternatives: list[str] | None = None) -> None:
        super().__init__(message)
        self.alternatives = list(alternatives or [])
