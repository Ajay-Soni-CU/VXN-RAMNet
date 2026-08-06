"""Typed exceptions used across pipeline boundaries."""
class VxnRamNetError(Exception):
    """Base package error."""

class ConfigurationError(VxnRamNetError):
    """Configuration is invalid or unsafe."""

class InputValidationError(VxnRamNetError):
    """An input file or stream failed validation."""

class ArtifactError(VxnRamNetError):
    """A persisted artifact is missing, corrupt, or incompatible."""

class StageExecutionError(VxnRamNetError):
    """A pipeline stage failed."""

class ModelLoadError(VxnRamNetError):
    """A visual encoder could not be loaded safely."""

class InsufficientEvidenceError(VxnRamNetError):
    """The available sequence does not contain enough evidence."""
