from container import wire_modules


class BaseCommand:
    def __init__(self) -> None:
        wire_modules()
