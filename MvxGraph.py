import ctypes
import os
from enum import IntEnum
import platform


if platform.system() == "Windows":
    MVX_GRAPH_CORE__LIBRARY_NAME = 'MvxGraphCore.dll'
else:
    MVX_GRAPH_CORE__LIBRARY_NAME = 'libMvxGraphCore.so'


class GraphState(IntEnum):
    NOT_BUILT = 0,
    ERROR = 1,
    PLAYING = 2,
    PAUSED = 3,
    STOPPED = 4


class GraphPlaybackMode(IntEnum):
    RPM_FORWARD_ONCE = 0,
    RPM_FORWARD_LOOP = 1,
    RPM_BACKWARD_ONCE = 2,
    RPM_BACKWARD_LOOP = 3,
    RPM_PINGPONG = 4,
    RPM_PINGPONG_INVERSE = 5,
    RPM_REALTIME = 255


class MvxGraphCoreWrapper:
    _library = None
    _max_error_str_buf_len = (8*1024)
    _max_return_buff_len   = (8*1024)

    def __init__(self, graphapi_plugins_path: str, memory_pool_frequency: int = 1000):
        try:
            bin_path = os.path.join(graphapi_plugins_path)
            # os.chdir(bin_path)
            self._library = ctypes.cdll.LoadLibrary(os.path.join(bin_path, MVX_GRAPH_CORE__LIBRARY_NAME))

            ctypes_wrapper = self._library.Init
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_char_p, ctypes.c_int]

            rc = ctypes_wrapper(graphapi_plugins_path.encode('ascii'), memory_pool_frequency)

            if rc == 1:
                print('MvxGraphCore object created successfully')
            else:
                raise ValueError(self.get_last_error())

        except Exception as e:
            raise ValueError('Failed to init MvxGraphCore, due to exception:', e)

    def get_available_filters(self):
        try:
            ctypes_wrapper = self._library.GetAvailableFilters
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = []

            rc = ctypes_wrapper()

            if rc == 1:
                return
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to retrieve available filters, due to exception:', e)

    def get_filter_guid_by_name(self, filter_name: str, max_ret_buff_size: int = _max_return_buff_len) -> str:
        try:
            ctypes_wrapper = self._library.GetFilterGuidByName
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]

            ret_str = ctypes.create_string_buffer(max_ret_buff_size)
            # TODO - check if not allocated
            rc = ctypes_wrapper(filter_name.encode(), max_ret_buff_size, ret_str)

            if rc == 1:
                return ret_str.value.decode('ascii')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to get GUID for MVX filter ', filter_name, 'due to exception', e)

    def get_filter_name_by_guid(self, filter_guid: str, max_ret_buff_size: int = _max_return_buff_len) -> str:
        try:
            ctypes_wrapper = self._library.GetFilterNameByGuid
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]

            ret_str = ctypes.create_string_buffer(max_ret_buff_size)
            # TODO - check if not allocated
            rc = ctypes_wrapper(filter_guid.encode(), max_ret_buff_size, ret_str)

            if rc == 1:
                return ret_str.value.decode('ascii')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to get name for MVX filter GUID', filter_guid, 'due to exception', e)

    def get_last_error(self, max_ret_buff_size: int = _max_return_buff_len) -> str:
        try:
            ctypes_wrapper = self._library.GetLastGraphError
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int, ctypes.c_char_p]
            ret_str = ctypes.create_string_buffer(max_ret_buff_size)

            rc = ctypes_wrapper(max_ret_buff_size, ret_str)

            if rc == 1:
                return str(ret_str.value.decode('ascii'))
            else:
                raise ValueError('rc=', rc)
        except Exception as e:
            raise ValueError('Failed to retrieve MvxGraphCore last error, due to exception:', e)

    def get_graph_state(self) -> GraphState:
        try:
            ctypes_wrapper = self._library.GetGraphState
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.POINTER(ctypes.c_int)]

            return_enum = ctypes.c_int(0)
            rc = ctypes_wrapper(ctypes.byref(return_enum))

            if rc == 1:
                return GraphState(return_enum.value)
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to retrieve graph state, due to exception:', e)

    def create_graph(self):
        try:
            ctypes_wrapper = self._library.CreateGraph
            ctypes_wrapper.restype = ctypes.c_int

            rc = ctypes_wrapper()

            if rc == 1:
                print('Graph object created successfully')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to create graph, due to exception:', e)

    def create_filter_from_guid(self, guid: str, filter_name: str) -> int:
        try:
            ctypes_wrapper = self._library.CreateFilterFromGuid
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]

            filter_instance_id = ctypes.c_int(0)
            rc = ctypes_wrapper(guid.encode('ascii'),
                                filter_name.encode('ascii'),
                                ctypes.byref(filter_instance_id))
            if rc == 1:
                return filter_instance_id.value
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to create MVX filter', filter_name, 'due to exception', e)
            
    def create_filter_from_name(self, filter_name: str) -> int:
        try:
            ctypes_wrapper = self._library.CreateFilterFromName
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]

            filter_instance_id = ctypes.c_int(0)
            rc = ctypes_wrapper(filter_name.encode('ascii'),
                                ctypes.byref(filter_instance_id))
            if rc == 1:
                return filter_instance_id.value
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to create MVX filter', filter_name, 'due to exception', e)

    def destroy_filter(self, filter_instance_id: int):
        try:
            ctypes_wrapper = self._library.DestroyFilter
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int]

            rc = ctypes_wrapper(filter_instance_id)
            if rc == 1:
                return True
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to set destroy MVX filter', 'due to error: ', e)

    def set_filter_parameter(self, filter_instance_id: int, param_name: str, param_value: str):
        try:
            ctypes_wrapper = self._library.SetFilterParameter
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]

            param_value_as_str = str(param_value)

            rc = ctypes_wrapper(filter_instance_id,
                                param_name.encode('ascii'),
                                param_value_as_str.encode('ascii'))
            if rc == 1:
                print('Filter instance ' + str(filter_instance_id) + ':\t' + param_name + '=' + param_value_as_str)
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to set MVX filter parameter:', param_name, 'to', param_value, 'due to error: ', e)

    def get_filter_parameter(self, filter_instance_id: int, param_name: str, max_ret_buff_size: int = _max_return_buff_len) -> str:
        try:
            ctypes_wrapper = self._library.GetFilterParameter
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]

            ret_str = ctypes.create_string_buffer(max_ret_buff_size)
            # TODO - check if not allocated
            rc = ctypes_wrapper(filter_instance_id, param_name.encode(), max_ret_buff_size, ret_str)

            if rc == 1:
                return ret_str.value.decode('ascii')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to get MVX filter parameter', param_name, 'due to exception', e)

    def get_filter_parameters(self, filter_instance_id: int, max_ret_buff_size: int = _max_return_buff_len) -> str:
        try:
            ctypes_wrapper = self._library.GetFilterParameters
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]

            ret_str = ctypes.create_string_buffer(max_ret_buff_size)
            # TODO - check if not allocated
            rc = ctypes_wrapper(filter_instance_id, max_ret_buff_size, ret_str)

            if rc == 1:
                return ret_str.value.decode('ascii')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to get MVX filter parameters, due to exception', e)

    def add_filter_to_graph(self, filter_instance_id: int):
        try:
            ctypes_wrapper = self._library.AddFilterToGraph
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int]

            rc = ctypes_wrapper(filter_instance_id)

            if rc == 1:
                print('Add filter to graph successful')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to add MVX filter to graph due to exception', e)

    def build_graph(self):
        try:
            ctypes_wrapper = self._library.BuildGraph
            ctypes_wrapper.restype = ctypes.c_int

            rc = ctypes_wrapper()

            if rc == 1:
                print('Graph built successfully')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to build MVX graph due to exception', e)

    def graph_source_info(self, max_ret_buff_size: int = _max_return_buff_len) -> str:
        try:
            ctypes_wrapper = self._library.GraphSourceInfo
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int, ctypes.c_char_p]

            ret_str = ctypes.create_string_buffer(max_ret_buff_size)
            # TODO - check if not allocated
            rc = ctypes_wrapper(max_ret_buff_size, ret_str)

            if rc == 1:
                return ret_str.value.decode('ascii')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to get graph source info, due to exception', e)

    def play_graph(self, playback_mode: GraphPlaybackMode):
        try:
            ctypes_wrapper = self._library.PlayGraph
            ctypes_wrapper.restype = ctypes.c_int
            ctypes_wrapper.argtypes = [ctypes.c_int]

            rc = ctypes_wrapper(playback_mode)

            if rc == 1:
                print('Graph play sent')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to Play MVX graph due to exception', e)

    def run_graph(self, playback_mode: GraphPlaybackMode):
        try:
            self.build_graph()
            self.play_graph(playback_mode)
        except Exception as e:
            raise ValueError('Failed to Run MVX graph due to exception', e)

    def stop_graph(self):
        try:
            ctypes_wrapper = self._library.StopGraph
            ctypes_wrapper.restype = ctypes.c_int

            rc = ctypes_wrapper()

            if rc == 1:
                print('Graph stop sent')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to Stop MVX graph due to exception', e)

    def pause_graph(self):
        try:
            ctypes_wrapper = self._library.PauseGraph
            ctypes_wrapper.restype = ctypes.c_int

            rc = ctypes_wrapper()

            if rc == 1:
                print('Graph pause sent')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to Pause MVX graph due to exception', e)

    def resume_graph(self):
        try:
            ctypes_wrapper = self._library.ResumeGraph
            ctypes_wrapper.restype = ctypes.c_int

            rc = ctypes_wrapper()

            if rc == 1:
                print('Graph resume sent')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to Resume MVX graph due to exception', e)


    def destroy_graph(self):
        try:
            ctypes_wrapper = self._library.DestroyGraph
            ctypes_wrapper.restype = ctypes.c_int

            rc = ctypes_wrapper()

            if rc == 1:
                print('Graph destroy sent')
            else:
                raise ValueError(self.get_last_error())
        except Exception as e:
            raise ValueError('Failed to Destroy MVX graph due to exception', e)


# if __name__ == "__main__":
#     MyWrapper = MvxGraphCoreWrapper("C:\\xx")

#     sys.exit(0)

