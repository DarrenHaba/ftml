class FTMLDict(dict):
    """
    A dictionary subclass that can maintain FTML AST information for round-trip serialization.

    This class behaves exactly like a normal dictionary but can maintain the original
    AST structure with comments for preserving them during serialization.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ast_node = None
