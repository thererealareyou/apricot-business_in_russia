import model
import parser
import processing_db
# TODO добавить передачу аргументов через argparse


def get_data(is_quant_model=True):
    parser.parse_consultant()
    parser.parse_all_events()
    model.launch_model('descriptions_consultant.txt', 'short_descriptions_consultant.txt', is_quant_model=True)
    processing_db.start_processing()


if __name__ == '__main__':
    get_data(is_quant_model=True)