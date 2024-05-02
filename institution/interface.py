from abc import ABC, abstractmethod

class InstitutionInterface(ABC):
    """Interface for financial institutions."""

    @abstractmethod
    def load_stmt_pdf(cnt) -> None:
        """Loads contents from a PDF statement."""
        pass

    @abstractmethod
    def _parse_opening_balance(self) -> int:
        """Parse the opening balance."""
        pass
    
    @abstractmethod
    def _parse_closing_balance(self) -> int:
        """Parse the closing balance."""
        pass

    @abstractmethod
    def _parse_transactions(self) -> list:
        """Parse the transactions."""
        pass

    @abstractmethod
    def _validate_balance(self) -> bool:
        """Validate the balance."""
        pass

    @abstractmethod
    def _write_csv(self) -> None:
        """Write the transactions to a CSV file."""
        pass
