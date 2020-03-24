import time
import queue
import serial

from serial import SerialException

from modi._communicator_task import CommunicatorTask


class SerTask(CommunicatorTask):

    def __init__(self, ser_read_q, ser_write_q):
        super().__init__(ser_read_q, ser_write_q)
        self._ser_read_q = ser_read_q
        self._ser_write_q = ser_write_q

        self.__ser = self._open_conn()
        self.__json_buffer = ""

    def __del__(self):
        self._close_conn()

    #
    # Inherited Methods
    #
    def _open_conn(self):
        """ Open serial port
        """

        modi_ports = self._list_modi_ports()
        if not modi_ports:
            raise SerialException("No MODI network module is connected.")

        # TODO: Refactor code to support multiple MODI network modules here
        modi_port = modi_ports.pop()
        ser = serial.Serial()
        ser.baudrate = 921600
        ser.port = modi_port.device

        # Check if the modi port(i.e. MODI network module) is in use
        if ser.is_open:
            raise SerialException(
                "The MODI port {} is already in use".format(ser.port)
            )
        ser.open()
        return ser

    def _close_conn(self):
        """ Close serial port
        """

        self.__ser.close()

    def _read_data(self):
        """ Read serial message and put message to serial read queue
        """

        serial_buffer = self.__ser.in_waiting
        if serial_buffer:
            # Flush the serial buffer and concatenate it to json buffer
            self.__json_buffer += self.__ser.read(
                serial_buffer
            ).decode("utf-8")

            # Once json buffer is obtained, we parse and send json message
            self.__parse_serial()

    def _write_data(self):
        """ Write serial message in serial write queue
        """

        try:
            message_to_write = self._ser_write_q.get_nowait().encode()
        except queue.Empty:
            pass
        else:
            self.__ser.write(message_to_write)

    def run_read_data(self, delay):
        while 1:
            self._read_data()
            time.sleep(delay)

    def run_write_data(self, delay):
        while 1:
            self._write_data()
            time.sleep(delay)

    #
    # Helper method
    #
    def __parse_serial(self):
        # While there is a valid json in the json buffer
        while "{" in self.__json_buffer and "}" in self.__json_buffer:
            split_index = self.__json_buffer.find("}") + 1

            # Parse json message and send it
            json_msg = self.__json_buffer[:split_index]
            self._ser_read_q.put(json_msg)

            # Update json buffer, remove the json message sent
            self.__json_buffer = self.__json_buffer[split_index:]