"""
date: 2023-03-16
last update: 2023-08-23
author: Jin Her
"""
import tkinter as tk
from tkinter import ttk
from datetime import date
import time
import itertools
from instruments.Inst import Inst


class CheckListWidget(tk.Frame):
    def __init__(self, parent, btn_label, chk_labels, max_checks):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.btn_label = btn_label
        self.chk_labels = chk_labels
        self.max_checks = max_checks
        self.num_of_chk_labels = len(chk_labels)

        self.clear_btn = tk.Button(self, text=btn_label, command=self.clear)
        self.clear_btn.configure(font=("Courier 10"))
        self.clear_btn.grid(row=0, column=0, ipadx=15)

        self.int_vars = [tk.BooleanVar() for _ in range(self.num_of_chk_labels)]

        self.chk_btn_list = [tk.Checkbutton(
            self,
            text=chk_labels[i],
            font=("Courier 10"),
            variable=self.int_vars[i],
            onvalue=tk.TRUE,
            offvalue=tk.FALSE,
            command=self.check_btn_checked,
        ) for i in range(self.num_of_chk_labels)]

        for i, each in enumerate(self.chk_btn_list):
            each.grid(row=i+1, column=0)

    def get_checked_indices(self):
        return [i for i, var in enumerate(self.int_vars) if var.get()]

    def get_checked_labels(self):
        return [self.chk_labels[i] for i, var in enumerate(self.int_vars) if var.get()]

    def get_num_of_indices_selected(self):
        return len(self.get_checked_indices())

    def set_all_ports_enabled(self, enable):
        for button in self.chk_btn_list:
            button["state"] = tk.NORMAL if enable else tk.DISABLED

    def set_all_ports_checked(self, checked):
        for button in self.chk_btn_list:
            button.select() if checked else button.deselect()

    def set_clear_btn_color(self, change):
        if change:
            self.clear_btn.configure(bg="#98F516")
        else:
            self.clear_btn.configure(bg="#f0f0f0")

    def check_btn_checked(self):
        if self.get_num_of_indices_selected() >= self.max_checks:
            self.set_all_ports_enabled(False)
            self.set_clear_btn_color(True)

    def clear(self):
        self.set_all_ports_enabled(True)
        self.set_all_ports_checked(False)
        self.set_clear_btn_color(False)


