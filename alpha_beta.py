import tkinter as tk

class TreeNode:
    def __init__(self, is_max):
        self.is_max = is_max
        self.children = []
        self.value = None
        self.alpha = None
        self.beta = None

    def is_leaf(self):
        return len(self.children) == 0
    
    def set_value(self, oth):
        if self.value:
            v1, v2 = self.value, oth.value
            self.value = max(v1, v2) if self.is_max else min(v1, v2)
        else:
            self.value = oth.value
    
    def alpha_beta_propagate_up(self, child):
        if self.is_max:
            self.alpha = max(self.alpha, child.value)
        else:
            self.beta = min(self.beta, child.value)

    def alpha_beta_propagate_down(self, parent):
        self.alpha = parent.alpha
        self.beta = parent.beta

        if self.is_leaf():
            if self.is_max:
                self.alpha = self.value
            else:
                self.beta = self.value
    
    def value_string(self):
        if self.value:
            return str(int(self.value)) if self.value.is_integer() else str(self.value)
        else:
            return ""
    
    def alpha_beta_string(self):
        if self.alpha and self.beta:
            alpha_string = "- \u221E" if self.alpha == float('-inf') else (str(int(self.alpha)) if self.alpha.is_integer() else str(self.alpha))
            beta_string = "+ \u221E" if self.beta == float('inf') else (str(int(self.beta)) if self.beta.is_integer() else str(self.beta))
            return f"\u03B1: {alpha_string}\n\u03B2: {beta_string}"
        else:
            return ""

            
    # creates TreeNode structure from the given structure and leaf values
    def generate_tree(tree_structure_lst, leaf_values):
        root = TreeNode(True)
        prev_layer = [root]
        
        for layer_degrees in tree_structure_lst:
            curr_layer = []
            for i, degree in enumerate(layer_degrees):
                prev_layer[i].children = [TreeNode(not prev_layer[i].is_max) for d in range(degree)]
                curr_layer.extend(prev_layer[i].children)
            prev_layer = curr_layer
        
        # set leaf values
        for i, node in enumerate(prev_layer):
            node.value = leaf_values[i]

        return root

    # sets nodes positions (on canvas) recursively
    def set_position(self, curr_x, curr_y, margin_x, margin_y):
        if self.is_leaf():
            self.x = curr_x
            self.y = curr_y
            return curr_x + margin_x

        children_x = 0

        for child in self.children:
            curr_x = child.set_position(curr_x, curr_y + margin_y, margin_x, margin_y)
            children_x += child.x

        # set current's node position
        self.x = children_x / len(self.children)
        self.y = curr_y 

        return curr_x

