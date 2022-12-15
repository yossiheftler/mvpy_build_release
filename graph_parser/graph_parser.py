import sys
import re
import argparse
from pathlib import Path

sys.path.append(r".")
from graph_parser.json2txt import json2txt
from graph_parser.xml2txt import xml2txt
# from json2txt import json2txt
# from xml2txt import xml2txt


class GraphParser():
    def __init__(self, input_file, output_file, cli_params=None):
        self.input_graph = input_file
        self.txt_file = output_file
        self.cli_params = cli_params

    def txt_to_dict(self):
        lines = []
        graph_data = []

        data_after_parse = []
        with open(self.input_graph, 'r') as f:
            lines = f.readlines()

        for n, line in enumerate(lines):
            if line.startswith((" ", "\t")):
                raise SyntaxError("Error in file: " + self.txt_file + " in line " + str(n))

            s_line = line.strip()
            if len(s_line) > 0 and not s_line.startswith("#"):
                results = re.findall(r"\$([A-Z,,a-z,0-9]*)\$", s_line)
                for param in results:
                    try:
                        s_line = s_line.replace(f"${param}$", self.cli_params[param])
                    except (KeyError, TypeError):
                        raise KeyError(f"Parameter {param} is not specified!")

                args = s_line.split("~")

                graph_data.append({"COMMAND": args[0], "ARGS": args[1:]})
                data_after_parse.append(s_line)
            else:
                data_after_parse.append("##")

        with open(self.txt_file, 'w') as f:
            for line in data_after_parse:
                f.write(line + "\n")

        return graph_data

    def xml_parser(self):
        try:
            xml2txt(self.input_graph, self.txt_file)
            self.input_graph = self.txt_file
        except Exception as e:
            print(e)
        return self.txt_to_dict()

    def json_parser(self):
        try:
            json2txt(self.input_graph, self.txt_file)
            self.input_graph = self.txt_file
        except Exception as e:
            print(e)
        return self.txt_to_dict()

    def __call__(self):
        if Path(self.input_graph).suffix == ".xml":
            graph_dict = self.xml_parser()
        elif Path(self.input_graph).suffix == ".json":
            graph_dict = self.json_parser()
        else:
            graph_dict = self.txt_to_dict()

        return graph_dict


if __name__ == "__main__":
    global args
    parser = argparse.ArgumentParser(description='GraphParser', epilog='Parse and converts Genesis style XML or JeffersonPy JSON files to MVGraphAPI txt format')
    parser.add_argument('--input', '-i', help='Graph file to load, either in XML, JSON', required=True)
    parser.add_argument('--output', '-o', help='Graph file in TXT format to be created', required=True)

    args = parser.parse_args()
    arguments = vars(args)

    if not Path(arguments['input']).exists():
        print("Graph file does not exist!")
        sys.exit(1)

    if Path(arguments['input']).suffix != ".xml" and Path(arguments['input']).suffix != ".json" and Path(arguments['input']).suffix != ".txt":
        print("Graph file not in the right format [xml | json | txt]")
        sys.exit(1)

    GraphParser(arguments['input'], arguments['output'])()

    sys.exit(0)
