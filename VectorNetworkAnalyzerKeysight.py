#!/usr/bin/env python3.8

###############################################################################
# Description: Performance DL Automation Framework
#
# Copyright (c) 2021 Dell Technologies, all rights reserved.
# This material is Confidential and shall not be disclosed
# to a third party without the written consent.
#
# Author: Jin Her
###############################################################################

"""

"""

import os
import sys
import skrf
from decimal import Decimal
from typing import Union
from framework.drivers.SSHDriver import SSHDriver
import logging
logger = logging.getLogger("RobotFramework")

sys.path.append(os.getcwd())

class InvalidPortTypeException(Exception):
    "Raised when the type of VNA Ports is not a list of integers."
    pass


class InvalidPortNumberException(Exception):
    "Raised when the number of VNA Ports are not between 1 to 4."
    pass


class VectorNetworkAnalyzerKeysight(object):
    """! Keysight Vector Network Analyzer Class
    
    """

    # TODO: migrate some functions to TxBandReturnLoss Class

    def __init__(self, vna_session=None, vna_vendor='', vna_model=''):
        """! Init
        @return None
        """
        self.session = vna_session
        self.vendor = vna_vendor
        self.model = vna_model
        
    def __del__(self):
        """! Del
        @return None
        """

    def write_opc(self, command, timeout=30):
        """! Write with integrated synchronization command for remote operation

        """
        timeout_original = self.session.timeout # save original timeout value
        self.session.timeout = timeout*1000    # set timeout value to 30 seconds
        completed = self.session.write(f"{command};*OPC?")
        self.session.timeout = timeout_original # restore original timeout value
        if completed:
            return True
        else:
            raise TimeoutError

    def query_opc(self, command, sec=3):
        """!

        """
        opc = 0
        timeout_original = self.session.timeout # save original timeout value
        self.session.timeout = 30000    # set timeout value to 30 seconds
        opc = self.session.query('*OPC?')
        opc = int(opc[0])
        self.session.timeout = timeout_original # restore original timeout value
        if opc == 1:
            value = self.session.query(f"{command}")
        return value
    
    def __throw_if_invalid_ports(self, vna_ports):
        if not all(isinstance(port, int) for port in vna_ports):
            raise InvalidPortTypeException("Port Type must be a list of integers.")
        if not all(1 <= port <= 4 for port in vna_ports):
            raise InvalidPortNumberException("Port Numbers must be between 1 to 4.")

    def ports_list_to_string(self, vna_ports):
        vna_ports.sort()
        return str(vna_ports)[1:-1].replace(', ', ',')
    
    def initialize_display(self):
        """!

        """
        self.write_opc("CALC:MEAS:DEL:ALL")
        self.write_opc("DISP:WIND:STATE ON")

    def set_ports_to_be_calibrated(self, vna_ports: list[int]):
        """!
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        """
        self.__throw_if_invalid_ports(vna_ports)

        ports = self.ports_list_to_string(vna_ports)
        self.write_opc(f"SYST:CAL:ALL:CHAN:PORT {ports}")

    def set_frequency_range(self, start_frequency, stop_frequency, step_frequency):
        """!

        """
        self.write_opc(f"SENS:FREQ:STAR {start_frequency}")
        self.write_opc(f"SENS:FREQ:STOP {stop_frequency}")
        self.write_opc(f"SENS:SWE:STEP {step_frequency}")

    def set_reference_power_level(self, reference_power_level, vna_ports: list[int]):
        """!
        @param reference_power_level Source Power in dBm.
        @param vna_ports 1-based indexing.
        """
        self.__throw_if_invalid_ports(vna_ports)

        for port in vna_ports:
            self.write_opc(f"SOUR:POW{port} {reference_power_level}")

    def set_and_display_traces(self, vna_ports: list[int], s_parameter: str):
        """!
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        """
        self.__throw_if_invalid_ports(vna_ports)

        n = len(vna_ports)
        mnum = 0
        if s_parameter == 'ALL':
            for i in range(1, n+1):
                for j in range(1, n+1):
                    mnum += 1
                    self.write_opc(f"CALC:MEAS{mnum}:DEF 'S{i}{j}'")
                    self.write_opc(f"DISP:MEAS{mnum}:FEED 1")
        else:
            self.write_opc(f"CALC:MEAS:DEF '{s_parameter}'")
            self.write_opc(f"DISP:MEAS:FEED 1")

    def save_screen(self, stem_of_file_name):
        """!
        
        """
        screenshot_file_name = f"{stem_of_file_name}.png"

        self.write_opc("DISP:TOOL:KEYS OFF")
        self.write_opc("DISP:TOOL:ENTR OFF")

        self.write_opc("MMEM:CDIR 'D:/downlink'")
        self.write_opc(f"MMEM:STOR '{screenshot_file_name}'")

        return screenshot_file_name

    def save_traces(self, vna_ports: list[int], s_parameter: str, stem_of_file_name):
        """!
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        """
        self.__throw_if_invalid_ports(vna_ports)

        snum = len(vna_ports)
        if s_parameter != 'ALL':
            snum = s_parameter[1:-1] 
        snp_file_name = f"{stem_of_file_name}.s{snum}p"

        self.write_opc("MMEM:CDIR 'D:/downlink'")
        self.write_opc(f"MMEM:STOR '{snp_file_name}'")

        return snp_file_name

    def copy_file_to_local(self, file_name):
        """!

        """
        pass


if __name__ == "__main__":
    """!
    
    """