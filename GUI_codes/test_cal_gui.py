import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class CheckboxListWidget(ctk.CTkFrame):
    def __init__(self, parent, title_button_title: str, check_button_labels: list[str], max_checks) -> None:
        self.parent = parent
        ctk.CTkFrame.__init__(self, parent)

        self.title_button_title = title_button_title
        self.check_button_labels = check_button_labels
        self.max_checks = max_checks
        self.number_of_check_buttons = len(self.check_button_labels)

        self.title_button = ctk.CTkButton(self, text=self.title_button_title, command=self.clear, fg_color='red')
        self.title_button.grid(row=0)

        self.check_button_vars = [ctk.BooleanVar() for _ in range(self.number_of_check_buttons)]
        self.check_buttons = [ctk.CTkCheckBox(
            self,
            text=self.check_button_labels[i],
            variable=self.check_button_vars[i],
            onvalue='True',
            offvalue='False',
            command=self.check_button_checked
        ) for i in range(self.number_of_check_buttons)]

        for i, each in enumerate(self.check_buttons):
            each.grid(row=i+1)

    def get_checked_indices(self):
        return [i for i, var in enumerate(self.check_button_vars) if var.get()]

    def get_checked_texts(self):
        checked_indices = self.get_checked_indices()
        checked_buttons = [self.check_button[i] for i in checked_indices]
        return [each['text'] for each in checked_buttons]

    def get_number_of_checked_indices(self):
        return len(self.get_checked_indices())
    
    def set_all_checks_checked(self, check: bool):
        for each in self.check_buttons:
            each.select() if check else each.deselect()

    def set_all_checks_enabled(self, enable: bool):
        for each in self.check_buttons:
            each.configure(state='normal') if enable else each.configure(state='disabled')

    def set_button_color_as_enabled(self, enable: bool):
        if enable:
            self.title_button.configure(fg_color='red')
        else:
            self.title_button.configure(fg_color='green')

    def check_button_checked(self):
        if self.get_number_of_checked_indices() >= self.max_checks:
            self.set_all_checks_enabled(False)
            self.set_button_color_as_enabled(False)

    def confirm(self):
        self.set_all_checks_enabled(False)
        self.set_button_color_as_enabled(False)

    def clear(self):
        self.set_all_checks_enabled(True)
        self.set_all_checks_checked(False)
        self.set_button_color_as_enabled(True)


class ComboboxListWidget(ctk.CTkFrame):
    def __init__(self, parent):
        self.parent = parent
        ctk.CTkFrame.__init__(self, parent)

        self.title_button = None
        self.ctk_labels = None
        self.combos = None
        self.str_vars = None

    def create_title_button(self, title_label: str, row: int, column: int):
        if title_label != None or title_label != '':
            self.title_button = ctk.CTkButton(self, text=title_label, command=self.clear, fg_color='red')
            self.title_button.grid(row=row, column=column, columnspan=1)

    def create_labels(self, labels: list[str], row: int, column: int):
        if labels != None or labels != []:
            self.ctk_labels = [ctk.CTkLabel(self, text=labels[i]) for i in range(len(labels))]
            for i, each in enumerate(self.ctk_labels):
                each.grid(row=row+i, column=column)

    def create_combos(self, combo_labels: list[str], number_of_combos: int, row: int, column: int):
        self.str_vars = [ctk.StringVar() for _ in range(number_of_combos)]
        if combo_labels != None or combo_labels != []:
            self.combos = [ctk.CTkComboBox(self, values=combo_labels, variable=self.str_vars[i]) for i in range(number_of_combos)]
            for i, each in enumerate(self.combos):
                each.grid(row=row+i, column=column)

    def set_default_combo_values(self, combo_values: list[int]):
        for i, var in enumerate(self.str_vars):
            var.set(combo_values[i])

    def set_all_combos_enabled(self, enable: bool):
        for each in self.combos:
            each.configure(state='normal') if enable else each.configure(state='disabled')

    def set_button_color_as_enabled(self, enable: bool):
        if enable:
            self.title_button.configure(fg_color='red')
        else:
            self.title_button.configure(fg_color='green')

    def confirm(self):
        if self.title_button == None:
            self.set_all_combos_enabled(False)
        else:
            self.set_all_combos_enabled(False)
            self.set_button_color_as_enabled(False)
            self.set_all_combos_enabled(False)  

    def clear(self): 
        if self.title_button == None:
            self.set_all_combos_enabled(True)
            self.set_default_combo_values([None for _ in range(len(self.str_vars))])
        else:
            self.set_all_combos_enabled(True)
            self.set_default_combo_values([None for _ in range(len(self.str_vars))])
            self.set_button_color_as_enabled(True)



