""" full fault list generator for a circuit.bench file
"""
from re import match  # re = REGULAR EXPRESSION, helps with parser

""" NODE class:
name : 'wire' that is the output of the node, 
g_type: INPUT, OUTPUT, 'GATE NAME' from bench file
inputs: list of all input wires' names
io : if the node is a PI or PO
"""

class Node(object):

    def __init__(self, name: str, g_type: str, inputs,io):
        self.input_names = inputs
        self.name = name
        self.gate_type = g_type
        self.faults = []
        self.IO = io


    def generate_faults(self):
        if self.gate_type == "INPUT":

            s = ''
            for i in range(2):
                s = f"{self.name}-{i}"
                self.faults.append(s)

            #print(self.faults)

        elif self.gate_type == "OUTPUT":
            s = ''
            for i in range(2):
                s = f"{self.name}-{i}"
                self.faults.append(s)
            #print(self.faults)

        else:
            s = ""
            if not self.IO:
                for i in range(2):
                    s = f"{self.name}-{i}"
                    self.faults.append(s)

            for in_name in self.input_names:
                for i in range(2):
                    s = f"{self.name}-{in_name}-{i}"
                    self.faults.append(s)
            #print(self.faults)

            pass

    def __str__(self):
        s = f"name {self.name} gate_type: {self.gate_type}"

        if self.input_names:
            s += "\nin_terms: "
            for i in range(len(self.input_names)):
                s += f"{self.input_names[i]} "

        s += "\n\n"
        return s

# class PINode(Node):
#     def __init__(self):
#         super(self)


class FFA(object):
    class LineParser(object):
        def __init__(self, bench):
            self.file = bench
            self.pattern_gate = "(\S+) = ([A-Z]+)\((.+)\)"
            self.pattern_io = "([A-Z]+)\((.+)\)"
            self.Nodes = []  # array of NODES class
            self.input_names = []
            self.output_names = []
            self.PI = 0
            self.PO = 0
            self.gates_n = 0
            self.gates_w = 0

            # self.gate_map = {"AND": nodes.AndGate, "OR": nodes.OrGate, "NAND": nodes.NandGate, "XNOR": nodes.XnorGate,
            #                 "NOR": nodes.NorGate, "BUFF": nodes.BuffGate, "XOR": nodes.XorGate, "NOT": nodes.NotGate}


        def parse_file(self):
            worked = 1
            try:
                with open(self.file) as f:
                    for line in f:
                        self.parse_line(line)


            except FileNotFoundError:
                worked = 0
                # print(f"NO FILE FOUND in Project 2/{self.file}")
                # exit ()
            if not worked:
                try:
                    with open('benches/'+self.file) as f:
                        for line in f:
                            self.parse_line(line)

                except FileNotFoundError:
                    pass
                    # print(f"NO FILE FOUND ->{self.file}")
                    # exit ()


            return self

        def parse_line(self, line: str):
            if groups := match(self.pattern_gate, line):
                name = groups.group(1)
                gate_type = groups.group(2)

                # gate_type = self.gate_map[groups.group(2)]
                if not gate_type:
                    print(f"Gate not found @ {line}\n")
                    # raise exceptions.ParseLineError(line)
                inputs = groups.group(3).split(', ')
                self.gates_n += 1
                self.gates_w += len(inputs) + 1
                if name in self.input_names or name in self.output_names:
                    self.Nodes.append(Node(name, gate_type, inputs,1))
                else:
                    self.Nodes.append(Node(name, gate_type, inputs, 0))
            elif groups := match(self.pattern_io, line):

                io = groups.group(1)
                name = groups.group(2)
                # print(io,name)
                if io == "INPUT":
                    self.PI += 1
                    self.input_names.append(name)
                    self.Nodes.append(Node(name, io, None,1))
                    # self.gates.append(nodes.Gate(name))
                elif io == "OUTPUT":
                    self.PO += 1
                    self.output_names.append(name)
                    # self.output_names.append(Gate(name,io,None))
                    self.Nodes.append(Node(name, io, None,1))
                else:
                    print(f"incorrect input / output @ {line}\n")
                    # raise exceptions.ParseLineError(line)
            elif line.startswith('#') or line == '\n':
                pass
            else:
                print(f"error in {line}")
                # raise exceptions.ParseLineError(line)

        def __str__(self):
            print(f"input Names: {self.input_names}\noutput Names: {self.output_names}")
            s = "Gate info: \n"
            for i in range(len(self.Nodes)):
                s += self.Nodes[i].__str__()
            return s

    def __init__(self, filename):
        self.f = filename
        self.parser = self.LineParser(filename)
        self.parser.parse_file()
        self.Node_list = self.parser.Nodes
        self.Input_names = self.parser.input_names
        self.Output_names = self.parser.output_names

        self.PIs = self.parser.PI
        self.POs = self.parser.PO
        self.N_gates = self.parser.gates_n
        self.W_gates = self.parser.gates_w
        self.FFA = [] # full fault with sub arrays
        self.FFLIST= [] # full fault as 1 array

    # generate full fault list
    def gate_faults(self):
        for gate in self.Node_list:
            #if gate.gate_type != "OUTPUT": # avoid dupes
            gate.generate_faults()
            self.FFA.append(gate.faults)

        for subFault in self.FFA:
            for fault in subFault:
                self.FFLIST.append(fault)


    # print Full fault list
    def display_faults(self):
        c = 0
        for fault in self.FFLIST:

            if c % 10 == 0:
                print("")
            if c < len(self.FFLIST) - 1:
                print(fault, end=", ")
            else:
                print(fault, end = " ")
            c += 1
        print(f"\nA total Fault count = {c}")

    def write_faults(self):
        f = open(self.f + '-FFL','w+')
        f.write(f'Fault Count: {len(self.FFLIST)}\n')
        c = 0
        s = ''
        for fault in self.FFLIST:
            s += fault + ' '
            if c % 15 == 0 and c != 0:
                f.write(s)
                f.write("\n")
                s = ''
            c+= 1
            # f.write(fault)


        f.close()

    def __str__(self):
        print(f"Node info\nInput nodes: {self.Input_names}\nOutput nodes: {self.Output_names}")
        print("FULL FAULT LIST\n")
        print(f"PI: {self.PIs}  PO: {self.POs}  gates: {self.N_gates} with {self.W_gates} wires around")
        print(f"expected faults: ( {self.PIs} + {self.W_gates} ) * 2 = {(self.PIs +self.W_gates) * 2}")

        print(self.FFLIST)
        # c = 0
        # for f in self.FFA:
        #     for g in f:
        #         print(g)
        #         c +=1
        print(f"fault count: {len(self.FFLIST)}")
        return "\n"
        # print(self.Fault_list)
# if __name__ == '__main__':
#     #f = input("enter .bench filename\n")
#     f = "circuit.bench"
#     Fault_List = FFA(f)
#     Fault_List.gate_faults()
#     print(Fault_List)
#     #print( Fault_List.parser)