class EntryListWidget(tk.Frame):
    def __init__(self, parent, btn_label, entry_label, combo_label, num_of_entries, num_of_combos, make_switch, inst):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.inst = inst

        self.btn_label = btn_label
        self.entry_label = entry_label
        self.combo_label = combo_label
        self.num_of_entries = num_of_entries
        self.num_of_combos = num_of_combos
        self.make_switch = make_switch

        self.clear_btn = tk.Button(self, text=btn_label, command=self.clear, padx=25)
        self.clear_btn.configure(font=("Courier 10"))
        self.clear_btn.grid(row=0, columnspan=3, ipadx=30)

        self.int_vars = [tk.IntVar() for _ in range(self.num_of_entries)]
        self.str_vars = [tk.StringVar() for _ in range(self.num_of_combos)]

        self.entries_label = [tk.Label(
            self,
            text=self.entry_label[i],
            font=("Courier 10"),
        ) for i in range(self.num_of_entries)]

        for i, lbl in enumerate(self.entries_label):
            lbl.grid(row=i+1, column=0, pady=5)

        self.entries = [tk.Entry(
            self,
            textvariable=self.int_vars[i],
            width=15,
        ) for i, entry in enumerate(range(self.num_of_entries))]

        for i, entry in enumerate(self.entries):
            entry.grid(row=i+1, column=1, pady=8)

        self.combos = [ttk.Combobox(
            self,
            textvariable=self.str_vars[i],
            values=self.combo_label,
            width=7
        ) for i, combo in enumerate(range(self.num_of_combos))]

        for i, combo in enumerate(self.combos):
            combo.grid(row=i+1, column=2, padx=5)

        self.confirm_btn = tk.Button(
            self,
            text="Confirm",
            font=("Courier 8"),
            command=self.confirm_entries,
        )
        self.confirm_btn.grid(row=len(self.entries)+1, column=1, pady=2)

        if self.make_switch:
            self.btn_on = tk.Button(
                self,
                text="ON",
                font=("Courier 8"),
                command=lambda: self.switch_smoothing(True),
            )
            self.btn_on.grid(row=1, column=2, ipadx=10)

            self.btn_off = tk.Button(
                self,
                text="OFF",
                font=("Courier 8"),
                command=lambda: self.switch_smoothing(False),
            )
            self.btn_off.grid(row=1, column=3, ipadx=5)

    def change_unit(self):
        for i, value in enumerate(self.int_vars):
            if self.combos[i].get() == "Kilo":
                value.set(value.get()*1000)
            elif self.combos[i].get() == "Mega":
                value.set(value.get()*1000000)
            elif self.combos[i].get() == "Giga":
                value.set(value.get()*1000000000)
            else:
                pass

    def get_typed_values(self):
        return [value.get() for value in self.int_vars]

    def set_btn_color(self, btn, change):
        if change:
            btn.configure(bg="#98F516")
        else:
            btn.configure(bg="#f0f0f0")

    def set_all_entries_enabled(self, enable):
        self.set_btn_color(self.clear_btn, True)

        for entry in self.entries:
            entry["state"] = tk.NORMAL if enable else tk.DISABLED

    def set_default_entries_value(self, entries_value: list):
        for i, var in enumerate(self.int_vars):
            var.set(entries_value[i])

    def set_default_combos_value(self, combos_value: list):
        for i, var in enumerate(self.str_list):
            var.set(combos_value[i])

    def switch_smoothing(self, on: bool):
        if on:
            self.inst.vna.set_smoothing_on(True)
            self.set_btn_color(self.btn_on, True)
        else:
            self.inst.vna.set_smoothing_on(False)
            self.set_btn_color(self.btn_on, False)

    def set_all_entries_empty(self):
        for entry in self.entries:
            entry.delete(0, tk.END)

    def confirm_entries(self):
        self.set_all_entries_enabled(False)
        if self.btn_label == "Frequency":
            self.change_unit()
            freq = self.get_typed_values()
            self.inst.vna.set_frequency_range(freq[0], freq[1], freq[2])
        elif self.btn_label == "Smoothing":
            self.inst.vna.set_smoothing_percentage(self.get_typed_values()[0])

    def clear(self):
        self.set_all_entries_enabled(True)
        self.set_all_entries_empty()
        self.set_btn_color(self.clear_btn, False)