class EntryListWidget(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self.parent = parent
        ctk.CTkFrame.__init__(self, parent)

        self.title_button = None
        self.ctk_labels = None
        self.entries = None
        self.str_vars = None

    def create_title_button(self, label: str, row: int, column: int):
        if label != None or label != '':
            self.title_button = ctk.CTkButton(self, text=label, command=self.clear, fg_color='red')
            self.title_button.grid(row=row, column=column, columnspan=1)

    def create_labels(self, labels: list[str], row: int, column: int):
        if labels != None or labels != []:
            self.entries_label = [ctk.CTkLabel(self, text=labels[i]) for i in range(len(labels))]
            for i, each in enumerate(self.entries_label):
                each.grid(row=row+i, column=column)

    def create_entries(self, number_of_entries: int, row: int, column: int):
        self.str_vars = [ctk.StringVar() for _ in range(number_of_entries)]
        self.entries = [ctk.CTkEntry(self, textvariable=self.str_vars[i]) for i in range(number_of_entries)]
        for i, each in enumerate(self.entries):
            each.grid(row=row+i, column=column)

    def set_all_entries_zero(self):
        for each in self.entries:
            each.insert(0, 0)
            each.delete(1, ctk.END)

    def set_default_entry_values(self, entry_values: list[int]):
        for i, var in enumerate(self.str_vars):
            var.set(entry_values[i])

    def set_default_combo_values(self, combo_values: list[int]):
        for i, var in enumerate(self.str_vars):
            var.set(combo_values[i])

    def set_all_entries_enabled(self, enable: bool):
        for each in self.entries:
            each.configure(state='normal') if enable else each.configure(state='disabled')

    def set_all_combos_enabled(self, enable: bool):
        for each in self.combos:
            each.configure(state='normal') if enable else each.configure(state='disabled')

    def set_button_color_as_enabled(self, enable: bool):
        if enable:
            self.title_button.configure(fg_color='red')
        else:
            self.title_button.configure(fg_color='green')

    def get_typed_values(self) -> list[int]:
        return [int(each.get()) for each in self.str_vars]

    def confirm(self):
        if self.title_button == None:
            self.set_all_entries_enabled(False)  
        else: 
            self.set_all_entries_enabled(False)  
            self.set_all_entries_enabled(False)
            self.set_button_color_as_enabled(False)

    def clear(self): 
        if self.title_button == None:
            self.set_all_entries_enabled(True)
            self.set_all_entries_zero() 
        else:
            self.set_all_entries_enabled(True)
            self.set_all_entries_zero() 
            self.set_button_color_as_enabled(True)


# TODO: refactor as path cal window
class EcalWindow():
    def __init__(self, parent, window_title: str):
        self.parent = parent
        self.window_title = window_title

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(self.window_title)
        self.window.geometry('660x170')

        self.widget_frame = None
        self.button_frame = None
        self.close_button = None
        self.clear_button = None
        self.confirm_button = None
        self.start_button = None
        self.vna_widget = None
        self.frequency_entry_widget = None
        self.frequency_combo_widget = None
        self.smoothing_widget = None

        self.create_frames()
        self.create_buttons()
        self.create_frequency_widget()

        tk.mainloop()

    def change_unit(self):
        for i, value in enumerate(self.frequency_widget.str_vars):
            if self.frequency_widget.combos[i].get() == 'Kilo':
                value.set(int(value.get())*1000)
            elif self.frequency_widget.combos[i].get() == 'Mega':
                value.set(int(value.get())*1000000)
            elif self.frequency_widget.combos[i].get() == 'Giga':
                value.set(int(value.get())*1000000000)
            else:
                pass

    def close(self):
        self.window.destroy()

    def clear(self):
        self.vna_widget.clear()
        self.frequency_widget.clear()
        self.smoothing_widget.clear()

    def confirm(self):
        self.vna_widget.confirm()
        self.frequency_entry_widget.confirm()
        self.frequency_combo_widget.confirm()
        self.smoothing_widget.confirm()
        self.change_unit()

    def start(self):
        vna_ports = self.vna_widget.get_checked_indices()
        frequencies = self.frequency_widget.get_typed_values()
        start, stop, step = frequencies[0], frequencies[1], frequencies[2]

        # self.inst.vna.initialize_display()
        # self.inst.vna.set_ports_to_be_calibrated(vna_ports)
        # self.inst.vna.set_frequency_range(start, stop, step)
        # self.inst.vna.measure_ecal(vna_ports, 'SOLT')

    def create_frames(self):
        self.widget_frame = ctk.CTkFrame(self.window)
        self.button_frame = ctk.CTkFrame(self.window)

        self.widget_frame.pack(fill='both', side='top')
        self.button_frame.pack(fill='both', side='bottom')

    def create_buttons(self):
        self.close_button = ctk.CTkButton(self.button_frame, text='Close', command=self.close)
        self.clear_button = ctk.CTkButton(self.button_frame, text='Clear', command=self.clear)
        self.confirm_button = ctk.CTkButton(self.button_frame, text='Confirm', command=self.confirm)
        self.start_button = ctk.CTkButton(self.button_frame, text='Start', command=self.start)

        self.close_button.pack(expand=True, fill='both', side='left', ipady=10)
        self.confirm_button.pack(expand=True, fill='both', side='left')
        self.start_button.pack(expand=True, fill='both', side='left')

    def create_vna_widget(self):
        self.vna_widget = CheckboxListWidget(self.widget_frame, 'VNA Ports', [f'Port{i}' for i in range(1, 5)], 5)
        self.vna_widget.pack(fill='y', side='left', expand=True)

    def create_frequency_widget(self):
        self.frequency_entry_widget = EntryListWidget(self.widget_frame)
        self.frequency_entry_widget.create_title_button('Frequency', row=0, column=1)
        self.frequency_entry_widget.create_labels(['Start', 'Stop', 'Step'], row=1, column=0)
        self.frequency_entry_widget.create_entries(3, row=1, column=1)
        self.frequency_entry_widget.set_default_entry_values([2, 6, 1])

        self.frequency_combo_widget = ComboboxListWidget(self.widget_frame)
        self.frequency_combo_widget.create_title_button('', row=0, column=0)
        self.frequency_combo_widget.create_combos(['Kilo', 'Mega', 'Giga'], 3, row=1, column=0)
        self.frequency_combo_widget.set_default_combo_values(['Giga', 'Giga', 'Mega'])

        self.frequency_entry_widget.pack(fill='y', side='left')
        self.frequency_combo_widget.pack(fill='y', side='left')

    def create_smoothing_widget(self):
        # TODO: continue here
        self.smoothing_widget = EntryListWidget(self.widget_frame, 'Smoothing', ['Percentage'], None)
        self.smoothing_widget.create_title_button('Smoothing', row=0, column=1)
        self.smoothing_widget.create_labels
        self.smoothing_widget.pack(fill='y', side='left', expand=True)
        self.smoothing_widget.set_default_entry_values([0])


class PathCalWindow():
    def __init__(self, parent, window_title) -> None:
        self.parent = parent
        self.window_title = window_title

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(self.window_title)
        self.window.geometry('540x500')

        self.combo_frame = None
        self.entry_frame = None
        self.button_frame = None
        self.close_button = None
        self.clear_button = None
        self.confirm_button = None
        self.start_button = None
        self.antenna_widget = None
        self.instrument_widget = None

        self.create_frames()
        self.create_buttons()
        self.create_antenna_widget()
        self.create_instrument_widget()
        self.create_frequency_widget()
        self.create_smoothing_widget()

        tk.mainloop()

    def change_unit(self):
        for i, value in enumerate(self.frequency_entry_widget.str_vars):
            if self.frequency_combo_widget.combos[i].get() == 'Kilo':
                value.set(int(value.get())*1000)
            elif self.frequency_combo_widget.combos[i].get() == 'Mega':
                value.set(int(value.get())*1000000)
            elif self.frequency_combo_widget.combos[i].get() == 'Giga':
                value.set(int(value.get())*1000000000)
            else:
                pass

    def close(self):
        self.window.destroy()

    def clear(self):
        self.antenna_widget.clear()
        self.instrument_widget.clear()
        self.frequency_entry_widget.clear()
        self.frequency_combo_widget.clear()
        self.smoothing_widget.clear()

    def confirm(self):
        self.antenna_widget.confirm()
        self.instrument_widget.confirm()
        self.frequency_entry_widget.confirm()
        self.frequency_combo_widget.confirm()
        self.smoothing_widget.confirm()
        self.change_unit()

    def start(self):
        frequencies = self.frequency_entry_widget.get_typed_values()
        start, stop, step = frequencies[0], frequencies[1], frequencies[2]
        print(start, stop, step)

    def create_frames(self):
        self.combo_frame = ctk.CTkFrame(self.window)
        self.entry_frame = ctk.CTkFrame(self.window)
        self.button_frame = ctk.CTkFrame(self.window)

        self.combo_frame.pack(expand=True, fill='both')
        self.entry_frame.pack(expand=True, fill='both')
        self.button_frame.pack(expand=True, fill='both', side='bottom')

    def create_buttons(self):
        self.close_button = ctk.CTkButton(self.button_frame, text='Close', command=self.close)
        self.clear_button = ctk.CTkButton(self.button_frame, text='Clear', command=self.clear)
        self.confirm_button = ctk.CTkButton(self.button_frame, text='Confirm', command=self.confirm)
        self.start_button = ctk.CTkButton(self.button_frame, text='Start', command=self.start)

        self.close_button.pack(expand=True, fill='both', side='left')
        self.clear_button.pack(expand=True, fill='both', side='left')
        self.confirm_button.pack(expand=True, fill='both', side='left')
        self.start_button.pack(expand=True, fill='both', side='left')

    def create_antenna_widget(self):
        combo_labels = [f'port{i}' for i in range(1, 5)]
        combo_labels.append('None')

        self.antenna_widget = ComboboxListWidget(self.combo_frame)
        self.antenna_widget.create_title_button('Antennas', row=0, column=1)
        self.antenna_widget.create_labels([f'ANT{i}' for i in range(1 , 9)], row=1, column=0)
        self.antenna_widget.create_combos(combo_labels, 8, row=1, column=1)
        self.antenna_widget.pack(side='left', expand=True, fill='both')
        self.antenna_widget.set_default_combo_values(['VNA' for _ in range(1, 9)])

    def create_instrument_widget(self):
        combo_labels = [f'Port{i}' for i in range(1, 5)]
        combo_labels.append('None')

        self.instrument_widget = ComboboxListWidget(self.combo_frame)
        self.instrument_widget.create_title_button('Instruments', row=0, column=1)
        self.instrument_widget.create_labels(['PWM', 'SA', 'SG1', 'SG2'], row=1, column=0)
        self.instrument_widget.create_combos(combo_labels, 4, row=1, column=1)
        self.instrument_widget.set_default_combo_values(['VNA' for _ in range(1, 5)])
        self.instrument_widget.pack(side='left', expand=True, fill='both')

    def create_frequency_widget(self):
        self.frequency_entry_widget = EntryListWidget(self.entry_frame)
        self.frequency_entry_widget.create_title_button('Frequency', row=0, column=1)
        self.frequency_entry_widget.create_labels(['Start', 'Stop', 'Step'], row=1, column=0)
        self.frequency_entry_widget.create_entries(3, row=1, column=1)

        self.frequency_combo_widget = ComboboxListWidget(self.entry_frame)
        self.frequency_combo_widget.create_title_button('', row=0, column=0)
        self.frequency_combo_widget.create_combos(['Kilo', 'Mega', 'Giga', 'None'], 3, row=1, column=0)

        self.frequency_entry_widget.set_default_entry_values([2, 6, 1])
        self.frequency_combo_widget.set_default_combo_values(['Giga', 'Giga', 'Mega'])  

        self.frequency_entry_widget.pack(side='left', fill='both')
        self.frequency_combo_widget.pack(side='left', fill='both')
        # self.frequency_combo_widget.pack(side='left', fill='y', pady=28)

    def create_smoothing_widget(self):
        # TODO: create on/off button
        self.smoothing_widget = EntryListWidget(self.entry_frame)

        self.smoothing_widget.create_title_button('Smoothing', row=0, column=1)
        self.smoothing_widget.create_labels(['percentage'], row=1, column=0)
        self.smoothing_widget.create_entries(1, row=1, column=1)
        self.smoothing_widget.set_default_entry_values([0])
        self.smoothing_widget.pack(side='left', expand=True, fill='both')


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self.parent = parent
        ctk.CTkFrame.__init__(self, parent)
        self.parent.title("Calibration GUI")
        self.parent.geometry("450x450")

        self.e_cal_window = None
        self.path_cal_window = None

        self.e_cal_button = ctk.CTkButton(self.parent, text='Start E Calibration', command=self.create_e_calibration_window)
        self.path_cal_button = ctk.CTkButton(self.parent, text='Start Path Calibration', command=self.create_path_calibration_window)

        self.e_cal_button.pack(fill='both', expand=True)
        self.path_cal_button.pack(fill='both', expand=True)

        tk.mainloop()

    def create_e_calibration_window(self):
        self.e_cal_window = EcalWindow(self.parent, 'E Calibration')

    def create_path_calibration_window(self):
        self.path_cal_window = PathCalWindow(self.parent, 'Path Calibration')

    def get_associated_checked_indices_of_sub_widgets(self, labels, checkbox_widget, sub_checkbox_widgets):
        # checked_values_of_main_widget = self.get_checked_values(checkbox_widget)
        # associated_indices_of_sub_widget = [labels.index(label) for i, label in enumerate(labels) if label == checked_values_of_main_widget[i]]
        # associated_sub_widgets = [sub_checkbox_widgets[each] for each in associated_indices_of_sub_widget]
        # checked_indices_of_sub_widget = [[sub_widget.get_checked_indices] for sub_widget in associated_sub_widgets]
        # return [{checked_values_of_main_widget[i]:checked_indices_of_sub_widget[i]} for i in range(len(checked_values_of_main_widget))]
        pass


if __name__ == '__main__':
    root = tk.Tk()
    test = MainWindow(root)
    # test_path_window = PathCalWindow(root, 'Window Test')