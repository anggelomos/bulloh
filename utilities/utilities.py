from typing import Union


class Utilities:

    @staticmethod
    def round_number(number, amount_of_digits: int = 2, round_zero: bool = True) -> Union[float, int]:
        rounded_number = round(number, amount_of_digits)
        if rounded_number == 0 and round_zero:
            return 0
        return rounded_number
