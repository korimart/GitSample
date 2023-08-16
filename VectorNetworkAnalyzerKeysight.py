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


class InvalidReflectionUseException(Exception):
    """Raised when the reflection is enabled but S parameter is not set to 'ALL'"""
    pass


class InvalidSnpFileException(Exception):
    """Raised when the SNP file format does not match with number of VNA Ports chosen."""
    pass


class VectorNetworkAnalyzerKeysight(object):
    """! Keysight Vector Network Analyzer Class
    
    """

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
    
    def __throw_if_invalid_reflection_use(self, s_parameter, reflection):
        if reflection and s_parameter != 'ALL':
            raise InvalidReflectionUseException("S parameter must be set to 'ALL' to enable reflection.")

    def __throw_if_invalid_snp_file(self, snp_file_path, vna_ports):
        n = len(vna_ports)
        base_name =os.path.basename(snp_file_path)
        if f'.s{n}p' not in base_name:
            raise InvalidSnpFileException("File format must match with the number of VNA Ports used.")

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

    def configure_settings(self, start_frequency, stop_frequency, step_frequency, reference_power_level, vna_ports: list[int], s_parameter):
        """!
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        """
        self.initialize_display()
        self.set_ports_to_be_calibrated(vna_ports)
        self.set_frequency_range(start_frequency, stop_frequency, step_frequency)
        self.set_reference_power_level(reference_power_level, vna_ports)
        self.set_and_display_traces(vna_ports, s_parameter)

    def initiate_measurement(self):
        """!

        """
        pass   

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

    # FIXME: can a type hint be list[dict: dict]?
    # TODO: Refactor
    def get_test_results_from_snp_file(self, snp_file_path: str, vna_ports: list[int], s_parameter: Union[str, list[str]], reflection=False) -> list[dict]:
        """!
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        @param reflection Set to True with s_parameter to 'ALL'
        """
        self.__throw_if_invalid_ports(vna_ports)
        # FIXME: should this code only be in this function only?
        self.__throw_if_invalid_reflection_use(s_parameter, reflection)

        test_results = []
        network = skrf.Network(snp_file_path)
        if s_parameter == 'ALL':
            n = len(vna_ports)
            if reflection:
                s_params = [f'S{i}{i}' for i in range(1, n+1)]
                measurements = [network.s_db[:, i, i] for i in range(n)]
            else:
                s_params = [f'S{i}{j}' for i in range(1, n+1) for j in range(1, n+1)]
                measurements = [network.s_db[:, i, j] for i in range(n) for j in range(n)]
            for i, param in enumerate(s_params):
                for j, frequency in enumerate(network.f):
                    test_results.append({f'{param}': {frequency: measurements[i][j]}})
        elif type(s_parameter) == list:
            s_param_matrix_indices = [[int(value)-1 for value in s_param.replace('S', '').replace('',  ' ').split()] for s_param in s_parameter]
            measurements = [network.s_db[:, indices[0], indices[1]] for indices in s_param_matrix_indices]
            for i, s_param in enumerate(s_parameter):
                for j, frequency in enumerate(network.f):
                    test_results.append({f'{s_param}': {frequency: measurements[i][j]}})
        else:
            s_param_matrix_index = [int(value)-1 for value in s_parameter.replace('S', '').replace('',  ' ').split()]
            measurements = [network.s_db[:, s_param_matrix_index[0], s_param_matrix_index[1]]]
            for i, frequency in enumerate(network.f):
                test_results.append({f'{s_parameter}': {frequency: measurements[0][i]}})

        return test_results

    def log_tx_band_return_loss_pass_fail(self, snp_file_path: str, vna_ports: list[int], s_parameter: Union[str, list[str]], reflection: bool, maximum_allowable_return_loss):
        """!
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        @param reflection Set to True with s_parameter to 'ALL'
        """
        # TODO: refactor
        self.__throw_if_invalid_snp_file(snp_file_path, vna_ports)

        test_results = self.test_get_test_results(snp_file_path, vna_ports, s_parameter, reflection)
        for result in test_results:
            for s_param, measurements in result.items():
                for frequency, return_loss in measurements.items():
                    if not (-return_loss) < maximum_allowable_return_loss:
                        logger.info(f"Test Failed at S-PARAMETER: {s_param}, FREQUENCY: {'%.3E'%Decimal(frequency)},  RETURN LOSS: {round(-return_loss, 4)}, OFFSET: {round(-return_loss-maximum_allowable_return_loss, 4)}")

    def perform_calibration_for_tx_band_return_loss(self, start_frequency, stop_frequency, step_frequency, reference_power_level, vna_ports: list[int], s_parameter: Union[str, list[str]], reflection: bool, stem_of_file_name, maximum_allowable_return_loss):
        """!
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        @param reflection Set to True with s_parameter to 'ALL'
        """
        self.configure_settings(start_frequency, stop_frequency, step_frequency, reference_power_level, vna_ports, s_parameter)       
        self.initiate_measurement()

        saved_screenshot_file_name = self.save_screen(stem_of_file_name)
        saved_traces_file_name = self.save_traces(vna_ports, s_parameter, stem_of_file_name)

        saved_screenshot_file_path = self.copy_file_to_local(saved_screenshot_file_name)
        saved_traces_file_path = self.copy_file_to_local(saved_traces_file_name)

        self.log_tx_band_return_loss_pass_fail(saved_traces_file_path, vna_ports, s_parameter, reflection, maximum_allowable_return_loss)


if __name__ == "__main__":
    """!
    
    """