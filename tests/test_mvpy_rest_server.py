
import sys
import pytest
import platform
from pathlib import Path

sys.path.append(r".")
from mvpy_rest_server import NucRestRunner # noqa
import MvxGraph # noqa

DEFAULT_LIB_PATH = r".\libc"
DEFAULT_MEMPOOL  = 1000
MAX_STR = 256
DEFAULT_PORT     = "7500"

current_dir = ""


@pytest.fixture
def nuc_rest_runner(pytestconfig):
    global current_dir
    current_dir = lib = pytestconfig.getoption("lib")
    if not lib:
        current_dir = lib = DEFAULT_LIB_PATH
    return NucRestRunner(lib, DEFAULT_MEMPOOL, DEFAULT_PORT)


@pytest.fixture()
def client(nuc_rest_runner):
    return nuc_rest_runner.app.test_client()


@pytest.fixture()
def runner(nuc_rest_runner):
    return nuc_rest_runner.app.test_cli_runner()


def test_nuc_rest_runner_init(nuc_rest_runner):
    assert(nuc_rest_runner._graph_core)

    assert(not nuc_rest_runner.is_graph_running())
    assert(not nuc_rest_runner.graph_commands)
    assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)


# def test_nuc_rest_runner_parse(nuc_rest_runner):
#     # Test XML Parser
#     commands = None
#     commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/devices_only.xml")), {"PORT": "5555"})
#     assert(Path(r"./tests/devices_only_from_xml.txt").exists())
#     assert(commands)
#
#     # Test JSON Parser
#     commands = None
#     commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/lord_rtmesh.json")), {"PORT": "5555", "LORDIP": "192.168.77.112", "NUM": "1"})
#     assert(Path(r"./tests/lord_rtmesh_from_json.txt").exists())
#     assert(commands)
#
#     # Test TXT Parser
#     commands = None
#     commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/TX_MV_DM.txt")), {"CONF": str(Path(r"c:\nuc\ring_it\Configs"))})
#     assert(Path(r"./tests/TX_MV_DM_from_txt.txt").exists())
#     assert(commands)
#
#     assert(not nuc_rest_runner.is_graph_running())
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)


# def test_nuc_rest_runner_run(nuc_rest_runner):
#     nuc_rest_runner.r_destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
#     assert(nuc_rest_runner.graph_commands)
#
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#
#     nuc_rest_runner._graph_core.play_graph(int(nuc_rest_runner.play_mode))
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.PLAYING)
#     assert(nuc_rest_runner.is_graph_running())

# def test_nuc_rest_runner_build(nuc_rest_runner):
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     input_mvx = ""
#     if platform.system() == "Windows":
#         input_mvx = f"{str(Path.cwd())}\\tests\\morning.mvx"
#     if platform.system() == "Linux":
#         input_mvx = f"{str(Path.cwd())}/tests/morning.mvx"
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": input_mvx})
#     assert(nuc_rest_runner.graph_commands)
#
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.STOPPED)
#     assert(nuc_rest_runner.is_graph_running())
#     nuc_rest_runner.r_destroy_graph()


# def test_nuc_rest_runner_stop(nuc_rest_runner):
#     nuc_rest_runner.r_destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
#     assert(nuc_rest_runner.graph_commands)
#
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#
#     nuc_rest_runner._graph_core.play_graph(int(nuc_rest_runner.play_mode))
#     nuc_rest_runner._graph_core.stop_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.STOPPED)


# def test_nuc_rest_runner_terminate(nuc_rest_runner):
#     nuc_rest_runner.r_destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
#     assert(nuc_rest_runner.graph_commands)
#
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#
#     nuc_rest_runner._graph_core.play_graph(int(nuc_rest_runner.play_mode))
#     nuc_rest_runner._graph_core.stop_graph()
#     nuc_rest_runner._graph_core.destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)


# def test_nuc_rest_runner_get_filter_param(nuc_rest_runner, client):
#     nuc_rest_runner.r_destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#     nuc_rest_runner._graph_core.play_graph(int(nuc_rest_runner.play_mode))
#
#     response = client.get("/graph/get_filter_param", json={"unique_name": "mvx2filewriter_1", "param_name": "Enable Recording"})
#
#     assert b"False" in response.data


def test_nuc_rest_runner_set_filter_param(nuc_rest_runner, client):
    nuc_rest_runner.r_destroy_graph()
    assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)

    nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
    nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
    nuc_rest_runner._graph_core.build_graph()

    client.post("/graph/set_filter_param", json={"unique_name": "mvx2filewriter_1", "param_name": "Write XML", "param_value": "False"})
    response = client.get("/graph/get_filter_param", json={"unique_name": "mvx2filewriter_1", "param_name": "Enable Recording"})

    assert b"False" in response.data


def test_nuc_rest_runner_set_params(nuc_rest_runner, client):
    nuc_rest_runner.r_destroy_graph()
    assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)

    nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
    nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
    nuc_rest_runner._graph_core.build_graph()

    filepath = r".\tests\set_multiple.json"
    filename = Path(filepath).name  # => "file.json"

    client.post("/graph/set_params", data={'filename': filename, 'file': open(filepath, 'rb')})

    response = client.get("/graph/get_filter_param", json={"unique_name": "mvx2filewriter_1", "param_name": "Write XML"})
    assert b"False" in response.data


# def test_nuc_rest_runner_get_play_mode(nuc_rest_runner, client):
#     nuc_rest_runner.r_destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#
#     nuc_rest_runner._graph_core.play_graph(int(nuc_rest_runner.play_mode))
#
#     response = client.get("/graph/get_play_mode")
#
#     assert b"3" in response.data


def test_nuc_rest_runner_set_play_mode(nuc_rest_runner, client):
    nuc_rest_runner.r_destroy_graph()
    assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)

    nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
    nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
    nuc_rest_runner._graph_core.build_graph()

    client.post("/graph/set_play_mode", json={"play_mode": "255"})

    response = client.get("/graph/get_play_mode")

    assert b"255" in response.data


# def test_nuc_rest_runner_get_filters(nuc_rest_runner, client):
#     nuc_rest_runner.r_destroy_graph()
#     assert(nuc_rest_runner.get_state() == MvxGraph.GraphState.NOT_BUILT)
#
#     nuc_rest_runner.graph_commands = nuc_rest_runner.load_graph_from_file(str(Path(r"./tests/read_decomp_write.xml")), {"INPUT": f"{str(Path.cwd())}\\tests\\morning.mvx"})
#     nuc_rest_runner.invoke_graph_commands(nuc_rest_runner.graph_commands)
#     nuc_rest_runner._graph_core.build_graph()
#
#     response = client.get("/graph/get_filters")
#
#     assert b"mvx2filereader" in response.data
#     assert b"#autodecompressor" in response.data
#     assert b"mvx2filewriter" in response.data
