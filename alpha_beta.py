import tkinter as tk
import tkinter.font as tkFont

class TreeNode:
    def __init__(self, is_max):
        self.is_max = is_max
        self.children = []
        self.value = None
        self.alpha = None
        self.beta = None
        self.prev_alpha = None
        self.prev_beta = None

    def is_leaf(self):
        return len(self.children) == 0
    
    def set_value(self, oth):
        if self.value is not None:
            v1, v2 = self.value, oth.value
            self.value = max(v1, v2) if self.is_max else min(v1, v2)
        else:
            self.value = oth.value
    
    def alpha_beta_propagate_up(self, child):
        if self.is_max:
            self.prev_alpha = self.alpha
            self.prev_child_beta = child.value
            self.alpha = max(self.alpha, child.value)
        else:
            self.prev_beta = self.beta
            self.prev_child_alpha = child.value
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
        if self.value is not None:
            return str(int(self.value)) if self.value.is_integer() else str(self.value)
        else:
            return ""
    
    def alpha_beta_string(self, display_eq):
        if self.alpha is None or self.beta is None:
            return ""
        
        def to_string(f):
            if f.is_integer():
                return str(int(f))
            return str(f)

        if self.is_max and display_eq:
            alpha_string = f"max({to_string(self.prev_alpha)}, {to_string(self.prev_child_beta)}) = {to_string(self.alpha)}" 
        else:
            alpha_string = to_string(self.alpha)
        
        if not self.is_max and display_eq:
            beta_string = f"min({to_string(self.prev_beta)}, {to_string(self.prev_child_alpha)}) = {to_string(self.beta)}"
        else:
            beta_string = to_string(self.beta)

        return f"\u03B1: {alpha_string}\n\u03B2: {beta_string}"
            
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

    # sets node positions to match the center of the canvas
    def center_node(self, offset_x, offset_y):
        self.x -= offset_x
        self.y -= offset_y

        for child in self.children:
            child.center_node(offset_x, offset_y)

    # traverses the tree and returns sets of possible x and y
    def get_possible_coords(self, set_x, set_y):
        set_x.add(self.x)
        set_y.add(self.y)

        for child in self.children:
            child.get_possible_coords(set_x, set_y)

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
            is_prop_up = len(self.action_stack) > 0 and self.action_stack[-1][0] == "MOVE_UP"
            self.app.draw_tree(self.root_node, self.app.node_radius, marked_node=self.curr_node, cutoffs=self.cutoffs, is_prop_up=is_prop_up)
    
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
            self.app.draw_tree(self.root_node, self.app.node_radius, marked_node=self.curr_node, cutoffs=self.cutoffs)

    def all_backward(self):
        while len(self.action_stack):
            self.backward(draw=False)
        self.app.draw_tree(self.root_node, self.app.node_radius, marked_node=self.curr_node, cutoffs=self.cutoffs)


    def all_forward(self):
        while not self.over:
            self.forward(draw=False)
        self.app.draw_tree(self.root_node, self.app.node_radius, marked_node=self.curr_node, cutoffs=self.cutoffs) 

class MovableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.bind('<ButtonPress-1>', lambda ev: self.scan_mark(ev.x, ev.y))
        self.bind('<B1-Motion>', lambda ev: self.scan_dragto(ev.x, ev.y, gain=1))
        self.bind("<MouseWheel>", self.zoom)

    def zoom(self, ev):
        x = self.canvasx(ev.x)
        y = self.canvasx(ev.y)
        scale = 1.001 ** ev.delta
        self.scale(tk.ALL, x, y, scale, scale)

