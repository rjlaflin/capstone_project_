from typing import Optional, Generic, TypeVar, Callable

T = TypeVar('T')
V = TypeVar('V')


class Util(Generic[T, V]):

    @classmethod
    def optional_map(cls, f: Callable[[T], V], t: Optional[T]) -> Optional[V]:
        """
        Takes an aptional value of type T and a function that can convert T -> V.
        If t is not None then run the conversion function, otherwise return none.
        """
        return f(t) if t is not None else None
