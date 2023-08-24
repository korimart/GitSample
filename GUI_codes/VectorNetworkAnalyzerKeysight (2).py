"""
date: 2023-03-15
last update: 2023-08-22
author: Jin Her
"""

from E2E_local_data import InstConfig
import os
import pathlib
import shutil
import matplotlib.pyplot as plt
import skrf
import itertools
# import numpy as np
import logging
logger = logging.getLogger("Automation_Logger")


class InvalidPortTypeException(Exception):
    "Raised when the type of VNA Ports is not a list of integers."
    pass


class InvalidPortNumberException(Exception):
    "Raised when the number of VNA Ports are not between 1 to 4."
    pass


class InvalidTraceTypeException(Exception):
    """Raised when the type of trace number is not an integer."""
    pass


class InvalidTraceNumberException(Exception):
    """Raised when the number of Trace number is not between 1 to 16."""
    pass



class VectorNetworkAnalyzerKeysight(object):
    """

    """

    def __init__(self, vna_session=None, vna_vendor='', vna_model='', bench_ip_address=''):
        """

        """
        self.session = vna_session
        self.vendor = vna_vendor
        self.model = vna_model
        self.bench_ip = bench_ip_address

        self.trace_number = 0
    
    def __throw_if_invalid_ports(self, vna_ports):
        if not all(isinstance(port, int) for port in vna_ports):
            raise InvalidPortTypeException("Port Type must be a list of integers.")
        if not all(1 <= port <= 4 for port in vna_ports):
            raise InvalidPortNumberException("Port Numbers must be between 1 to 4.") 
        
    def __throw_if_invalid_trace(self, trace_number):
        if not isinstance(trace_number, int):
            raise InvalidTraceTypeException("Trace type must be an integer.")
        if not 1 <= trace_number <= 16:
            raise InvalidTraceNumberException("Trace number must be between 1 to 16.")

    def __port_list_to_string(self, vna_ports: list[int]):
        """
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        """
        self.__throw_if_invalid_ports(vna_ports)

        vna_ports.sort()
        return str(vna_ports)[1:-1].replace(', ', ',')

    def __get_available_trace_number(self) -> int:
        self.trace_number += 1
        return self.trace_number

    def query_opc(self) -> bool:
        if self.session.query("*OPC?") == "+1":
            return True
        else:
            return False
    
    def initialize_display(self):
        self.session.write("CALC:MEAS:DEL:ALL")
        self.session.write("DISP:WIND:STATE ON")
        self.trace_number = 0
    
    def preset(self):
        """ 
        Deletes all traces, measurements, and windows. Creates a S11 measurement.
        """
        self.session.write("SYST:PRES")

    def set_ports_to_be_calibrated(self, vna_ports: list[int]):
        """
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        """
        ports = self.__port_list_to_string(vna_ports)
        self.session.write(f"SYST:CAL:ALL:CHAN:PORT {ports}")

    def set_frequency_range(self, start, stop, step):
        self.session.write(f"SENS:FREQ:STAR {start}")
        self.session.write(f"SENS:FREQ:STOP {stop}")
        self.session.write(f"SENS:SWE:STEP {step}")

    def set_smoothing_on(self, on: bool):
        if on:
            self.session.write("CALC:MEAS:SMO ON")
        else:
            self.session.write("CALC:MEAS:SMO OFF")

    def set_smoothing_percentage(self, percentage):
        self.session.write(f"CALC:MEAS:SMO:APER {percentage}")

    def set_and_display_trace(self, s_parameter: str):
        """
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44'
        """
        trace_num = self.__get_available_trace_number()
        self.__throw_if_invalid_trace(trace_num)

        self.session.write(f"CALC:MEAS:DEF '{s_parameter}'")
        self.session.write(f"DISP:MEAS{trace_num}:FEED 1")

    def set_and_display_all_traces(self, vna_ports: list[int]):
        """
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        """
        self.__throw_if_invalid_ports(vna_ports)
        
        n = len(vna_ports)
        try:
            for i, j in itertools.product(range(1, n+1), range(1, n+1)):
                trace_num = self.__get_available_trace_number()
                self.__throw_if_invalid_trace(trace_num)
                self.session.write(f"CALC:MEAS{trace_num}:DEF 'S{i}{j}'")
                self.session.write(f"DISP:MEAS{trace_num}:FEED 1")
        except InvalidTraceNumberException:
            self.initialize_display()
            for i, j in itertools.product(range(1, n+1), range(1, n+1)):
                trace_num = self.__get_available_trace_number()
                self.session.write(f"CALC:MEAS{trace_num}:DEF 'S{i}{j}'")
                self.session.write(f"DISP:MEAS{trace_num}:FEED 1")

    def set_and_display_group_delay(self, s_parameter: str):
        """
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44'
        """
        try:
            trace_num = self.__get_available_trace_number()
            self.__throw_if_invalid_trace(trace_num)

            self.session.write(f"CALC:MEAS{trace_num}:DEF '{s_parameter}'") 
            self.session.write(f"DISP:MEAS{trace_num}:FEED 1")
            self.session.write(f"CALC:PAR:MNUM {trace_num}")
            self.session.write(f"CALC:MEAS{trace_num}:FORM GDEL") 
        except InvalidTraceNumberException:
            self.initialize_display()
            self.session.write(f"CALC:MEAS{self.trace_number}:DEF '{s_parameter}'") 
            self.session.write(f"DISP:MEAS{self.trace_number}:FEED 1")
            self.session.write(f"CALC:PAR:MNUM {self.trace_number}")
            self.session.write(f"CALC:MEAS{self.trace_number}:FORM GDEL") 

    def measure_ecal(self, vna_ports: list[int], calibration_method: str):
        """
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        @calibration_method 'SOLT', 'SOLR', and 'ERES'. 
        'SOLT': used to accurately calibrate any number of ports.
        'SOLR': used to accurately calibrate any two ports.
        'ERES': used to calibrate two ports when only measurements in one direction (forward/reverse) are required.
        """
        self.__throw_if_invalid_ports(vna_ports)

        ports = self.__port_list_to_string(vna_ports)
        self.session.write(f"SENS:CORR:COLL:GUID:ECAL:ACQ {calibration_method}, {ports}")
        self.session.timeout = 90000

        return self.query_opc()

    def save_traces_as_snp_file(self, vna_ports: list[int], stem_of_file_name):
        """
        Saves traces in .snp format. Can't save the group delay.
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        """
        self.__throw_if_invalid_ports(vna_ports)


        n = len(vna_ports)
        snp_file_name = f"{stem_of_file_name}.s{n}p"
        self.session.write("MMEM:CDIR '/pathloss'")
        self.session.write(f"MMEM:STOR '{snp_file_name}'")

        return snp_file_name

    def save_traces_as_csv_file(self, stem_of_base_name):
        """
        Saves traces in .csv format. Can save the group delay.
        """
        csv_file_name = f'{stem_of_base_name}.csv'
        self.session.write("MMEM:CDIR '/pathloss'")
        self.session.write(f"MMEM:STOR:DATA '{csv_file_name}', 'CSV Formatted Data', 'Displayed', 'Displayed', -1")

        return csv_file_name

    def plot_from_snp_file(self, snp_file_path: str):
        # TODO: group delay?
        nw = skrf.Network(snp_file_path)
        nw.plot_s_db()

        plt.show()

    def copy_file_to_local(self, file_name):
        """
        returns local path of where file is copied
        """
        visaAddrs = InstConfig.sysConfigDict.get(self.bench_ip).get('Network_Analyzer')
        vna_ip = visaAddrs.split("::")
        destination_folder = pathlib.Path(__file__).parent.parent / 'E2E_local_data' / 'pathloss'

        os.system(rf"NET USE P: \\{vna_ip[1]}\pathloss " + rf"/u:Instrument Keysight4u!")
        shutil.copyfile(rf"P:{file_name}", rf"{destination_folder}\{file_name}")
        os.system(rf"NET USE P: /DELETE")
        local_path = os.path.join(destination_folder, file_name)
        return local_path