class App:
    def __init__(self):
        # main window
        self.root = tk.Tk()
        self.root.title("Alpha Beta Pruning")         

        window_width = 1024    
        window_height = 768 
        self.node_radius = 30 

        self.tree_structure_lst = None
        self.leaf_values_lst = None

        self.root.geometry(f"{window_width}x{window_height}")
        self.create_widgets()

        self.root.mainloop()

    def create_widgets(self): 
        self.widget_frame = tk.Frame(self.root)
        self.widget_frame.pack(fill=tk.X)

        # tree structure input
        self.tree_structure_label = tk.Label(self.widget_frame, text="Enter tree structure:", font=tkFont.Font(size=10))
        self.tree_structure_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.tree_structure = tk.StringVar()

        self.tree_structure_input = tk.Entry(self.widget_frame, textvariable=self.tree_structure, font=tkFont.Font(size=10), width=40)
        self.tree_structure_input.grid(row=0, column=1, padx=(0, 10), pady=10)
        # default value
        self.tree_structure_input.insert(tk.END, "2|2,2|2,2,2,2")

        def_bg = self.tree_structure_input.cget("bg")
        self.tree_structure.trace_add("write", lambda *args: self.tree_structure_input.config(bg=def_bg))

        # leaf values input
        self.leaf_values_label = tk.Label(self.widget_frame, text="Enter leaf values:", font=tkFont.Font(size=10))
        self.leaf_values_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky=tk.W)

        self.leaf_values = tk.StringVar()

        self.leaf_values_input = tk.Entry(self.widget_frame, textvariable=self.leaf_values, font=tkFont.Font(size=10), width=40)
        self.leaf_values_input.grid(row=1, column=1, padx=(0, 10), pady=(0, 10))
        # default value
        self.leaf_values_input.insert(tk.END, "11,-20,12,-10,-12,-5,-6,2")

        self.leaf_values.trace_add("write", lambda *args: self.leaf_values_input.config(bg=def_bg))

        # generate tree button
        self.generate_tree_btn = tk.Button(self.widget_frame, text="Generate tree", command=self.validate_input, font=tkFont.Font(size=10))
        self.generate_tree_btn.grid(row=0, column=2, padx=10, pady=10, sticky=tk.E+tk.W)

        # reset button
        self.reset_btn = tk.Button(self.widget_frame, text="Reset current tree", command=self.prepare_simulator, font=tkFont.Font(size=10))
        self.reset_btn.grid(row=1, column=2, padx=10, pady=(0, 10), sticky=tk.E+tk.W)

        # canvas
        self.canvas = MovableCanvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # simulation controls
        self.one_step_label = tk.Label(self.widget_frame, text="One forward / backward step:", font=tkFont.Font(size=10))
        self.one_step_label.grid(row=0, column=3, padx=(20, 10), pady=10, sticky=tk.W)

        self.backward_button = tk.Button(self.widget_frame, text="<<", font=tkFont.Font(size=10))
        self.backward_button.grid(row=0, column=4, pady=10, sticky=tk.E+tk.W)

        self.forward_button = tk.Button(self.widget_frame, text=">>", font=tkFont.Font(size=10))
        self.forward_button.grid(row=0, column=5, pady=10, sticky=tk.E+tk.W)

        self.all_steps_label = tk.Label(self.widget_frame, text="All forward / backward steps:", font=tkFont.Font(size=10))
        self.all_steps_label.grid(row=1, column=3, padx=(20, 10), pady=(0, 10), sticky=tk.W)

        self.all_backward_button = tk.Button(self.widget_frame, text="<<<", font=tkFont.Font(size=10))
        self.all_backward_button.grid(row=1, column=4, pady=(0, 10), sticky=tk.E+tk.W)

        self.all_forward_button = tk.Button(self.widget_frame, text=">>>", font=tkFont.Font(size=10))
        self.all_forward_button.grid(row=1, column=5, pady=(0, 10), sticky=tk.E+tk.W)

        # instructions
        self.instruction_btn = tk.Button(self.widget_frame, text="Instructions", command=self.show_instructions, font=tkFont.Font(size=10))
        self.instruction_btn.grid(row=0, column=6, padx=(50, 10))

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
        
        tree_str_valid = is_valid

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
            self.invalid_input(tree_str_valid)

    
    def show_instructions(self):
        instruction = tk.Toplevel(self.root)
        instruction.title("Program Instructions")
        # instruction.geometry("500x400")

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
            "If the input generates a tree that is too large for the canvas, drag the tree around\n"
            "to view different parts of the tree. You can also use mouse-wheel for zooming."
        )

        label = tk.Label(instruction, text=instruction_text, justify="left", pady=10)
        label.grid(row=0, column=0, pady=10, padx=10)

    def invalid_input(self, tree_str_valid):
        if not tree_str_valid:
            self.tree_structure_input.config(bg="IndianRed1")
        else:
            self.leaf_values_input.config(bg="IndianRed1")

    def prepare_simulator(self):
        if not self.tree_structure_lst or not self.leaf_values_lst:
            return

        root_node = TreeNode.generate_tree(self.tree_structure_lst, self.leaf_values_lst)
        
        # fixed margin
        margin_x = 90
        margin_y = 150
 
        root_node.set_position(margin_x, margin_y, margin_x, margin_y)
        root_node.center_node(root_node.x - self.canvas.winfo_width() / 2, 0)
        
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # draw initial tree
        self.draw_tree(root_node, self.node_radius)

        alpha_beta_simulator = AlphaBetaSimulator(self, root_node)

        # set buttons for controlling simulation
        self.backward_button.config(command=alpha_beta_simulator.backward)
        self.forward_button.config(command=alpha_beta_simulator.forward)

        self.all_backward_button.config(command=alpha_beta_simulator.all_backward)
        self.all_forward_button.config(command=alpha_beta_simulator.all_forward)

    # draws tree on canvas
    def draw_tree(self, root_node, radius, parent_x=None, parent_y=None, marked_node=None, cutoffs=None, cutoff=False, is_prop_up=None):
        # clear canvas
        if parent_x is None and parent_y is None:
            self.canvas.delete("all")

        self.draw_separators(root_node)
        self.draw_nodes(root_node, radius, parent_x, parent_y, marked_node, cutoffs, cutoff, is_prop_up)

    # draws nodes on canvas
    def draw_nodes(self, node, radius, parent_x=None, parent_y=None, marked_node=None, cutoffs=None, cutoff=False, is_prop_up=None):
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

            self.draw_nodes(child, radius, node.x, node.y, marked_node, cutoffs, cutoff, is_prop_up)

        # draw node as triangle
        color = "olivedrab1" if node == marked_node else ("light sky blue" if node.is_max else "IndianRed1")
        v_max = [node.x, node.y - 0.866 * radius, node.x - radius, node.y + radius, node.x + radius, node.y + radius]
        v_min = [node.x - radius, node.y - radius, node.x + radius, node.y - radius, node.x, node.y + 0.866 * radius]
        vertices = v_max if node.is_max else v_min
        
        self.canvas.create_polygon(vertices, fill=color)        
        
        # draw node value
        text_color = "red" if node == marked_node else "black"
        text_yoffset = (0.2 if node.is_max else -0.2) * radius 
        self.canvas.create_text(node.x, node.y + text_yoffset, text=node.value_string(), font=("Arial", 10, "bold"), fill=text_color)
        
        # draw alpha beta values
        display_eq = is_prop_up and node == marked_node
        self.canvas.create_text(node.x, node.y - 1.5 * self.node_radius, text=node.alpha_beta_string(display_eq), font=("Arial", 10, "bold"), fill=text_color)

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
        self.canvas.create_line(perp_x1, perp_y1, perp_x2, perp_y2, width=4, fill="red")

    # draws dotted separators between tree layers
    def draw_separators(self, root_node):
        padding = 75
        text_padding = 60

        set_x = set()
        set_y = set()
        root_node.get_possible_coords(set_x, set_y)

        min_x, max_x = min(set_x) - padding, max(set_x) + padding
        list_y = sorted(list(set_y))

        # draw separator between each layer
        for i in range(1, len(list_y)):
            y1, y2 = list_y[i - 1], list_y[i]
            y_line = (y1 + y2) / 2
            self.canvas.create_line(min_x - padding, y_line, max_x + padding, y_line, dash=(4, 2), fill="black") 
        
        # draw layer type
        for i, layer_y in enumerate(list_y):
            text = "MAX" if i % 2 == 0 else "MIN"
            self.canvas.create_text(max_x + text_padding, layer_y, text=text, font=("Arial", 12, "bold"), fill="black")
        
if __name__ == "__main__":
    app = App()