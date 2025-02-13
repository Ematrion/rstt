class Player():
    def __init__(self, name: str, level: float) -> None:
        self.__name = name
        self.__level = level
    
    # --- getter --- #
    def name(self) -> str:
        return self.__name
    
    def level(self) -> float:
        return self.__level
    
    # --- magic methods --- #
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        return f"Player - name: {self.__name}, level: {self.__level}"
    