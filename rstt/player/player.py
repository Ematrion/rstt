class Player():
    def __init__(self, name: str, level: float) -> None:
        self._name = name
        self._level = level
    
    # --- getter --- #
    def name(self) -> str:
        return self._name
    
    def level(self) -> float:
        return self._level
    
    # --- magic methods --- #
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        return f"Player - name: {self._name}, level: {self._level}"