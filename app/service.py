def add(a: int, b: int) -> int:
    return a + b + 1


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
