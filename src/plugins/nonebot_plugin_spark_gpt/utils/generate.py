import random
import string


def generate_random(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    numbers = random.randint(range_start, range_end)

    letters = ''.join(random.choice(string.ascii_letters) for i in range(n))

    result = str(numbers) + letters
    return result
