from abc import ABC,abstractmethod

class Operator(ABC):
         
    @abstractmethod
    def next(self) -> dict:
        pass

    @abstractmethod
    def open(self,file:str):
        pass

    @abstractmethod
    def close(self):
        pass

