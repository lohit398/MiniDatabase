from abc import ABC,abstractmethod

class Operator(ABC):
         
    @abstractmethod
    def next(self) -> dict:
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