class CalibrationGUI(tk.Frame):
    def __init__(self, window):
        self.inst = Inst()
        self.inst.connect_all_instruments()

        self.ecal_completed = False

        tk.Frame.__init__(self, window)
        self.window = window
        self.window.title("Calibration GUI")
        self.window.geometry("850x300")

        self.vna_widget = CheckListWidget(
            self.window,
            'VNA Ports',
            [
                'Port1',
                'Port2',
                'Port3',
                'Port4',
            ],
            2,
        )
        self.antenna_widget = CheckListWidget(
            self.window,
            'Antenna Ports',
            [
                'ANT1',
                'ANT2',
                'ANT3',
                'ANT4',
                'ANT5',
                'ANT6',
                'ANT7',
                'ANT8',
            ],
            1,
        )
        self.instrument_widget = CheckListWidget(
            self.window,
            'Instruments',
            [
                'PM',
                'SA',
                'SG1',
                'SG2',
            ],
            1,
        )
        self.frequency_widget = EntryListWidget(
            self.window,
            'Frequency',
            [
                'Start',
                'Stop',
                'Step',
            ],
            [
                'Kilo',
                'Mega',
                'Giga',
            ],
            3,
            3,
            False,
            self.inst,
        )
        self.frequency_widget.set_default_entries_value([2, 6, 1])
        self.frequency_widget.set_default_combos_value(['Giga', 'Giga', 'Mega'])

        self.smoothing_widget = EntryListWidget(
            self.window,
            'Smoothing',
            ['%'],
            None,
            1,
            0,
            True,
            self.inst,
        )

        self.frame_btn = tk.Frame(self.window)
        self.frame_btn.pack(fill=tk.BOTH, side=tk.BOTTOM, anchor=tk.S)

        self.vna_widget.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, anchor=tk.N)
        self.antenna_widget.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, anchor=tk.N)
        self.instrument_widget.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, anchor=tk.N)
        self.frequency_widget.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, anchor=tk.N)
        self.smoothing_widget.pack(fill=tk.BOTH, expand=tk.TRUE)

        self.btn_clear = tk.Button(
            self.frame_btn,
            text="Clear",
            font=("Courier 10"),
            command=self.clear,
        )

        self.btn_e_cal = tk.Button(
            self.frame_btn,
            text="Start E Calibration",
            font=("Courier 10"),
            command=self.start_ecal,
        )

        self.btn_path_cal = tk.Button(
            self.frame_btn,
            text="Start Path Loss Calibration",
            font=("Courier 10"),
            command=self.start_path_cal,
        )

        self.btn_clear.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, ipady=8)
        self.btn_e_cal.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, ipady=8)
        self.btn_path_cal.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE, ipady=8)

        self.clearable_widget = [
            self.vna_widget,
            self.antenna_widget,
            self.instrument_widget,
            self.frequency_widget,
            self.smoothing_widget,
        ]

        tk.mainloop()

    def clear(self):
        for widget in self.clearable_widget:
            widget.clear()

    def show_plot(self, port_number, inst):
        vna_ports = [i+1 for i in self.vna_widget.get_checked_indices()]
        frequencies = self.frequency_widget.get_typed_values()
        self.inst.vna.set_frequency_range(frequencies[0], frequencies[1], frequencies[2])
        
        date_today = date.today().strftime("%Y%b%d")
        stem_of_file_name = f'Port{port_number}_{inst}_{date_today}'
        # time to stabilize the connection
        time.sleep(3) 
        self.inst.vna.set_and_display_all_traces(vna_ports)
        # time to measure and display measurements
        time.sleep(3)
        snp_file_name = self.inst.vna.save_traces_as_snp_file(vna_ports, stem_of_file_name)
        file_name_csv = self.inst.vna.save_traces_as_csv_file(stem_of_file_name)
        # time to save files in the VNA
        time.sleep(3)
        snp_file_path = self.inst.vna.copy_file_to_local(snp_file_name)
        csv_file_path = self.inst.vna.copy_file_to_local(file_name_csv)
        # time to copy file from VNA to the local folder (Radio_E2E_Performance -> instruments -> pathloss)
        time.sleep(3)
        self.inst.vna.plot_from_snp_file(snp_file_path)

    def start_ecal(self):
        frequencies = self.frequency_widget.get_typed_values()
        vna_ports = [i+1 for i in self.vna_widget.get_checked_indices()]

        self.inst.vna.preset()
        self.inst.vna.set_frequency_range(frequencies[0], frequencies[1], frequencies[2])
        
        should_connect = tk.messagebox.askokcancel(
            message="Connect E Cal to the VNA.\nClick OK once the connection is made.")

        if should_connect:
            self.ecal_completed = self.inst.vna.measure_ecal(vna_ports)
            if self.ecal_completed:
                tk.messagebox.showinfo(message="E Calibration complete.")
            else:
                tk.messagebox.showerror(message="Error Occurred. Please try again.")

    def start_path_cal(self):
        vna_ports = [i+1 for i in self.vna_widget.get_checked_indices()]
        antenna_ports = self.antenna_widget.get_checked_indices()
        instruments = self.instrument_widget.get_checked_labels()
        frequencies = self.frequency_widget.get_typed_values()

        self.inst.vna.set_frequency_range(frequencies[0], frequencies[1], frequencies[2])
        if not self.ecal_completed:
            tk.messagebox.showerror(message="E Calibration required to start Path Calibration."
                                    "\nIgnore this message if ECal is already done.")

        for instrument, ant_port in itertools.product(instruments, antenna_ports):
            should_connect = tk.messagebox.askokcancel(
                message=f"Connect ANT{ant_port+1} and {instrument} to VNA ports {str(vna_ports)[1:-1]}."
                        f"\nClick OK once the connection is made.")
            if should_connect:
                if instrument == 'PWRM':
                    self.inst.sw.switch_to_tx(ant_port, False)
                elif instrument == 'SPEC':
                    self.inst.sw.switch_to_tx(ant_port, True)
                else:
                    self.inst.sw.switch_to_rx(ant_port)
                self.show_plot(ant_port, instrument)
            if ant_port == len(antenna_ports)-1:
                tk.messagebox.showinfo(message="Path Calibration complete.")


if __name__ == "__main__":
    root = tk.Tk()
    test = CalibrationGUI(root)
