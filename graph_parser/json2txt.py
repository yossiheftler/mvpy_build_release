import sys
import argparse
import enum
import json
from pathlib import Path


class ReturnCodes(enum.IntEnum):
    CLEAN_EXIT = 0,
    BAD_INPUT_PARAMETERS = 1,
    BAD_CONFIGURATION = 2,
    UNHANDLED_EXCEPTION = 3

def json2txt(source_file_name: str, target_file_name: str):
    if not Path(source_file_name).exists():
        raise FileNotFoundError('Could not find file ' + source_file_name)
        
    with open(source_file_name, 'r') as f:
        filter_data = json.load(f)
    
    with open(target_file_name, 'w') as target_f:
        target_f.write('SetMemoryPool~1000~b\n\n')

        target_f.write('###########################################################################\n'
                        '###                         Create Filters                              ###\n'
                        '###########################################################################\n')
        graph_name = 'jeffGraph'
        filters_list = []

        for mvx_filter in filter_data:
            
            filters_list.append(mvx_filter['Name'])

            target_f.write('\n')
            target_f.write('createfilterbyname~' + mvx_filter['ID'] + '~' + mvx_filter['Name'] + '~b\n')

            for mvx_parameter,value in mvx_filter['PARAMS'].items():
                target_f.write('setParams~' +
                                mvx_filter['Name'] + '~' +
                                mvx_parameter + '~' +
                                value + '~b\n')

        target_f.write('\n'
                        '###########################################################################\n'
                        '###                         Create Graph                                ###\n'
                        '###########################################################################\n'
                        '\n')
        target_f.write('createGraph~' + graph_name + '~b\n')

        target_f.write('\n'
                        '###########################################################################\n'
                        '###                         Attach Filters                              ###\n'
                        '###########################################################################\n'
                        '\n')
        for attach_filter_name in filters_list:
            target_f.write('attachFilter~' + graph_name + '~' + attach_filter_name + '~b\n')

        target_f.write('\n'
                        '###########################################################################\n'
                        '###                         Get Filter Params                           ###\n'
                        '###########################################################################\n'
                        '\n')
        for get_filter_name in filters_list:
            target_f.write('getParams~' + graph_name + '~' + get_filter_name + '~b\n')

        target_f.write('\n'
                        '###########################################################################\n'
                        '###                         Run Graph                                   ###\n'
                        '###########################################################################\n'
                        '\n')
        target_f.write('runGraph~' + graph_name + '~255~b\n')

        target_f.write('\n'
                        '###########################################################################\n'
                        '###                         Stop Graph                                  ###\n'
                        '###########################################################################\n'
                        '#NOTE: stopGraph may abort your graph prematurely,\n'
                        '#      commenting out cleanup code!\n'
                        '\n')
        target_f.write('#stopGraph~' + graph_name + '~b\n')
        target_f.write('#deleteGraph~' + graph_name + '~b\n')

        for delete_filter_name in filters_list:
            target_f.write('#deleteFilter~' + delete_filter_name + '~b\n')


if __name__ == '__main__':
    _arg_parser = argparse.ArgumentParser(description='xml2txt',
                                          epilog='Converts Genesis style XML files to Jefferson txt format')
    _arg_parser.add_argument('--source', nargs=1,
                             help='source Genesis style XML file name', required=True)
    _arg_parser.add_argument('--target', nargs=1,
                             help='target Jefferson style XML file name'
                                  'By default will take same filename and replace suffix with .txt', required=False)
    try:
        _parse_results = _arg_parser.parse_args(sys.argv[1:])
    except SystemExit:  # library terminates immediately on fail, overriding return code
        print('Input argument parsing terminated this utility')
        sys.exit(ReturnCodes.BAD_INPUT_PARAMETERS)

    try:
        _source_file = _parse_results.source[0]

        _target_file = None

        if _parse_results.target is None:
            _target_file = _source_file.replace('.json', '.txt')
        else:
            _target_file = _parse_results.target[0]

        if not Path(_source_file).exists():
            print('Provided input filename does not exist!')
            sys.exit(ReturnCodes.BAD_INPUT_PARAMETERS)

        json2txt(_source_file, _target_file)

    except Exception as e:
        print('*** Abort due to caught exception! ***')
        print(e)
        sys.exit(ReturnCodes.UNHANDLED_EXCEPTION)
    