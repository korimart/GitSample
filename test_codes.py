import skrf
from decimal import Decimal
from typing import Union
import os


two_port_file_path = r'c:\Users\Jin_Her\OneDrive - Dell Technologies\Desktop\RFCB3\Port0_PM_2023Jun14.s2p'
three_port_file_path = r'c:\Users\Jin_Her\OneDrive - Dell Technologies\Desktop\RFCB3\Port4_PM_SA_2023Jul12.s3p'
# network.s_db[:, 0, 0] matrix order --> [S11 S12 S21 S22]

class InvalidReflectionUseException(Exception):
    """Raised when the reflection is enabled but S parameter is not set to 'ALL'"""
    pass


class InvalidSparameterException(Exception):
    """Raised when the S parameter given is out of range based on the VNA Ports chosen."""
    pass

def __throw_if_invalid_reflection_use(s_parameter, reflection):
    if reflection and s_parameter != 'ALL':
        raise InvalidReflectionUseException("S parameter must be set to 'ALL' to enable reflection.")

def __throw_if_invalid_s_parameter(vna_ports, s_parameter):
    if s_parameter == 'ALL':
        pass
    elif type(s_parameter) == list:
        for s_param in s_parameter:
            if int(s_param[1]) not in vna_ports:
                raise InvalidSparameterException("S parameter should be within the range of selected VNA Ports.")
    else:
        if int(s_parameter[1]) not in vna_ports:
            raise InvalidSparameterException("S parameter should be within the range of selected VNA Ports.")

def get_s_parameter_matrix_indices(s_parameter):
    if s_parameter == 'ALL':
        pass
    elif type(s_parameter) == list:
        return [[int(value)-1 for value in s_param.replace('S', '').replace('',  ' ').split()] for s_param in s_parameter]
    else:
        return [int(value)-1 for value in s_parameter.replace('S', '').replace('',  ' ').split()]

def get_all_active_s_parameters(snp_file_path, reflection):
    network = skrf.Network(snp_file_path)
    n = network.number_of_ports

    if reflection:
        return [f'S{i}{i}' for i in range(1, n+1)]
    else:
        return [f'S{i}{j}' for i in range(1, n+1) for j in range(1, n+1)]

def get_s_parameter_measurements(network, s_parameter, reflection):
    n = network.number_of_ports
    matrix_indices = get_s_parameter_matrix_indices(s_parameter)
    if s_parameter == 'ALL':
        if reflection:
            return [network.s_db[:, i, i] for i in range(n)]
        else:
            return [network.s_db[:, i, j] for i in range(n) for j in range(n)]
    elif type(s_parameter) == list:
        return [network.s_db[:, indices[0], indices[1]] for indices in matrix_indices]
    else:
        return network.s_db[:, matrix_indices[0], matrix_indices[1]]

def get_formatted_test_results(snp_file_path, s_parameter, reflection):
    network = skrf.Network(snp_file_path)
    measurements = get_s_parameter_measurements(network, s_parameter, reflection)

    results = []
    if type(s_parameter) == str and s_parameter != 'ALL':
        for i, frequency in enumerate(network.f):
            results.append({f'{s_parameter}': {frequency: measurements[i]}})
    else:
        for i, s_param in enumerate(s_parameter):
            for j, frequency in enumerate(network.f):
                results.append({f'{s_param}': {frequency: measurements[i][j]}})
    return results

def get_test_results_from_snp_file(snp_file_path, s_parameter: Union[str, list[str]], reflection):
    __throw_if_invalid_reflection_use(s_parameter, reflection)

    if s_parameter == 'ALL':
        s_parameter = get_all_active_s_parameters(snp_file_path, reflection)
    return get_formatted_test_results(snp_file_path, s_parameter, reflection)

def check_and_log_return_loss_pass_fail(s_parameter, frequency, return_loss, maximum_allowable_return_loss):
    if not (-return_loss) < maximum_allowable_return_loss:
        print(f"Test Failed at S-PARAMETER: {s_parameter}, FREQUENCY: {'%.3E'%Decimal(frequency)},  RETURN LOSS: {round(-return_loss, 4)}, OFFSET: {round(-return_loss-maximum_allowable_return_loss, 4)}")

def test_tx_band_return_loss_test(snp_file_path, vna_ports, s_parameter, reflection, maximum_allowable_return_loss):
    __throw_if_invalid_s_parameter(vna_ports, s_parameter)

    test_results = get_test_results_from_snp_file(snp_file_path, s_parameter, reflection)
    for result in test_results:
        for s_param, measurements in result.items():
            for frequency, return_loss in measurements.items():
                check_and_log_return_loss_pass_fail(s_param, frequency, return_loss, maximum_allowable_return_loss)

def start_return_loss_pass_fail_test():
    vna_ports = [1, 2]
    s_parameter = 'S11'
    reflection = True
    maximum_allowable_return_loss = 50

    test_tx_band_return_loss_test(two_port_file_path, vna_ports, s_parameter, reflection, maximum_allowable_return_loss)


if __name__ == '__main__':
    start_return_loss_pass_fail_test()