class AlphaBetaSimulator:
    def __init__(self, app, root_node):
        self.app = app
        self.root_node = root_node

        self.curr_node = None
        self.curr_path = []
        self.over = False

        # maps node to index of next unvisited child 
        self.next_child = {}
        
        # stores actions to allow backward steps
        self.action_stack = []
        
        # stores current cutoffs as (parent, cutoff_idx) pairs
        self.cutoffs = []

    def forward(self, draw=True):
        if self.over:
            return

        if self.curr_node is None:
            self.curr_node = self.root_node
            self.curr_path.append(self.curr_node)
            
            self.curr_node.alpha = float('-inf')
            self.curr_node.beta = float('inf')

            self.action_stack.append(('INIT',))

        else:
            if self.curr_node.is_leaf():
                prev_node = self.curr_node
                self.curr_node = self.curr_path[-2]
                self.curr_path.pop()

                # save previous values
                prev_value = self.curr_node.value
                prev_alpha = self.curr_node.alpha
                prev_beta = self.curr_node.beta 

                # update value, alpha and beta
                self.curr_node.set_value(prev_node)
                self.curr_node.alpha_beta_propagate_up(prev_node)

                self.action_stack.append(('MOVE_UP', prev_node, prev_value, prev_alpha, prev_beta, False))

            else:
                # determine next child's index
                if self.curr_node not in self.next_child:
                    self.next_child[self.curr_node] = 0
                next_child_idx = self.next_child[self.curr_node]

                # is there a cutoff?
                cutoff = self.curr_node.alpha >= self.curr_node.beta 
                if cutoff: 
                    self.cutoffs.append((self.curr_node, next_child_idx))

                # is there any unsivised child?
                if next_child_idx < len(self.curr_node.children) and not cutoff:
                    self.next_child[self.curr_node] += 1
                    self.curr_node = self.curr_node.children[next_child_idx]
                    self.curr_path.append(self.curr_node)

                    # save previous alpha and beta
                    prev_alpha = self.curr_node.alpha
                    prev_beta = self.curr_node.beta
                    
                    # propagate alpha and beta
                    self.curr_node.alpha_beta_propagate_down(self.curr_path[-2])
                    
                    self.action_stack.append(('MOVE_DOWN', self.curr_path[-2], prev_alpha, prev_beta))

                else:
                    if self.curr_node == self.root_node:
                        self.curr_path.pop()
                        self.curr_node = None
                        self.over = True

                        self.action_stack.append(('END', cutoff))
                    
                    else:
                        prev_node = self.curr_node
                        self.curr_node = self.curr_path[-2]
                        self.curr_path.pop()

                        # save previous values
                        prev_value = self.curr_node.value
                        prev_alpha = self.curr_node.alpha
                        prev_beta = self.curr_node.beta 

                        # update value, alpha and beta
                        self.curr_node.set_value(prev_node)
                        self.curr_node.alpha_beta_propagate_up(prev_node)

                        self.action_stack.append(('MOVE_UP', prev_node, prev_value, prev_alpha, prev_beta, cutoff))

        if draw:
            self.app.draw_tree(self.root_node, 20, marked_node=self.curr_node, cutoffs=self.cutoffs)
    
    def backward(self, draw=True):
        if len(self.action_stack) == 0:
            return

        action = self.action_stack[-1][0]

        if action == 'INIT':
            self.curr_node.alpha = None
            self.curr_node.beta = None

            self.curr_node = None
            self.curr_path.pop()

            self.action_stack.pop()

        elif action == 'MOVE_DOWN':
            # reconstruct node's alpha and beta
            self.curr_node.alpha = self.action_stack[-1][2]
            self.curr_node.beta = self.action_stack[-1][3]

            # set current node and fix child indexing
            self.curr_node = self.action_stack[-1][1]
            self.next_child[self.curr_node] -= 1
            self.curr_path.pop()
            
            self.action_stack.pop()

        elif action == 'MOVE_UP':
            # reconstruct node's value, alpha and beta
            self.curr_node.value = self.action_stack[-1][2]
            self.curr_node.alpha = self.action_stack[-1][3]
            self.curr_node.beta = self.action_stack[-1][4]
            
            # set current node
            self.curr_node = self.action_stack[-1][1]
            self.curr_path.append(self.curr_node)
            
            # remove cutoff (if exists)
            if self.action_stack[-1][5]:
                self.cutoffs.pop()

            self.action_stack.pop()

        elif action == 'END':
            self.curr_node = self.root_node
            self.curr_path.append(self.curr_node)
            self.over = False
            
            # remove cutoff
            if self.action_stack[-1][1]:
                self.cutoffs.pop()

            self.action_stack.pop()

        if draw:
            self.app.draw_tree(self.root_node, 20, marked_node=self.curr_node, cutoffs=self.cutoffs)

    def all_backward(self):
        while len(self.action_stack):
            self.backward(draw=False)
        self.app.draw_tree(self.root_node, 20, marked_node=self.curr_node, cutoffs=self.cutoffs)


    def all_forward(self):
        while not self.over:
            self.forward(draw=False)
        self.app.draw_tree(self.root_node, 20, marked_node=self.curr_node, cutoffs=self.cutoffs) 

