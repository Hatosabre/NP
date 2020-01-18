class NonAnswerException(Exception):
    """解が一つもない例外"""
    pass


class MultipleAnswerException(Exception):
    """解が基準以上ある例外"""
    pass
