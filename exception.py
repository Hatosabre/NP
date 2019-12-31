class NonAnswerException(Exception):
    """解が一つもない例外"""
    pass


class MultipleAnswerException(Exception):
    """解が二つ以上ある例外"""
    pass