class App:
    def __init__(self):
        # main window
        self.root = tk.Tk()
        self.root.title("Alpha Beta Pruning")         

        self.window_width = 1500
        self.window_height = 900

        self.tree_structure_lst = None
        self.leaf_values_lst = None

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        self.create_widgets()

        self.root.mainloop()

    def create_widgets(self):
        # tree structure input
        tk.Label(self.root, text="Enter tree structure: ").place(x=20, y=20, width=120, height=20)

        self.tree_structure = tk.StringVar()

        self.tree_structure_input = tk.Entry(self.root, textvariable=self.tree_structure)
        self.tree_structure_input.place(x=160, y=20, width=300, height=20)
        # default value
        self.tree_structure_input.insert(tk.END, "3|3,3,3|3,3,3,3,3,3,3,3,3")

        # leaf values input
        tk.Label(self.root, text="Enter leaf values: ").place(x=20, y=50, width=120, height=20)

        self.leaf_values = tk.StringVar()

        self.leaf_values_input = tk.Entry(self.root, textvariable=self.leaf_values)
        self.leaf_values_input.place(x=160, y=50, width=300, height=20)
        # default value
        self.leaf_values_input.insert(tk.END, "-11,-20,5,-10,-12,-5,-6,2,3,-18,12,-1,12,12,4,6,-16,14,-1,-2,-7,-8,18,2,6,7,-13")

        # generate tree button
        self.generate_tree_btn = tk.Button(self.root, text="Generate tree", command=self.validate_input)
        self.generate_tree_btn.place(x=480, y=20, width=100, height=20)

        # reset button
        self.reset_btn = tk.Button(self.root, text="Reset current tree", command=self.prepare_simulator)
        self.reset_btn.place(x=480, y=50, width=100, height=20)

        # canvas
        self.canvas = tk.Canvas(self.root, bg='white')
        self.canvas.place(x=0, y=100, width=self.window_width-20, height=self.window_height-120)

        scroll_y = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scroll_y.place(x=self.window_width-20, y=100, width=20, height=self.window_height-100)

        scroll_x = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        scroll_x.place(x=0, y=self.window_height-20, width=self.window_width-20, height=20)

        # simulation controls
        tk.Label(self.root, text="One forward / backward step: ").place(x=650, y=20, width=160, height=20)

        self.backward_button = tk.Button(self.root, text="<<")
        self.backward_button.place(x=830, y=20, width=40, height=20)

        self.forward_button = tk.Button(self.root, text=">>")
        self.forward_button.place(x=870, y=20, width=40, height=20)

        tk.Label(self.root, text="All forward / backward steps: ").place(x=650, y=50, width=160, height=20)

        self.all_backward_button = tk.Button(self.root, text="<<<")
        self.all_backward_button.place(x=830, y=50, width=40, height=20)

        self.all_forward_button = tk.Button(self.root, text=">>>")
        self.all_forward_button.place(x=870, y=50, width=40, height=20)

        # instrctions
        self.instruction_btn = tk.Button(self.root, text="Instructions", command=self.show_instructions)
        self.instruction_btn.place(x=1000, y=20, width=100, height=20)

    def validate_input(self):
        tree_structure_str = self.tree_structure.get()
        leaf_values_str = self.leaf_values.get()

        is_valid = True 

        # validate tree structure input
        tree_structure_lst = []
        layers = tree_structure_str.split("|")
        expected_no_nodes = 1

        for l, layer in enumerate(layers):
            tree_structure_lst.append([])
            layer_degrees = layer.split(",")
            # degree counts from upper layers should match with current layer
            if len(layer_degrees) != expected_no_nodes:
                is_valid = False

            degree_count = 0
            # each degree must be an (positive) integer
            for deg in layer_degrees:
                if deg.isnumeric() and int(deg) > 0:
                    degree_count += int(deg)
                    tree_structure_lst[-1].append(int(deg))
                else:
                    is_valid = False
            expected_no_nodes = degree_count
        
        leaf_values = []
        leafs = leaf_values_str.split(",")
        # number of leafs should match degree count from last layer
        if len(leafs) != expected_no_nodes:
            is_valid = False
        
        def is_number(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        for l, leaf in enumerate(leafs):
            if not is_number(leaf):
                is_valid = False
            else:
                leaf_values.append(float(leaf))

        if is_valid:
            print('input is valid!')
            self.tree_structure_lst = tree_structure_lst
            self.leaf_values_lst = leaf_values
            self.prepare_simulator()
        else:
            print('input is not valid!')
            self.invalid_input()

    
    def show_instructions(self):
        instruction = tk.Toplevel(self.root)
        instruction.title("Program Instructions")
        instruction.geometry("500x400")
        instruction.resizable(False, False)

        instruction_text = (
            "Generate Tree:\n"
            "To create a tree, provide both the tree structure and leaf values.\n\n"
            "Tree Structure:\n"
            "Define the number of children for nodes in each layer. For instance, use the format\n"
            "'n|m1,m2,m3' where 'n' is the number of children for the root node, and 'm1,m2,m3'\n"
            "represent the number of children for the nodes in the next layer. Example: '3|3,3,3'\n"
            "signifies that the root node has 3 children, and each of those children has 3 children\n"
            "as well.\n\n"
            "Leaf Values:\n"
            "Input a list of numbers (possibly decimals) separated by commas. For the previously\n"
            "mentioned tree structure, an example would be: '-11,4,3,1.5,1,-5.3,7,-10,20'.\n\n"
            "Ensure that the input is semantically valid; otherwise, the tree cannot be generated.\n\n"
            "Alpha Beta Pruning Simulation:\n"
            "After generating a tree, simulate Alpha Beta pruning by clicking on '<<' and '>>'.\n\n"
            "Handling Large Trees:\n"
            "If the input generates a tree that is too large for the canvas, navigate using the scrollbar\n"
            "buttons to view different parts of the tree."
        )

        label = tk.Label(instruction, text=instruction_text, justify="left", pady=10)
        label.pack()

    def invalid_input(self):
        error = tk.Toplevel(self.root)
        error.title("Program Instructions")
        error.geometry("300x100")
        error.resizable(False, False)

        error_text = (
            "Given input is invalid!\n\n"
            "Please check the instructions for the correct format."
        )

        label = tk.Label(error, text=error_text, justify="left", pady=10)
        label.pack()

    def prepare_simulator(self):
        if not self.tree_structure_lst or not self.leaf_values_lst:
            return

        root_node = TreeNode.generate_tree(self.tree_structure_lst, self.leaf_values_lst)
        
        # determine canvas size for fixed margin
        margin_x = 50
        margin_y = 150
        canvas_width = margin_x * (len(self.leaf_values_lst) + 1)
        canvas_height = margin_y * (len(self.tree_structure_lst) + 2)
        self.canvas.config(width=canvas_width, height=canvas_height)

        root_node.set_position(margin_x, margin_y, margin_x, margin_y)
        # draw initial tree
        self.draw_tree(root_node, 20)

        alpha_beta_simulator = AlphaBetaSimulator(self, root_node)

        # set buttons for controlling simulation
        self.backward_button.config(command=alpha_beta_simulator.backward)
        self.forward_button.config(command=alpha_beta_simulator.forward)

        self.all_backward_button.config(command=alpha_beta_simulator.all_backward)
        self.all_forward_button.config(command=alpha_beta_simulator.all_forward)

    # draws tree on canvas
    def draw_tree(self, node, radius, parent_x=None, parent_y=None, marked_node=None, cutoffs=None, cutoff=False):
        # clear canvas on initial call
        if parent_x is None and parent_y is None:
            self.canvas.delete("all")

        # connect node with parent
        if parent_x is not None and parent_y is not None:
            self.canvas.create_line(parent_x, parent_y, node.x, node.y, width=1, fill="black")

        # draw cutoff line 
        if cutoff:
            self.draw_perpendicular_line(parent_x, parent_y, node.x, node.y)

        for i, child in enumerate(node.children):
            # determine if there is a cutoff
            cutoff = False
            for cutoff_pair in cutoffs or []:
                if cutoff_pair[0] == node and cutoff_pair[1] <= i:
                    cutoff = True

            self.draw_tree(child, radius, node.x, node.y, marked_node, cutoffs, cutoff)

        # draw node as circle
        color = "olivedrab1" if node == marked_node else ("light sky blue" if node.is_max else "IndianRed1")
        self.canvas.create_oval(node.x - radius, node.y - radius, node.x + radius, node.y + radius, fill=color)
        # draw node value
        text_color = "red" if node == marked_node else "black"
        self.canvas.create_text(node.x, node.y, text=node.value_string(), font=("Arial", 12, "bold"), fill=text_color)
        # draw alpha beta values
        self.canvas.create_text(node.x, node.y - 40, text=node.alpha_beta_string(), font=("Arial", 12, "bold"), fill=text_color)

    def draw_perpendicular_line(self, x1, y1, x2, y2, length=10):
        # direction of the original line
        dx = x2 - x1
        dy = y2 - y1

        # perpendicular direction
        perp_dx = -dy
        perp_dy = dx

        # normalize perpendicular direction
        perp_length = (perp_dx ** 2 + perp_dy ** 2) ** 0.5
        perp_dx /= perp_length
        perp_dy /= perp_length

        # calculate endpoints of the perpendicular line
        x_center = x1 + (x2 - x1) / 2
        y_center = y1 + (y2 - y1) / 2

        perp_x1 = x_center + perp_dx * length
        perp_y1 = y_center + perp_dy * length
        perp_x2 = x_center - perp_dx * length
        perp_y2 = y_center - perp_dy * length

        # draw perpendicular line
        self.canvas.create_line(perp_x1, perp_y1, perp_x2, perp_y2, width=3, fill="red")

if __name__ == "__main__":
    app = App()