class NumberConverter:

    @staticmethod
    def to_string(number:int) -> str:
        # input: 44100, output: 44.1k
        if number >= 1000:
            if number % 1000 == 0:
                return f'{int(number/1000)}k'
            return f'{number/1000:.1f}k'
        return str(number)

    @staticmethod
    def from_string(text:str) -> int:
        # input: 44.1k, output: 44100
        text = text.lower().strip()
        if 'k' in text:
            number = text.replace('k', '')
            return int(float(number) * 1000)
        return int(text)
