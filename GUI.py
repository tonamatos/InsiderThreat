import tkinter as tk
from tkinter import ttk
from config import GUI_WINDOW_DIMENSIONS
import user_feedback
import subprocess
import main

class App(tk.Tk):
    def __init__(self):
        #basic setup
        super().__init__()
        self.geometry(GUI_WINDOW_DIMENSIONS)
        self.resizable(True,True)
        self.title("Attack Graph Viewer")

        #image setup
        self.image_container = ttk.Labelframe(self, text='Attack Graph')
        self.image_container.grid(row=0, column=1, padx=20)

        self.attack_image = tk.PhotoImage()

        ttk.Label(self.image_container, image=self.attack_image).pack()

        #feedback setup
        self.feedback_container = ttk.Labelframe(self, text='Feedback')
        self.feedback_container.grid(row=0, column=2, padx=20)

        self.bool_initial_access = tk.BooleanVar()
        self.bool_privilege_escalation = tk.BooleanVar()
        self.bool_collection = tk.BooleanVar()
        self.bool_exfiltration = tk.BooleanVar()
        self.bool_defense_evasion = tk.BooleanVar()

        self.check_initial_access = ttk.Checkbutton(self.feedback_container, text='Initial Access', variable=self.bool_initial_access, state='disabled')
        self.check_privilege_escalation = ttk.Checkbutton(self.feedback_container, text='Privilege Escalation', variable=self.bool_privilege_escalation, state='disabled')
        self.check_collection = ttk.Checkbutton(self.feedback_container, text='Collection', variable=self.bool_collection, state='disabled')
        self.check_exfiltration = ttk.Checkbutton(self.feedback_container, text='Exfiltration', variable=self.bool_exfiltration, state='disabled')
        self.check_defense_evasion = ttk.Checkbutton(self.feedback_container, text='Defense Evasion', variable=self.bool_defense_evasion, state='disabled')

        self.check_initial_access.grid(row=0, sticky='w')
        self.check_privilege_escalation.grid(row=1, sticky='w')
        self.check_collection.grid(row=2, sticky='w')
        self.check_exfiltration.grid(row=3, sticky='w')
        self.check_defense_evasion.grid(row=4, sticky='w')

        self.submit_button = ttk.Button(self.feedback_container, text='Submit', command=self.submit_feedback)
        self.submit_button.grid(row=5)
        

        #dropdown setup
        self.dropdown_container = ttk.Labelframe(self, text='Attack Graph Selection')
        self.dropdown_container.grid(row=0, column=0, padx=20, pady=20, rowspan=30)

        # --- Tona's code goes here ---

        self.load_button = ttk.Button(self.dropdown_container, text='Reload data', command=self.load_system_data)
        self.load_button.grid(row=0, column=0, pady=10)

        self.subgraph_var = tk.StringVar()
        self.subgraph_dropdown = ttk.Combobox(self.dropdown_container, textvariable=self.subgraph_var, state="readonly")
        self.subgraph_dropdown.grid(row=1, column=0)

        # Scrollable info box
        info_frame = tk.Frame(self.dropdown_container)
        info_frame.grid(row=2, column=0, pady=10)

        self.info_scrollbar = ttk.Scrollbar(info_frame)
        self.info_scrollbar.pack(side="right", fill="y")

        self.subgraph_info_box = tk.Text(info_frame, width=50, height=15, wrap="word", yscrollcommand=self.info_scrollbar.set)
        self.subgraph_info_box.pack(side="left", fill="both")

        self.info_scrollbar.config(command=self.subgraph_info_box.yview)

        # Populate dropdown
        self.all_event_subgraphs = sorted(main.all_event_subgraphs, key=lambda sg: sg["Score"], reverse=True)
        #self.subgraph_dropdown["values"] = ["Event "+str(sg["Index"])+" | Score: "+str(sg["Score"]) for sg in self.all_event_subgraphs]
        self.subgraph_dropdown["values"] = [sg["Index"] for sg in self.all_event_subgraphs]
        self.subgraph_dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)
    
    def update_image(self, path):
        self.attack_image.config(file=path)
        
    def update_user_feedback(self, dict):

        self.bool_initial_access.set(False)
        self.bool_privilege_escalation.set(False)
        self.bool_collection.set(False)
        self.bool_exfiltration.set(False)
        self.bool_defense_evasion.set(False)

        text_dict = {}
        for tactic in dict:
            if dict[tactic]:
                text_dict[tactic] = 'enabled'
            if not dict[tactic]:
                text_dict[tactic] = 'disabled'

        self.check_initial_access.config(state=text_dict['Initial Access'])
        self.check_privilege_escalation.config(state=text_dict['Privilege Escalation'])
        self.check_collection.config(state=text_dict['Collection'])
        self.check_exfiltration.config(state=text_dict['Exfiltration'])
        self.check_defense_evasion.config(state=text_dict['Defense Evasion'])
    
    def submit_feedback(self):
        user_feedback.update_weight_parameters({"Initial Access": self.bool_initial_access.get(), 
                       "Privilege Escalation": self.bool_privilege_escalation.get(), 
                       "Collection": self.bool_collection.get(), 
                       "Exfiltration": self.bool_exfiltration.get(), 
                       "Defense Evasion": self.bool_defense_evasion.get()})

    def on_dropdown_select(self, event=None):
        selected_index = self.subgraph_var.get()
        selected_subgraph = next((sg for sg in self.all_event_subgraphs if str(sg["Index"]) == selected_index), None)
        if selected_subgraph:
            # Update image path
            if int(selected_index) < main.GRAPH_DISPLAY_CUTOFF:
                image_path = f"graph_plots/event_subgraph_{selected_index}.png"
                self.update_image(image_path)
            else:
                self.attack_image.config(file="graph_plots/placeholder.png")


            # Display basic info
            self.subgraph_info_box.config(state="normal")
            self.subgraph_info_box.delete("1.0", tk.END)
            self.subgraph_info_box.insert(tk.END, f"Event index: \t\t{selected_index}")
            score = selected_subgraph["Score"]
            self.subgraph_info_box.insert(tk.END, f"\nSeverity score: \t{score}")
            subgraph = selected_subgraph["Subgraph"]
            self.subgraph_info_box.insert(tk.END, "\n\n"+"="*20+ " NODES " + "="*20+"\n")
            for node in subgraph.nodes():
                desc = subgraph.nodes[node].get("description", "[Missing description]")
                type = subgraph.nodes[node].get("type", "[Missing type]")
                message = subgraph.nodes[node].get("alert_message", "[Missing message]")
                timestamp = subgraph.nodes[node].get("timestamp", "[Missing timestamp]")
                self.subgraph_info_box.insert(tk.END, f"\nDescription: \t{desc}")
                self.subgraph_info_box.insert(tk.END, f"\nType: \t{type}")
                self.subgraph_info_box.insert(tk.END, f"\nMessage: \t{message}")
                self.subgraph_info_box.insert(tk.END, f"\nTimestamp: \t{timestamp}")
                self.subgraph_info_box.insert(tk.END, "\n"+"-"*50)
            self.subgraph_info_box.insert(tk.END, "\n\n"+"="*20+ " HOSTS " + "="*20+"\n")
            for node in subgraph.nodes():
                for neighbor in main.G.neighbors(node):
                    if main.G.nodes[neighbor].get("type") == "Host":
                        host_props = main.G.nodes[neighbor].get("properties", {})
                        ip_address = host_props["ip_address"]
                        os_type = host_props["os_type"]
                        department = host_props["department"]
                        host_name = main.G.nodes[neighbor].get("name", {})
                        self.subgraph_info_box.insert(tk.END, f"\nName: \t\t{host_name}")
                        self.subgraph_info_box.insert(tk.END, f"\nIP address: \t{ip_address}")
                        self.subgraph_info_box.insert(tk.END, f"\nOS type: \t\t{os_type}")
                        self.subgraph_info_box.insert(tk.END, f"\nDepartment: \t{department}")
                        self.subgraph_info_box.insert(tk.END, "\n"+"-"*50)


            self.subgraph_info_box.config(state="disabled")


    def load_system_data(self):
        subprocess.run(["python", "main.py"])


if __name__ == "__main__":
    app = App()
    #app.update_image('test.png')
    #app.update_user_feedback({"Initial Access": True, "Privilege Escalation": False, "Collection": False, "Exfiltration": True, "Defense Evasion": True})
    app.mainloop()