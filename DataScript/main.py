import model
import parser
# TODO добавить передачу аргументов через argparse


def get_data(is_quant_model=True):
    parser.parse_consultant()
    # parser.parse_all_events()
    model.launch_model('data.txt', 'output.txt', is_quant_model=True)


if __name__ == '__main__':
    get_data(is_quant_model=True)