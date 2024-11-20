import tkinter as tk
from tkinter import ttk, messagebox
from scipy.optimize import linprog


class LinearProgramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimización Lineal")
        self.root.geometry("800x600")
        self.root.configure(bg="#f2f2f2")

        # Variables principales
        self.opt_type = tk.StringVar(value="min")
        self.num_vars = tk.IntVar(value=2)
        self.num_constraints = tk.IntVar(value=2)
        self.non_negativity = tk.BooleanVar(value=True)

        # Estilos
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12), background="#f2f2f2")
        self.style.configure(
            "TButton",
            font=("Helvetica", 12, "bold"),
            background="#4caf50",
            foreground="black",
        )

        # Interfaz principal
        self.create_main_interface()

    def create_main_interface(self):
        # Título
        tk.Label(self.root, text="Optimización Lineal", font=("Helvetica", 18, "bold"), bg="#f2f2f2").pack(pady=20)

        # Tipo de optimización
        frame_type = tk.Frame(self.root, bg="#f2f2f2")
        frame_type.pack(pady=10)
        tk.Label(frame_type, text="Selecciona el tipo de optimización:", bg="#f2f2f2").pack(anchor=tk.W)
        ttk.Radiobutton(frame_type, text="Minimizar", variable=self.opt_type, value="min").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_type, text="Maximizar", variable=self.opt_type, value="max").pack(side=tk.LEFT, padx=5)

        # Número de variables
        frame_vars = tk.Frame(self.root, bg="#f2f2f2")
        frame_vars.pack(pady=10)
        tk.Label(frame_vars, text="Número de variables de decisión:", bg="#f2f2f2").pack(side=tk.LEFT)
        ttk.Entry(frame_vars, textvariable=self.num_vars, width=5).pack(side=tk.LEFT, padx=5)

        # Número de restricciones
        frame_constraints = tk.Frame(self.root, bg="#f2f2f2")
        frame_constraints.pack(pady=10)
        tk.Label(frame_constraints, text="Número de restricciones:", bg="#f2f2f2").pack(side=tk.LEFT)
        ttk.Entry(frame_constraints, textvariable=self.num_constraints, width=5).pack(side=tk.LEFT, padx=5)

        # No negatividad
        frame_nonneg = tk.Frame(self.root, bg="#f2f2f2")
        frame_nonneg.pack(pady=10)
        ttk.Checkbutton(frame_nonneg, text="Variables no negativas", variable=self.non_negativity).pack()

        # Botón para configurar
        ttk.Button(self.root, text="Configurar Problema", command=self.configure_problem).pack(pady=20)

    def configure_problem(self):
        try:
            num_vars = self.num_vars.get()
            num_constraints = self.num_constraints.get()

            if num_vars <= 0 or num_constraints <= 0:
                raise ValueError("Los valores deben ser mayores que 0.")

            self.coefficients_window()
        except ValueError:
            messagebox.showerror("Error", "Introduce valores válidos.")

    def coefficients_window(self):
        self.coeff_win = tk.Toplevel(self.root)
        self.coeff_win.title("Configurar Coeficientes")
        self.coeff_win.geometry("800x600")
        self.coeff_win.configure(bg="#f2f2f2")

        # Variables de decisión
        self.var_names = [tk.StringVar(value=f"x{i+1}") for i in range(self.num_vars.get())]
        for i, var_name in enumerate(self.var_names):
            ttk.Entry(self.coeff_win, textvariable=var_name, width=10).grid(row=0, column=i, padx=5, pady=5)

        # Coeficientes de la función objetivo
        tk.Label(self.coeff_win, text="Función objetivo", bg="#f2f2f2").grid(row=1, column=0, columnspan=2, pady=10)
        self.obj_coeffs = [tk.DoubleVar() for _ in range(self.num_vars.get())]
        for i, coeff in enumerate(self.obj_coeffs):
            ttk.Entry(self.coeff_win, textvariable=coeff, width=10).grid(row=2, column=i, padx=5, pady=5)

        # Restricciones
        self.constraints = []
        self.b_values = []
        self.operators = []
        for i in range(self.num_constraints.get()):
            row = []
            for j in range(self.num_vars.get()):
                var = tk.DoubleVar()
                ttk.Entry(self.coeff_win, textvariable=var, width=10).grid(row=3+i, column=j, padx=5, pady=5)
                row.append(var)
            self.constraints.append(row)

            operator = tk.StringVar(value="<=")
            ttk.Combobox(self.coeff_win, textvariable=operator, values=["<=", ">=", "="], width=5).grid(row=3+i, column=self.num_vars.get())
            self.operators.append(operator)

            b_value = tk.DoubleVar()
            ttk.Entry(self.coeff_win, textvariable=b_value, width=10).grid(row=3+i, column=self.num_vars.get() + 1)
            self.b_values.append(b_value)

        # Botón para resolver
        ttk.Button(self.coeff_win, text="Resolver", command=self.solve_problem).grid(row=4+self.num_constraints.get(), column=0, columnspan=3, pady=20)

    def solve_problem(self):
        # Extraer los datos
        c = [v.get() for v in self.obj_coeffs]
        if self.opt_type.get() == "max":
            c = [-v for v in c]

        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for i in range(self.num_constraints.get()):
            row = [v.get() for v in self.constraints[i]]
            operator = self.operators[i].get()
            b_value = self.b_values[i].get()

            if operator == "<=":
                A_ub.append(row)
                b_ub.append(b_value)
            elif operator == ">=":
                A_ub.append([-v for v in row])
                b_ub.append(-b_value)
            elif operator == "=":
                A_eq.append(row)
                b_eq.append(b_value)

        bounds = [(0, None) if self.non_negativity.get() else (None, None)] * self.num_vars.get()

        # Resolver
        solution = linprog(c, A_ub=A_ub or None, b_ub=b_ub or None, A_eq=A_eq or None, b_eq=b_eq or None, bounds=bounds, method="highs")

        if solution.success:
            self.display_solution(solution)
        else:
            messagebox.showerror("Error", "No se encontró una solución óptima.")

    def display_solution(self, solution):
        # Mostrar la solución
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultado")
        result_window.geometry("400x300")
        result_window.configure(bg="#f2f2f2")

        tk.Label(result_window, text="Resultado Óptimo", font=("Helvetica", 14, "bold"), bg="#f2f2f2").pack(pady=10)
        tk.Label(result_window, text=f"Valor óptimo: {solution.fun:.2f}", bg="#f2f2f2").pack(pady=10)

        for i, x in enumerate(solution.x):
            tk.Label(result_window, text=f"{self.var_names[i].get()} = {x:.2f}", bg="#f2f2f2").pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgramApp(root)
    root.mainloop()
