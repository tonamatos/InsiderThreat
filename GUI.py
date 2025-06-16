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



if __name__ == "__main__":
    app = App()
    #app.update_image('test.png')
    #app.update_user_feedback({"Initial Access": True, "Privilege Escalation": False, "Collection": False, "Exfiltration": True, "Defense Evasion": True})
    app.mainloop()