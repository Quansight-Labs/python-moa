from .moa import MOAParser
from ..visualize import print_ast


if __name__ == "__main__":
    parser = MOAParser()

    print('MOA Calculator')
    while True:
        text = input('>>> ')
        if text in {'q', 'quit'}: break
        print_ast(*parser.parse(text))
