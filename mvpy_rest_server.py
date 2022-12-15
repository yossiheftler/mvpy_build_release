import sys
import signal
import threading
import argparse
import logging
import MvxGraph
from datetime import datetime
from typing import List
from pathlib import Path
from flask import Flask, request, abort, jsonify

sys.path.append(r".")
from graph_parser.graph_parser import GraphParser


DEFAULT_LIB_PATH = str(Path.cwd())
DEFAULT_MEMPOOL  = 1000
DEFAULT_PORT     = "7500"


class NucRestRunner():
    UPLOAD_FOLDER = r'C:\RingTeam\openmv4d\mvpy\uploads'
    LOGS_FOLDER   = r"./mvpy_logs/"
    ALLOWED_EXTENSIONS = {'txt', 'xml', 'json'}

    api_name_lut = {
        "setagent"           : "empty",
        "rungraph"           : "empty",
        "setmemorypool"      : "empty",
        "createfilterbyname" : "create_filter_from_name",
        "createfilterbyguid" : "create_filter_from_guid",
        "createfilter"       : "create_filter_from_guid",
        "creategraph"        : "create_graph",
        "attachfilter"       : "add_filter_to_graph",
        "getparams"          : "get_filter_parameter",
        "setparams"          : "set_filter_parameter",
        "stopgraph"          : "stop_graph",
        "pausegraph"         : "pause_graph",
        "resumegraph"        : "resume_graph",
        "deletefilter"       : "destroy_filter",
        "deletegraph"        : "destroy_graph",
        "cleanall"           : "destroy_graph"
    }

    def __init__(self, mvgraphapi_plugins_path, memory_pool_frequency, port, local_graph=None, cli_params={}):
        self.app = Flask(__name__)
        self.app.secret_key               = 'super secret key'
        self.app.config['UPLOAD_FOLDER']  = self.UPLOAD_FOLDER
        self.app.json.sort_keys = False
        self.app_port           = port

        self.build_path         = mvgraphapi_plugins_path
        self.mempool            = memory_pool_frequency
        self._graph_core        = MvxGraph.MvxGraphCoreWrapper(self.build_path, self.mempool)
        self.graph_commands     = {}
        self.filters_dict       = {}
        self.attached_filters   = {}
        self.play_mode          = None
        self.current_graph      = None
        self.local_graph        = local_graph
        self.cli_params         = cli_params

        Path(self.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(self.LOGS_FOLDER).mkdir(parents=True, exist_ok=True)
        log_file = Path(self.LOGS_FOLDER).joinpath(rf'MVPY_REST_SERVER_{datetime.now().strftime("%d-%m-%Y_%I-%M-%S%p")}.log')
        logging.basicConfig(filename=str(log_file), level=logging.DEBUG)
        signal.signal(signal.SIGINT, self.signal_handler)

        if local_graph and Path(local_graph).exists():
            self.current_graph = Path(local_graph)
            try:
                self.graph_commands = self.load_graph_from_file(self.current_graph, self.cli_params)
                self.invoke_graph_commands(self.graph_commands)
                self._graph_core.build_graph()
            except Exception as e:
                print(str(e) + '  build_current_graph failed')
                sys.exit(1)

################# REST API Functions ####################################
#########################################################################

        @self.app.after_request
        def response_processor(response):
            if request.form:
                logging.log(logging.DEBUG, 'Request Body: %s', request.form)
            else:
                logging.log(logging.DEBUG, 'Request Body: %s', request.get_data(as_text=True))

            @response.call_on_close
            def process_after_request():
                logging.log(logging.DEBUG, 'Response Body: %s', response.get_data(as_text=True))

            return response

        @self.app.route('/')
        def hello_world():
            return jsonify('Hello, REST!'), 200

        @self.app.route('/server_status', methods=["GET"])
        def get_server_status():
            return jsonify('OK'), 200

        @self.app.route('/get_cli_params', methods=["GET"])
        def get_cli_params():
            return jsonify(self.cli_params), 200

        @self.app.route('/set_cli_params', methods=["POST"])
        def set_cli_params():
            if not request.is_json:
                abort(500, description="Request not in the right Format")

            req = request.get_json()
            self.cli_params = req['cli_params']
            return jsonify(self.cli_params), 200

        @self.app.route('/graph/upload', methods=["POST"])
        def upload_graph():
            if 'filename' not in request.form:
                abort(500, description="Request not in the right Format")

            if not self.allowed_file(request.form['filename']):
                abort(500, description="File format not supported")

            self.cli_params = request.form.to_dict()
            self.current_graph = Path(self.app.config['UPLOAD_FOLDER']).joinpath(request.form['filename'])
            f = None

            if 'file' in request.files:
                f = request.files['file']
            elif 'file' in request.form:
                f = request.form['file']
            else:
                abort(500, description='No File attached')

            if not self.save_graph_locally(f):
                abort(500, description='Could not save the Graph file locally!')

            self.cli_params.pop('file', None)
            self.cli_params.pop('filename', None)

            try:
                self.graph_commands = self.load_graph_from_file(self.current_graph, self.cli_params)
            except Exception as e:
                abort(500, description=str(e) + '  build_remote_graph failed')

            return jsonify("Graph uploded"), 200

        @self.app.route('/graph/upload_run', methods=["POST"])
        def upload_run():
            try:
                if not self.r_destroy_graph():
                    raise ValueError
                upload_graph()
                build_run_graph()
            except Exception as e:
                abort(500, description=str(e) + '  upload_graph_run failed')

            return jsonify(self.filters_dict), 200

        @self.app.route('/graph/build_run', methods=["POST"])
        def build_run_graph():
            try:
                if not build_current_graph():
                    raise ValueError
                if not run_current_graph():
                    raise ValueError
            except Exception as e:
                abort(500, description=str(e) + '  build_run failed')

            return jsonify(self.filters_dict), 200

        @self.app.route('/graph/build_remote', methods=["POST"])
        def build_remote_graph():
            if not request.is_json:
                abort(500, description="Request not in the right Format")

            req = request.get_json()

            if 'remote_graph' not in req:
                abort(500, description="Request not in the right Format")

            self.current_graph = req['remote_graph']
            self.cli_params = req.get('cli_params', None)
            try:
                self.graph_commands = self.load_graph_from_file(self.current_graph, self.cli_params)
            except Exception as e:
                abort(500, description=str(e) + '  build_remote_graph failed')

            try:
                if not build_current_graph():
                    raise ValueError
            except Exception as e:
                abort(500, description=str(e) + '  build_remote_graph failed')

            return jsonify(self.filters_dict), 200

        @self.app.route('/graph/build_run_remote', methods=["POST"])
        def build_run_remote():
            if not self.r_destroy_graph():
                raise ValueError

            build_remote_graph()

            try:
                if not run_current_graph():
                    raise ValueError
            except Exception as e:
                abort(500, description=str(e) + '  build_run_remote failed')

            return jsonify(self.filters_dict), 200

        @self.app.route('/graph/build', methods=["POST"])
        def build_current_graph():
            if not self.graph_commands:
                return jsonify("No graph is loaded"), 404
            try:
                self.invoke_graph_commands(self.graph_commands)
                self._graph_core.build_graph()
            except Exception as e:
                abort(500, description=str(e) + '  build_current_graph failed')

            return jsonify(self.filters_dict), 200

        @self.app.route('/graph/stop', methods=["POST"])
        def stop_current_graph():
            try:
                self.r_stop_graph(None)
            except Exception as e:
                abort(500, description=str(e) + '  stop_current_graph failed')

            return jsonify("Graph stopped"), 200

        @self.app.route('/graph/pause', methods=["POST"])
        def pause_current_graph():
            try:
                self.r_pause_graph(None)
            except Exception as e:
                abort(500, description=str(e) + '  pause_current_graph failed')

            return jsonify("Graph paused"), 200

        @self.app.route('/graph/resume', methods=["POST"])
        def resume_current_graph():
            try:
                self.r_resume_graph(None)
            except Exception as e:
                abort(500, description=str(e) + '  resume_current_graph failed')

            return jsonify("Graph resumed"), 200

        @self.app.route('/graph/run', methods=["POST"])
        def run_current_graph():
            if not self.is_graph_running() or self._graph_core.get_graph_state() == MvxGraph.GraphState.PLAYING:
                return jsonify("No graph is build"), 400

            try:
                threading.Thread(target=self._graph_core.play_graph, args=[int(self.play_mode), ]).start()

            except Exception as e:
                abort(500, description=str(e) + '  run_graph failed')

            return jsonify("Graph is now running"), 200

        @self.app.route('/graph/get_state', methods=["GET"])
        def get_graph_state():
            return jsonify(self._graph_core.get_graph_state().name)

        @self.app.route('/graph/get_filters', methods=["GET"])
        def get_graph_filters():
            if self.is_graph_running():
                return jsonify({k: v for k, v in sorted(self.attached_filters.items(), key=lambda item: item[1])}), 200
            else:
                return jsonify("No graph is loaded!"), 404

        @self.app.route('/graph/get_play_mode', methods=["GET"])
        def get_play_mode():
            if not self.play_mode:
                return jsonify("No play_mode was found!, build Graph first"), 404
            return jsonify(self.play_mode), 200

        @self.app.route('/graph/set_play_mode', methods=["POST"])
        def set_play_mode():
            if self.get_state() == MvxGraph.GraphState.PLAYING:
                return jsonify("Can't change play_mode while graph is running"), 400
            if request.is_json:
                req = request.get_json()
                self.play_mode = req['play_mode']
            else:
                abort(500, description="Request not in the right Format")
            return jsonify(self.play_mode), 200

        @self.app.route('/graph/terminate', methods=["POST"])
        def terminate_graph():
            if not self.is_graph_running():
                return jsonify("No graph is loaded!"), 404

            if not self.r_destroy_graph(None):
                abort(500, description='terminate_graph failed')

            return jsonify("Graph terminated"), 200

        @self.app.route('/graph/get_filter_param', methods=["GET"])
        def get_filter_param():
            if not self.is_graph_running():
                return jsonify("No graph is loaded!"), 404

            if not request.is_json:
                abort(500, description="Request not in the right Format")

            req = request.get_json()

            if not {"unique_name", "param_name"} <= set(req):
                abort(500, description="Request not in the right Format")

            if req['unique_name'] not in self.filters_dict :
                return jsonify(f"No Filter '{req['unique_name']}' was found!"), 404

            try:
                filter_id = self.filters_dict[req['unique_name']]
                return jsonify(self._graph_core.get_filter_parameter(filter_id, str(req['param_name']))), 200
            except Exception as e:
                return abort(500, description=str(e) + '  get_parameter failed')

        @self.app.route('/graph/set_filter_param', methods=["POST"])
        def set_filter_param():
            if not self.is_graph_running():
                return jsonify("No graph is loaded!"), 404

            if not request.is_json:
                abort(500, description="Request not in the right Format")

            req = request.get_json()

            if not {"unique_name", "param_name", "param_value"} <= set(req):
                abort(500, description="Request not in the right Format")

            try:
                filter_id = self.filters_dict[req['unique_name']]
                self._graph_core.set_filter_parameter(filter_id, req['param_name'], req['param_value'])
                return jsonify(self._graph_core.get_filter_parameter(filter_id, str(req['param_name']))), 200
            except Exception as e:
                return abort(500, description=str(e) + '  get_parameter failed')

        @self.app.route('/graph/set_params', methods=["POST"])
        def set_params():
            if not self.is_graph_running():
                return jsonify("No graph is loaded!"), 404

            upload_graph()
            self.invoke_graph_commands(self.graph_commands, mode="SET")

            return jsonify("Set params successfully"), 200

        @self.app.route('/graph/get_params', methods=["GET"])
        def get_params():
            if not self.is_graph_running():
                return jsonify("No graph is loaded!"), 404

            if not request.is_json:
                abort(500, description="Request not in the right Format")

            req = request.get_json()

            if "unique_name" not in req:
                abort(500, description="Request not in the right Format")

            if not req['unique_name'] in self.filters_dict:
                return jsonify(f"No Filter '{req['unique_name']}' was found!"), 404
            try:
                return jsonify(self._graph_core.get_filter_parameters(self.filters_dict[req['unique_name']])), 200
            except Exception as e:
                return abort(500, description=str(e) + '  get_params failed')

        @self.app.route('/shutdown', methods=["POST"])
        def shutdown():
            self.shutdown_server()
            return jsonify("ShutDown")

#################### Class Functions ####################################
#########################################################################
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def is_graph_running(self):
        current_state = self._graph_core.get_graph_state()

        if current_state.value == MvxGraph.GraphState.PLAYING \
            or current_state.value == MvxGraph.GraphState.PAUSED \
                or current_state.value == MvxGraph.GraphState.STOPPED:
            return True
        else:
            return False

    def load_graph_from_file(self, graph, cli_params):
        name    = Path(graph).stem
        suffix  = Path(graph).suffix[1:]

        return GraphParser(str(graph), str(Path(graph).with_name(f"{name}_from_{suffix}.txt")), cli_params)()

    def invoke_graph_commands(self, graph_commands, mode="BUILD"):
        for line in graph_commands:
            command = str(line['COMMAND']).lower()

            if command == "setmemorypool" or command == "setagent":  # Currently not supported
                continue

            if command == "rungraph":  # only extract play_mode
                self.play_mode = line['ARGS'][1]
                continue

            if mode == "SET":
                if command != "setparams":
                    continue

            # Run each TXT command line by line
            method_to_call = getattr(self, f"r_{self.api_name_lut[command]}")
            method_to_call(line['ARGS'])

    def get_state(self) -> MvxGraph.GraphState:
        state_enum = self._graph_core.get_graph_state()
        return MvxGraph.GraphState(state_enum)

    def save_graph_locally(self, file_data):
        if type(file_data).__name__ == "FileStorage":
            file_data.save(self.current_graph)

        elif type(file_data).__name__ == "str":
            with open(self.current_graph, 'w') as f:
                f.write(file_data.rstrip('\r\n'))
        else:
            return False

        return True

    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        if self.is_graph_running():
            self.r_destroy_graph(None)

        sys.exit(-1)

    def run_server(self):
        self.app.run(host="0.0.0.0", port=int(self.app_port), debug=False)

    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

################# MVX Core wrapFunctions ################################
#########################################################################

    def empty(self, args: List[str] = None):
        pass

    def r_get_available_filters(self, args: List[str] = None):
        self._graph_core.get_available_filters()

    def r_create_filter_from_name(self, args: List[str]) -> bool:
        try:
            id = self._graph_core.create_filter_from_name(args[0])
            self.filters_dict[args[1]] = id
        except Exception as e:
            print(e)
            return False

        return True

    def r_create_filter_from_guid(self, args: List[str]) -> bool:
        try:
            id = self._graph_core.create_filter_from_guid(args[0], args[1])
            self.filters_dict[args[1]] = id
        except Exception as e:
            print(e)
            return False

        return True

    def r_create_graph(self, args: List[str] = None) -> bool:
        try:
            self._graph_core.create_graph()
        except Exception as e:
            print(e)
            return False

        return True

    def r_stop_graph(self, args: List[str] = None):
        try:
            self._graph_core.stop_graph()

            print('Graph is stopped')
        except Exception as e:
            print(e)
            return False

        return True

    def r_pause_graph(self, args: List[str] = None):
        try:
            self._graph_core.pause_graph()

            print('Graph is paused')
        except Exception as e:
            print(e)
            return False

        return True

    def r_resume_graph(self, args: List[str] = None):
        try:
            self._graph_core.resume_graph()

            print('Graph is resused')
        except Exception as e:
            print(e)
            return False

        return True

    def r_destroy_graph(self, args: List[str] = None) -> bool:
        try:
            self.filters_dict   = {}
            self.graph_commands = {}
            self.play_mode      = None

            if self._graph_core.get_graph_state() == MvxGraph.GraphState.NOT_BUILT:
                return True

            self._graph_core.stop_graph()
            self._graph_core.destroy_graph()
        except Exception as e:
            print(e)
            return False

        return True

    def r_destroy_filter(self, args: List[str]) -> int:
        try:
            ret_code = self._graph_core.destroy_filter(args[0])
        except Exception as e:
            print(e)
            return -1

        return ret_code

    def r_set_filter_parameter(self, args: List[str]):
        try:
            self._graph_core.set_filter_parameter(self.filters_dict[args[0]], args[1], args[2])
        except Exception as e:
            print(e)
            return False
        return True

    def r_get_filter_parameter(self, args: List[str]) -> str:
        try:

            res = self._graph_core.get_filter_parameter(self.filters_dict[args[0]], args[1])
        except Exception as e:
            print(e)
            return ""

        return res

    def r_add_filter_to_graph(self, args: List[str]) -> bool:
        try:
            self._graph_core.add_filter_to_graph(self.filters_dict[args[1]])
            self.attached_filters[args[1]] = self.filters_dict[args[1]]
        except Exception as e:
            print(e)
            return False
        return True


if __name__ == "__main__":
    global args
    parser = argparse.ArgumentParser(
        description='MvxGraph demo',
        epilog='This demo loads and runs a simple XML graph in forward once mode,and waits until completion'
    )

    parser.add_argument(
        '-l',
        '--lib',
        help='Overwrite default library path file (default: {DEFAULT_LIB_PATH})',
        required=False
    )

    parser.add_argument(
        '-p',
        '--port',
        help='Overwrite default port number (default: 7500)',
        required=False
    )

    parser.add_argument(
        '-g',
        '--graph',
        help='Graph file to load, either in XML, JSON or TXT format',
        required=False
    )

    parser.add_argument(
        '--mempool',
        help=f"Overwrite default memory pool allocation (default: {str(DEFAULT_MEMPOOL)})",
        type=int,
        required=False
    )
    parser.add_argument('params', nargs='*')
    args = parser.parse_args()
    arguments = vars(args)

    lib_path  = DEFAULT_LIB_PATH
    mempool   = DEFAULT_MEMPOOL
    port      = DEFAULT_PORT

    if arguments['graph']:
        suffix = Path(arguments['graph']).suffix
        if suffix != ".xml" and suffix != ".json" and suffix != ".txt":
            print("Graph file not in the right format [xml | json | txt]")
            sys.exit(1)

    if arguments['lib']:
        lib_path = arguments['lib']
        if not Path(lib_path).exists() or Path(lib_path).stat().st_size == 0:
            print("Library path does not exist or empty")
            sys.exit(1)

    if arguments['port']:
        port = arguments['port']

    if arguments['mempool']:
        if not arguments['mempool'] > 0 or not arguments['mempool'] < 50000:
            print("Memory Pool argument must be in range of 0-50000!")
            sys.exit(1)

        mempool = arguments['mempool']

    cli_params = {}

    for param in arguments['params']:
        try:
            cli_params[str(param).split("=")[0]] = str(param).split("=")[1]
        except Exception:
            raise argparse.ArgumentTypeError("Parsing CLI parameters failed (example usage: \"NUM=1 PORT=5555\")")

    nrg = NucRestRunner(lib_path, mempool, port, arguments['graph'], cli_params)
    nrg.run_server()
