from abc import ABC, abstractmethod


class BaseModule(ABC):
    """Defines the abstract base class for tifinity modules"""

    @abstractmethod
    def add_subparser(self, mainparser):
        pass

    @abstractmethod
    def process_cli(self, args):
        pass
