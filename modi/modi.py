"""Main MODI module."""

import os
import time
import traceback

import threading as th
import multiprocessing as mp

from typing import Tuple

from modi._conn_proc import ConnProc
from modi._exe_thrd import ExeThrd

from modi.module.module import Module

from modi.util.topology_manager import TopologyManager
from modi.util.firmware_updater import FirmwareUpdater
from modi.util.stranger import check_complete
from modi.util.misc import module_list


class MODI:
    """
    Example:
    >>> import modi
    >>> bundle = modi.MODI()
    """

    def __init__(self, nb_modules: int = 1, conn_mode: str = "serial",
                 module_uuid: str = "", test: bool = False,
                 verbose: bool = False):

        self._modules = list()

        self._module_ids = dict()
        self._topology_data = dict()

        self._recv_q = mp.Queue()
        self._send_q = mp.Queue()

        self._conn_proc = None
        self._exe_thrd = None

        # Init flag used to notify initialization of MODI modules
        module_init_flag = th.Event()

        # If in test run, do not create process and thread
        if test:
            return

        init_flag = mp.Event()

        self._conn_proc = ConnProc(
            self._recv_q, self._send_q, conn_mode, module_uuid, verbose,
            init_flag
        )
        self._conn_proc.daemon = True
        try:
            self._conn_proc.start()
        except RuntimeError:
            if os.name == 'nt':
                print('\nProcess initialization failed!\nMake sure you are '
                      'using\n    if __name__ == \'__main__\' \n '
                      'in the main module.')
            else:
                traceback.print_exc()
            exit(1)

        self._child_watch = th.Thread(target=self.watch_child_process)
        self._child_watch.daemon = True
        self._child_watch.start()

        init_flag.wait()

        self._firmware_updater = FirmwareUpdater(
            self._send_q, self._module_ids, nb_modules
        )

        init_flag = th.Event()

        self._exe_thrd = ExeThrd(
            self._modules,
            self._module_ids,
            self._topology_data,
            self._recv_q,
            self._send_q,
            module_init_flag,
            nb_modules,
            self._firmware_updater,
            init_flag
        )
        self._exe_thrd.daemon = True
        self._exe_thrd.start()

        init_flag.wait()

        self._topology_manager = TopologyManager(self._topology_data)

        # module_init_flag.wait()
        # if not module_init_flag.is_set():
        #     raise Exception("Modules are not initialized properly!")
        #     exit(1)
        # print("MODI modules are initialized!")
        check_complete(self)

    def update_module_firmware(self) -> None:
        """Updates firmware of connected modules"""
        print("Request to update firmware of connected MODI modules.")
        self._firmware_updater.reset_state()
        self._firmware_updater.request_to_update_firmware()
        # self.firmware_updater.update_event.wait()
        print("Module firmwares have been updated!")

    def watch_child_process(self) -> None:
        while self._conn_proc.is_alive():
            time.sleep(0.1)
        os._exit(1)

    def print_topology_map(self, print_id: bool = False) -> None:
        """Prints out the topology map

        :param print_id: if True, the result includes module id
        :return: None
        """
        self._topology_manager.print_topology_map(print_id)

    @property
    def modules(self) -> Tuple[Module]:
        """Tuple of connected modules except network module.
        Example:
        >>> bundle = modi.MODI()
        >>> modules = bundle.modules
        """
        return tuple(self._modules)

    @property
    def buttons(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.button.Button` modules.
        """
        return module_list(self._modules, 'button')

    @property
    def dials(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.dial.Dial` modules.
        """

        return module_list(self._modules, "dial")

    @property
    def displays(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.display.Display` modules.
        """

        return module_list(self._modules, "display")

    @property
    def envs(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.env.Env` modules.
        """

        return module_list(self._modules, "env")

    @property
    def gyros(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.gyro.Gyro` modules.
        """

        return module_list(self._modules, "gyro")

    @property
    def irs(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.ir.Ir` modules.
        """

        return module_list(self._modules, "ir")

    @property
    def leds(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.led.Led` modules.
        """

        return module_list(self._modules, "led")

    @property
    def mics(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.mic.Mic` modules.
        """

        return module_list(self._modules, "mic")

    @property
    def motors(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.motor.Motor` modules.
        """

        return module_list(self._modules, "motor")

    @property
    def speakers(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.speaker.Speaker` modules.
        """

        return module_list(self._modules, "speaker")

    @property
    def ultrasonics(self) -> Tuple[Module]:
        """Tuple of connected :class:`~modi.module.ultrasonic.Ultrasonic` modules.
        """

        return module_list(self._modules, "ultrasonic")
