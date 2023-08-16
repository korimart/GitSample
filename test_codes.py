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


class InvalidSnpFileException(Exception):
    """Raised when the SNP file format does not match with number of VNA Ports chosen."""
    pass

def __throw_if_invalid_reflection_use(s_parameter, reflection):
    if reflection and s_parameter != 'ALL':
        raise InvalidReflectionUseException("S parameter must be set to 'ALL' to enable reflection.")

def __throw_if_invalid_snp_file(snp_file_path, vna_ports):
    n = len(vna_ports)
    base_name =os.path.basename(snp_file_path)
    if f'.s{n}p' not in base_name:
        raise InvalidSnpFileException("File format must match with the number of VNA Ports used.")

def test_get_test_results(snp_file_path, vna_ports, s_parameter: Union[str, list[str]], reflection=False):
    __throw_if_invalid_reflection_use(s_parameter, reflection)

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

def test_log_pass_fail(snp_file_path, vna_ports, s_parameter, reflection, maximum_allowable_return_loss):
    __throw_if_invalid_snp_file(snp_file_path, vna_ports)

    test_results = test_get_test_results(snp_file_path, vna_ports, s_parameter, reflection)
    for result in test_results:
        for s_param, measurements in result.items():
            for frequency, return_loss in measurements.items():
                if not (-return_loss) < maximum_allowable_return_loss:
                    print(f"Test Failed at S-PARAMETER: {s_param}, FREQUENCY: {'%.3E'%Decimal(frequency)},  RETURN LOSS: {round(-return_loss, 4)}, OFFSET: {round(-return_loss-maximum_allowable_return_loss, 4)}")

def start_return_loss_pass_fail_test():
    vna_ports = [1, 2, 3]
    s_parameter = 'S11'
    reflection = False
    maximum_allowable_return_loss = 30

    test_log_pass_fail(two_port_file_path, vna_ports, s_parameter, reflection, maximum_allowable_return_loss)


if __name__ == '__main__':
    start_return_loss_pass_fail_test()