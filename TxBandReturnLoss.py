# from framework.instruments import Inst
import os
import sys
import skrf
from decimal import Decimal
from typing import Union
# from framework.drivers.SSHDriver import SSHDriver
import logging
# logger = logging.getLogger("RobotFramework")

# sys.path.append(os.getcwd())


class InvalidReflectionUseException(Exception):
    """Raised when the reflection is enabled but S parameter is not set to 'ALL'"""
    pass


class InvalidSparameterException(Exception):
    """Raised when the S parameter given is out of range based on the VNA Ports chosen."""
    pass


class TxBandReturnLoss(object):
    def __init__(self, snp_file_path, vna_ports, maximum_allowable_return_loss):
        # self.inst = Inst()
        # self.inst.connect_all_instruments()

        self.snp_file_path = snp_file_path
        self.vna_ports = vna_ports
        self.max_loss = maximum_allowable_return_loss

        self.network = skrf.Network(self.snp_file_path)
    
    def __throw_if_invalid_reflection_use(self, s_parameter, reflection):
        if reflection and s_parameter != 'ALL':
            raise InvalidReflectionUseException("S parameter must be set to 'ALL' to enable reflection.")

    def __throw_if_invalid_s_parameter(self, vna_ports, s_parameter):
        if s_parameter == 'ALL':
            pass
        elif type(s_parameter) == list:
            for s_param in s_parameter:
                if int(s_param[1]) not in vna_ports:
                    raise InvalidSparameterException("S parameter should be within the range of selected VNA Ports.")
        else:
            if int(s_parameter[1]) not in vna_ports:
                raise InvalidSparameterException("S parameter should be within the range of selected VNA Ports.")

    def configure_settings(self, start_frequency, stop_frequency, step_frequency, reference_power_level, vna_ports: list[int], s_parameter):
        """!
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        """
        self.inst.vna.vnaInstance.initialize_display()
        self.inst.vna.vnaInstance.set_ports_to_be_calibrated(vna_ports)
        self.inst.vna.vnaInstance.set_frequency_range(start_frequency, stop_frequency, step_frequency)
        self.inst.vna.vnaInstance.set_reference_power_level(reference_power_level, vna_ports)
        self.inst.vna.vnaInstance.set_and_display_traces(vna_ports, s_parameter)

    def get_test_results_from_snp_file(self, snp_file_path: str, s_parameter: Union[str, list[str]], reflection=False) -> list[dict]:
        """!
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        @param reflection Set to True with s_parameter to 'ALL'
        @return test_results A list of dictionaries containing frequencies and measurement values.
        """
        self.__throw_if_invalid_reflection_use(s_parameter, reflection)

        test_results = []
        network = skrf.Network(snp_file_path)
        if s_parameter == 'ALL':
            n = network.number_of_ports
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

    # def check_and_log_return_loss_pass_fail(self, s_parameter, frequency, return_loss, maximum_allowable_return_loss):
    #     if not (-return_loss) < maximum_allowable_return_loss:
    #         logger.info(f"Test Failed at S-PARAMETER: {s_parameter}, FREQUENCY: {'%.3E'%Decimal(frequency)},  RETURN LOSS: {round(-return_loss, 4)}, OFFSET: {round(-return_loss-maximum_allowable_return_loss, 4)}")

    def perform_calibration_test(self):
        """!

        """
        # TODO: Assume E calibration is already done. 
        # TODO: 1. Configure Radio (leave as empty for now)
        # TODO: 2. Read feedback power (verify no output power). Wait for input if no output power (time to connect to the VNA)
        # TODO: 3. Connect Radio to the VNA and start measuring measurements.
        pass   

    def perform_return_loss_pass_fail_test(self, snp_file_path: str, vna_ports: list[int], s_parameter: Union[str, list[str]], reflection: bool, maximum_allowable_return_loss):
        """!
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        @param reflection Set to True with s_parameter to 'ALL'
        """
        self.__throw_if_invalid_s_parameter(vna_ports, s_parameter)

        test_results = self.get_test_results_from_snp_file(snp_file_path, s_parameter, reflection)
        for result in test_results:
            for s_param, measurements in result.items():
                for frequency, return_loss in measurements.items():
                    self.check_and_log_return_loss_pass_fail(s_param, frequency, return_loss, maximum_allowable_return_loss)

    def perform_tx_band_return_loss_test(self, start_frequency, stop_frequency, step_frequency, reference_power_level, vna_ports: list[int], s_parameter: Union[str, list[str]], reflection: bool, stem_of_file_name, maximum_allowable_return_loss):
        """!
        @param vna_ports 1-based indexing. Port numbers between 1 to 4.
        @param s_parameter 'S11', 'S12', ..., 'S21', ..., 'S44', and 'ALL' for all S parameters based on the number of VNA ports being used.
        @param reflection Set to True with s_parameter to 'ALL'
        """
        self.configure_settings(start_frequency, stop_frequency, step_frequency, reference_power_level, vna_ports, s_parameter)       
        self.perform_calibration_test()

        saved_screenshot_file_name = self.inst.vna.vnaInstance.save_screen(stem_of_file_name)
        saved_traces_file_name = self.inst.vna.vnaInstance.save_traces(vna_ports, s_parameter, stem_of_file_name)

        saved_screenshot_file_path = self.inst.vna.vnaInstance.copy_file_to_local(saved_screenshot_file_name)
        saved_traces_file_path = self.inst.vna.vnaInstance.copy_file_to_local(saved_traces_file_name)

        self.perform_return_loss_pass_fail_test(saved_traces_file_path, vna_ports, s_parameter, reflection, maximum_allowable_return_loss)

    def get_single_measurement_results(self, s_parameter: str):
        matrix_indices = [int(value)-1 for value in s_parameter.replace('S', '').replace('',  ' ').split()]
        measurements = self.network.s_db[:, matrix_indices[0], matrix_indices[1]]

        return [{f'{s_parameter}': {frequency: measurements[i]}} for i, frequency in enumerate(self.network.f)]

    def get_multiple_measurement_results(self, s_parameter: list[str]):
        matrix_indices = [[int(value)-1 for value in s_param.replace('S', '').replace('',  ' ').split()] for s_param in s_parameter]
        measurements = [self.network.s_db[:, indices[0], indices[1]] for indices in matrix_indices]

        return [{f'{s_param}': {frequency: measurements[i][j]}} for i, s_param in enumerate(s_parameter) for j, frequency in enumerate(self.network.f)]
    
    def get_all_measurement_results(self):
        n = self.network.number_of_ports
        all_s_parameters = [f'S{i}{j}' for i in range(1, n+1) for j in range(1, n+1)]
        measurements = [self.network.s_db[:, i, j] for i in range(n) for j in range(n)]

        return [{f'{s_param}': {frequency: measurements[i][j]}} for i, s_param in enumerate(all_s_parameters) for j, frequency in enumerate(self.network.f)]

    def get_all_reflection_results(self):
        n = self.network.number_of_ports
        reflection_parameters = [f'S{i}{i}' for i in range(1, n+1)]
        measurements = [self.network.s_db[:, i, i] for i in range(n)]

        return [{f'{s_param}': {frequency: measurements[i][j]}} for i, s_param in enumerate(reflection_parameters) for j, frequency in enumerate(self.network.f)]

    def get_all_forward_results(self):
        pass

    def get_all_reverse_results(self):
        n = self.network.number_of_ports
        pass

    def check_and_log_return_loss_pass_fail(self, test_result):
        for result in test_result:
            for s_parameter, measurements in result.items():
                for frequency, return_loss in measurements.items():
                    if not (-return_loss) < self.max_loss:
                        print(f"Test Failed at S-PARAMETER: {s_parameter}, FREQUENCY: {'%.3E'%Decimal(frequency)},  RETURN LOSS: {round(-return_loss, 4)}, OFFSET: {round(-return_loss-self.max_loss, 4)}")


if __name__ == '__main__':
    # snp_file_path = r'c:\Users\Jin_Her\OneDrive - Dell Technologies\Desktop\RFCB3\Port0_PM_2023Jun14.s2p'
    snp_file_path = r'c:\Users\Jin_Her\OneDrive - Dell Technologies\Desktop\RFCB3\Port4_PM_SA_2023Jul12.s3p'
    vna_ports = [1, 2, 3]
    maximum_allowable_return_loss = 45

    test = TxBandReturnLoss(snp_file_path, vna_ports, maximum_allowable_return_loss)

    # result_single = test.get_single_measurement_results('S11')
    # result_mutiple = test.get_multiple_measurement_results(['S11', 'S21'])
    # result_reflection = test.get_all_reflection_results()
    # result_all = test.get_all_measurement_results()
    # result_forward = test.get_all_forward_results()
    result_reverse = test.get_all_reverse_results()

    # test.check_and_log_return_loss_pass_fail(result_reverse)