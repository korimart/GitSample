# from framework.instruments import Inst
from dataclasses import dataclass
import os
import sys
import skrf
from decimal import Decimal
from typing import Union
# from framework.drivers.SSHDriver import SSHDriver
import logging
import itertools
# logger = logging.getLogger("RobotFramework")

# sys.path.append(os.getcwd())


class InvalidReflectionUseException(Exception):
    """Raised when the reflection is enabled but S parameter is not set to 'ALL'"""
    pass


class InvalidSparameterException(Exception):
    """Raised when the S parameter given is out of range based on the VNA Ports chosen."""
    pass


@dataclass
class Measurement:
    s_param: str
    frequency: float
    value: float


class SNPFileReader:
    def __init__(self, snp_file_path):
        pass

    def get_measurement(self, s_param, frequency) -> Measurement:
        pass

    def get_measurements_from_s_param(self, s_parameter: str) -> list[Measurement]:
        pass

    def get_all_measurements(self):
        pass

    def get_all_reflection_measurements(self):
        pass

    def get_all_forward_measurements(self):
        pass

    def get_all_reverse_measurements(self) -> dict[str, list[Measurement]]:
        pass


def log_return_loss_fails(max_loss: float, measurements: list[Measurement]):
    for each in measurements:
        if not (-each.value) < max_loss:
            print(f"Test Failed at S-PARAMETER: {each.s_param}, FREQUENCY: {'%.3E'%Decimal(each.frequency)},  RETURN LOSS: {round(-each.value, 4)}, OFFSET: {round(-each.value-max_loss, 4)}")


if __name__ == '__main__':
    # snp_file_path = r'c:\Users\Jin_Her\OneDrive - Dell Technologies\Desktop\RFCB3\Port0_PM_2023Jun14.s2p'
    snp_file_path = r'c:\Users\Jin_Her\OneDrive - Dell Technologies\Desktop\RFCB3\Port4_PM_SA_2023Jul12.s3p'
    vna_ports = [1, 2, 3]
    maximum_allowable_return_loss = 45

    vna = None
    start_frequency = None
    stop_frequency = None
    step_frequency = None
    reference_power_level = None
    s_parameter = None
    stem_of_file_name = None
    vna.vnaInstance.initialize_display()
    vna.vnaInstance.set_ports_to_be_calibrated(vna_ports)
    vna.vnaInstance.set_frequency_range(start_frequency, stop_frequency, step_frequency)
    vna.vnaInstance.set_reference_power_level(reference_power_level, vna_ports)
    vna.vnaInstance.set_and_display_traces(vna_ports, s_parameter)
    saved_screenshot_file_path = vna.vnaInstance.copy_file_to_local(vna.vnaInstance.save_screen(stem_of_file_name))
    saved_traces_file_path = vna.vnaInstance.copy_file_to_local(vna.vnaInstance.save_traces(vna_ports, s_parameter, stem_of_file_name))

    reader = SNPFileReader(saved_traces_file_path)

    for _, measurements in reader.get_all_reverse_measurements():
        log_return_loss_fails(max_loss, measurements)