# pipeline/steps/base.py
from abc import ABC, abstractmethod


#Global registry for all Step subclasses
STEP_REGISTRY = {}

def register_step(name: str):
    """
    Decorator: regiser a Step subcasll under a humna-readable name.
    """

    def decorartor(cls):
        STEP_REGISTRY[name] = cls
        return cls
    return decorartor      



class Step(ABC):

    @abstractmethod
    def execute(self, ctx : dict, callback: callable):
        """
        Execute this step
        Args:

            ctx: A dict containing at least:
                -'page' : the TaskMancerPAge instance
                - any extra data (comment,server paths, payloads)

            callback(status_code: int) : must be called when done.
            0 == success, non-zero == failure.    
        """
        
        pass



# def register_step(key: str):
#     def decorator(cls):
#         STEP_REGISTRY[key] = cls
#         return cls
#     return decorator

# class Step(ABC):
#     @abstractmethod
#     def execute(self, ctx: dict, callback):
#         """
#         ctx contains at least:
#           - 'page': the TaskMancerPage instance
#           - 'wf':   the current_working_version dict
#         callback(status_code: int) must be called when this step is done.
#         """
#         ...