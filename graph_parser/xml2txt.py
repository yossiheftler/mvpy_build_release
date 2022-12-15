import sys
import argparse
import enum
import pathlib
import xml.etree.ElementTree as xml_elem_tree


class ReturnCodes(enum.IntEnum):
    CLEAN_EXIT = 0,
    BAD_INPUT_PARAMETERS = 1,
    BAD_CONFIGURATION = 2,
    UNHANDLED_EXCEPTION = 3


########################################################
#  Translation of Genesis Play Speed combo box values  #
########################################################
genesis_play_speeds = {'0': 'Full',
                       '1': 'Original',
                       '2': '30',
                       '3': '25',
                       '4': '20',
                       '5': '10',
                       '6': '8',
                       '7': '5',
                       '8': '1'}


def xml2txt(source_file_name: str,
            target_file_name: str):
    if pathlib.Path(source_file_name).exists():
        with open(target_file_name, 'w') as target_f:
            tree = xml_elem_tree.parse(source_file_name)
            root = tree.getroot()

            target_f.write('SetMemoryPool~1000~b\n\n')

            target_f.write('###########################################################################\n'
                           '###                         Create Filters                              ###\n'
                           '###########################################################################\n')
            graph_name = 'jeffGraph'
            run_mode = None
            play_speed_index = None
            filters_list = []

            for mvxpipeline_header in root.iter('mvxpipeline'):
                run_mode = mvxpipeline_header.attrib['playmode']
                play_speed_index = mvxpipeline_header.attrib['playspeed']

            if genesis_play_speeds[play_speed_index] == 'Full':
                play_speed_translated = None  # No speed limit
            elif genesis_play_speeds[play_speed_index] == 'Original':
                play_speed_translated = '-1'  # TODO: Is this correct? unable to find in code
            else:
                play_speed_translated = genesis_play_speeds[play_speed_index]

            for mvx_filter in root.iter('filter'):
                ###################################################################################
                #  If Genesis defines a different running speed than 'Full',                      #
                #  We need to implement a #BlockFPS filter right after the source (first) filter  #
                ###################################################################################
                if len(filters_list) == 1:  # Source filter already defined
                    if play_speed_translated is not None:
                        target_f.write('\n')
                        target_f.write('createfilterbyname~#BlockFPS~blockfps~b\n')
                        target_f.write('setParams~blockfps~Buffer size~1~b\n')
                        target_f.write('setParams~blockfps~Framerate~' + play_speed_translated + '~b\n')
                        target_f.write('setParams~blockfps~Drop frames when occupied~False~b\n')
                        filters_list.append('blockfps')

                # Adding a suffix number for support of multiple instances of same filter name
                new_filter_name = mvx_filter.attrib['name'].lower() + '_1'

                while new_filter_name in filters_list:  # Such a filter instance already exists
                    split_filename = new_filter_name.split('_')
                    split_filter_prefix = split_filename[0]
                    split_filter_suffix = split_filename[1]
                    new_suffix_int = int(split_filter_suffix) + 1
                    new_filter_name = split_filter_prefix + '_' + str(new_suffix_int)

                filters_list.append(new_filter_name)

                target_f.write('\n')
                target_f.write('createfilterbyname~' + mvx_filter.attrib['name'] + '~' + new_filter_name + '~b\n')

                for mvx_parameter in mvx_filter.iter('parameter'):
                    target_f.write('setParams~' +
                                   new_filter_name + '~' +
                                   mvx_parameter.attrib['name'] + '~' +
                                   mvx_parameter.attrib['value'] + '~b\n')

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
                target_f.write('#getParams~' + graph_name + '~' + get_filter_name + '~b\n')

            target_f.write('\n'
                           '###########################################################################\n'
                           '###                         Run Graph                                   ###\n'
                           '###########################################################################\n'
                           '\n')
            target_f.write('runGraph~' + graph_name + '~' + run_mode + '~b\n')

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
    else:
        raise ValueError('Could not find file ' + source_file_name)


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
            _target_file = _source_file.replace('.xml', '.txt')
        else:
            _target_file = _parse_results.target[0]

        if not pathlib.Path(_source_file).exists():
            print('Provided input filename does not exist!')
            sys.exit(ReturnCodes.BAD_INPUT_PARAMETERS)

        xml2txt(_source_file, _target_file)

    except Exception as e:
        print('*** Abort due to caught exception! ***')
        print(e)
        sys.exit(ReturnCodes.UNHANDLED_EXCEPTION)
