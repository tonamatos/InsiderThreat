import tkinter as tk
from tkinter import ttk
from config import GUI_WINDOW_DIMENSIONS
import user_feedback

class App(tk.Tk):
    def __init__(self):
        #basic setup
        super().__init__()
        self.geometry(GUI_WINDOW_DIMENSIONS)
        self.resizable(False,False)
        self.title("Attack Graph Viewer")

        #image setup
        self.image_container = ttk.Labelframe(self, text='Attack Graph')
        self.image_container.grid(row=0, column=1, padx=20)

        self.attack_image = tk.PhotoImage()

        ttk.Label(self.image_container, image=self.attack_image).pack()

        #feedback setup
        self.feedback_container = ttk.Labelframe(self, text='Feedback')
        self.feedback_container.grid(row=0, column=2, padx=20)

        self.tactic_statuses = {}

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
        self.dropdown_container.grid(column=0, padx=20, pady=20)

        #Tona's code goes here
    
    def update_image(self, path):
        self.attack_image.config(file=path)
        
    def update_user_feedback(self, dct):

        self.bool_initial_access.set(False)
        self.bool_privilege_escalation.set(False)
        self.bool_collection.set(False)
        self.bool_exfiltration.set(False)
        self.bool_defense_evasion.set(False)

        self.tactic_statuses = {}
        for tactic in dct:
            if dct[tactic]:
                self.tactic_statuses[tactic] = 'enabled'
            if not dct[tactic]:
                self.tactic_statuses[tactic] = 'disabled'

        self.check_initial_access.config(state=self.tactic_statuses['Initial Access'])
        self.check_privilege_escalation.config(state=self.tactic_statuses['Privilege Escalation'])
        self.check_collection.config(state=self.tactic_statuses['Collection'])
        self.check_exfiltration.config(state=self.tactic_statuses['Exfiltration'])
        self.check_defense_evasion.config(state=self.tactic_statuses['Defense Evasion'])
    
    def submit_feedback(self):
        tactic_dict = {}
        if self.tactic_statuses["Initial Access"] == 'enabled':
            tactic_dict["Initial Access"] = self.bool_initial_access.get()
        if self.tactic_statuses["Privilege Escalation"] == 'enabled':
            tactic_dict["Privilege Escalation"] = self.bool_privilege_escalation.get()
        if self.tactic_statuses["Collection"] == 'enabled':
            tactic_dict["Collection"] = self.bool_collection.get()
        if self.tactic_statuses["Exfiltration"] == 'enabled':
            tactic_dict["Exfiltration"] = self.bool_exfiltration.get()
        if self.tactic_statuses["Defense Evasion"] == 'enabled':
            tactic_dict["Defense Evasion"] = self.bool_defense_evasion.get()

        user_feedback.update_weight_parameters(tactic_dict)



if __name__ == "__main__":
    app = App()
    #app.update_image('test.png')
    #app.update_user_feedback({"Initial Access": True, "Privilege Escalation": False, "Collection": False, "Exfiltration": True, "Defense Evasion": True})
    app.mainloop()