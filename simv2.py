import copy
import os
import time
from inputs import TVs as TVs
from FFL import FFA as FFA


# combination of projects... for v2
# Class used to store information for a wire

class Node(object):


    def __init__(self, name, value, gatetype, innames):
        self.name = name  # string
        self.value = value  # char: '0', '1', 'U' for unknown
        self.gatetype = gatetype  # string such as "AND", "OR" etc
        self.interms = []  # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
        self.is_input = False  # boolean: true if this wire is a primary input of the circuit
        self.is_output = False  # boolean: true if this wire is a primary output of the circuit

        self.has_fault = False # Not used

    def set_value(self, v):
        self.value = v

    def display(self):  # print out the node nicely on one line
        if self.is_input:
            # nodeinfo = f"input:\t{str(self.name[4:]):5} = {self.value:^4}"
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}"
            print(nodeinfo)
            return
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
        else:  # internal nodes
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"
        interm_str = " "
        interm_val_str = " "
        for i in self.interms:
            interm_str += str(i.name) + " "
            interm_val_str += str(i.value) + " "
        nodeinfo += f"as {self.gatetype:>5}"
        nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"
        print(nodeinfo)
        return

    #currently using Steve's calculate value
    def calculate_value(self):
        count0 = 0
        count1 = 0
        countU = 0

        # for i in self.interms:  # skip calculating unless all interms have specific values 1 or 0
        #     if i.value != "0" and i.value !="1":
        #         return "U"

        # TODO  Need to reformat all the gates to work with the Unknowns.
        # The way we should do this is use the "count"

        if self.gatetype == "AND":
            for i in self.interms:
                if i.value == "0":
                    count0 += 1
                if i.value == "U":
                    countU += 1
                if i.value == "1":
                    count1 += 1
                if count0 > 0:
                    val = "0"
                if count0 == 0 and count1 == 0:
                    val = "U"
                if count0 == 0 and countU == 0:
                    val = "1"
                if count0 == 0 and count1 > 0 and countU > 0:
                    val = "U"
            self.value = val
            return val


        # if self.gatetype == "AND":
        #     val = "1"
        #     for i in self.interms:
        #         if i.value == "0":
        #             val = "0"
        #     self.value = val
        #     return val
        elif self.gatetype == "OR":
            for i in self.interms:
                if i.value == "0":
                    count0 += 1
                if i.value == "U":
                    countU += 1
                if i.value == "1":
                    count1 += 1
                if count1 > 0:  # 1 ORed with anything is a 1
                    val = "1"
                if count1 == 0 and countU > 0:
                    val = "U"
                if count0 > 0 and count1 == 0 and countU == 0:
                    val = "0"
            self.value = val
            return val

            # val = "0"
            # for i in self.interms:
            #     if i.value == '1':
            #         val = "1"
            # self.value = val
            # return val
        elif self.gatetype == "NAND":
            for i in self.interms:
                if i.value == "0":
                    count0 += 1
                if i.value == "U":
                    countU += 1
                if i.value == "1":
                    count1 += 1
                if count0 > 0:
                    val = "1"
                if count0 == 0 and count1 == 0:
                    val = "U"
                if count0 == 0 and countU == 0:
                    val = "0"
                if count0 == 0 and count1 > 0 and countU > 0:
                    val = "U"
            self.value = val
            return val
            # flag = "1"
            # for i in self.interms:
            #     if i.value == "0":
            #         flag = "0"
            # val = str(1 - int(flag))
            # self.value = val
            # return val
        elif self.gatetype == "NOT":
            for i in self.interms:
                if i.value == "U":
                    val = "U"
                    return val
                else:
                    val = self.interms[0].value
                    self.value = str(1 - int(val))
                    return val
        elif self.gatetype == "XOR":
            num_of_1 = 0
            for i in self.interms:
                if i.value == "U":
                    val = "U"
                    return val
                elif i.value == "1":
                    num_of_1 = num_of_1 + 1
            val = num_of_1 % 2
            val = str(val)
            self.value = val
            return val
        elif self.gatetype == "XNOR":
            num_of_1 = 0
            for i in self.interms:
                if i.value == "U":
                    val = "U"
                    return val
                elif i.value == "1":
                    num_of_1 = num_of_1 + 1
            val = num_of_1 % 2
            self.value = str(1 - val)
            return val
        elif self.gatetype == "NOR":
            for i in self.interms:
                if i.value == "0":
                    count0 += 1
                if i.value == "U":
                    countU += 1
                if i.value == "1":
                    count1 += 1
                if count1 > 0:  # 1 ORed with anything is a 1
                    val = "0"
                if count1 == 0 and countU > 0:
                    val = "U"
                if count0 > 0 and count1 == 0 and countU == 0:
                    val = "1"
            self.value = val
            return val
            # flag = "0"
            # for i in self.interms:
            #     if i.value == "1":
            #         flag = "1"
            # val = str(1 - int(flag))
            # self.value = val
            # return val
        elif self.gatetype == "BUFF":
            val = self.interms[0].value
            self.value = val
            return val


# circuit object:
# contains node list
#TODO: Extend to auto generate faults, and inputs, then simulate those
class Circuit(object):



    def __init__(self):
        # .bench file vars
        self.Bench_name = ''
        self.Benchfile = ''
        self.Bench_str = ""
        self.input_bench_vals = None # list of raw bench file

        self.MAIN_node_list = []
        # parsed circuit vars
        self.cur_input = ''
        self.cur_fault = ''
        self.cur_tv_index = 0

        self.Node_list = []
        #circuit info
        self.Input_names = []
        self.Output_names = []

        #Test vector generated inputs
        #self.TV_List = TVs()

        #input TV info
        self.input_TV_list = [] # list of auto generated inputs
        self.user_TV = ''


        #input Fault info
        self.Fault_Node_list = []
        self.with_fault = None #bool : is fault input
        self.Fault_input_list = None # parsed Fault as list of items
        self.Faulty_Node = None # should this be a node object? !
        self.Fault_Index = None # index within node list for faulty node
        self.Fault_interm_index = None
        self.Fault_TYPE = -1 # 1 for single stuck at , 2 for from -stuck at
        self.Fault_added = False

        self.Full_Fault_List = [] # holds all the faults generated from bench



        #simulation
        self.Is_Running = False
        self.tv_mode = {"user_input":False, "auto":False } # differnt simulation modes/states
        self.print_iteration = False # the debug mode

        # variable for results
        self.Final_results = []
        self.detected = {}
        self.undetected = {}
        self.coverage = {}


    # parser of bench file
    def parse_gate(self, rawline):
        # example rawline is: a' = NAND(b', 256, c')

        # should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']

        # get rid of all spaces
        line = rawline.replace(" ", "")
        # now line = a'=NAND(b',256,c')

        name_end_idx = line.find("=")
        node_name = line[0:name_end_idx]
        # now node_name = a'

        gt_start_idx = line.find("=") + 1
        gt_end_idx = line.find("(")
        node_gatetype = line[gt_start_idx:gt_end_idx]
        # now node_gatetype = NAND

        # get the string of interms between ( ) to build tp_list
        interm_start_idx = line.find("(") + 1
        end_position = line.find(")")
        temp_str = line[interm_start_idx:end_position]
        tp_list = temp_str.split(",")
        # now tp_list = [b', 256, c]

        node_innames = [i for i in tp_list]
        # now node_innames = [b', 256, c]

        return node_name, node_gatetype, node_innames

    # builds node list from bench file
    def construct_nodelist(self):
        #print("\t.....Constructing node list\t.....")
        o_name_list = []

        for line in self.input_bench_vals:
            if line == "\n":
                continue

            if line.startswith("#"):
                continue

            # TODO: clean this up
            if line.startswith("INPUT"):
                index = line.find(")")
                # intValue = str(line[6:index])
                name = str(line[6:index])
                n = Node(name, "U", "PI", [])
                n.is_input = True
                self.MAIN_node_list.append(n)
                #self.Node_list.append(n)
                self.Input_names.append(name)


            elif line.startswith("OUTPUT"):
                index = line.find(")")
                name = line[7:index]
                o_name_list.append(name)
                self.Output_names.append(name)


            else:  # majority of internal gates processed here
                node_name, node_gatetype, node_innames = self.parse_gate(line)
                n = Node(node_name, "U", node_gatetype, node_innames)
                #self.Node_list.append(n)
                self.MAIN_node_list.append(n)

        # now mark all the gates that are output as is_output
        #for n in self.Node_list:
        for n in self.MAIN_node_list:
            if n.name in o_name_list:
                n.is_output = True

        # link the interm nodes from parsing the list of node names (string)
        # example: a = AND (b, c, d)
        # thus a.innames = [b, c, d]
        # node = a, want to search the entire node_list for b, c, d
        #for node in self.Node_list:
        for node in self.MAIN_node_list:
            for cur_name in node.innames:
                #for target_node in self.Node_list:
                for target_node in self.MAIN_node_list:
                    if target_node.name == cur_name:

                        node.interms.append(target_node)

        return

    def add_faulty_node(self): # modiefies only Fault list
        v= ''

        # print(self.Fault_input_list)
        if self.Fault_input_list[2] == 1 or self.Fault_input_list[2] == "1":
            v = "1"
        else:
            v = "0"

        self.Faulty_Node = copy.deepcopy(self.Fault_Node_list[self.Fault_Index].interms[self.Fault_interm_index])

        self.Faulty_Node.value = v

        self.Fault_Node_list[self.Fault_Index].interms[self.Fault_interm_index] = self.Faulty_Node
        self.Fault_added = True

    # returns list of how fault is input,
    # ex: a-1 -> ['a','1']
    # g-a-1 -> ['g','a','1']
    def parse_fault(self,in_fault):

        raw_fault = in_fault.split('-')
       # print(raw_fault)
        if len(in_fault) == 0:
            return None
        if len(raw_fault) > 3:
            print("invalid fault input | Try again?\n")
            return False
            # self.input_fault()

        if raw_fault[len(raw_fault) -1] != "0" and raw_fault[len(raw_fault) -1] != "1":
            print(f"{ raw_fault[len(raw_fault) - 1] } is not a valid Fault Value | try again?\n")
            return False
            # self.input_fault()

        #debug tool
        #print(raw_fault,"has length: ",len(raw_fault))

        f_n = ''
        from_inname = ''
        f_val = ''
        fault_type = -1
        if len(raw_fault) == 2:
            f_n = raw_fault[0]
            f_val = raw_fault[1]
            fault_type = 1
            self.Fault_TYPE = 1
        else:
            f_n = raw_fault[0]
            from_inname = raw_fault[1]
            f_val = raw_fault[2]
            fault_type = 2
            self.Fault_TYPE = 2

        fault_node_found = 0
        fault_index = 0
        #for n in self.Node_list:
        for n in self.MAIN_node_list:
            if n.name == f_n:
                fault_node_found = 1
                break
            fault_index += 1


        if fault_node_found:
            if fault_type == 1:
                self.Fault_Index = fault_index
                return [f_n,f_val]

            if fault_type == 2:
                found_interm = 0
                interm_index = 0

                #if self.Node_list[fault_index].is_input:
                if self.MAIN_node_list[fault_index].is_input:
                    print(f"PI can not have from fault")
                    return False

                # for interm in self.Node_list[fault_index].interms:
                for interm in self.MAIN_node_list[fault_index].interms:
                    if from_inname == interm.name:
                        found_interm = 1
                        break
                    interm_index += 1

                if found_interm:

                    self.Fault_Index = fault_index
                    self.Fault_interm_index = interm_index
                    return [f_n,from_inname,f_val]
                else:
                    print(f"interm {from_inname} not found @ NODE:")
                    # self.Node_list[fault_index].display()
                    self.MAIN_node_list[fault_index].display()

                    return False


        else:# node not found, try again
            print(f"Node {f_n} not found")
            return False





    def input_fault(self):

        s = "Run with fault?\n"
        s += "for single fault: name-val ex: a SA 1 = a-1\n"
        s += "for output fault from node: output-from-val ex: g-a-1\n"
        s += f"(enter) for none"
        print(s)
        input_fault = str(input(">"))


        # a-1 -> [ 'a', '1' ]
        # g-a-1-> [ 'g' , 'a' , '1']
        c_len = len(input_fault)
        if c_len == 0:
            self.with_fault = False
            self.Fault_input_list = None
            return

        self.Fault_input_list = self.parse_fault(input_fault)

        # print(self.Fault_input)
        while not self.Fault_input_list and c_len != 0:
            print("Invalid input - Try again")
            input_fault = str(input(">"))
            c_len = len(input_fault)
            self.Fault_input_list = self.parse_fault(input_fault)

        self.with_fault = True


    def input_prompt(self):
        print(f"\nProvide a {len(self.Input_names)}-bit vector for input nodes:")
        # print("PIs: ",*self.Input_names)
        # print("(auto) for auto generated inputs")
        print("(exit or return) to exit")
        choice = str( input(">") )

        c_len = len(choice)
        # print(c_len)

        if c_len == 0 or choice == "exit" or choice == "return":
            self.Is_Running = False
            return True

        if c_len > len(self.Input_names): # too many inputs, try again
            print("Inputs larger than bench inputs, try again")
            self.input_prompt()

        self.user_TV = choice

        self.input_fault()


    # comes in as list [ a , 1] or [g, a ,1]
    def display_fault(self,f_list):
        print("With Fault:", end = " ")
        if self.Fault_TYPE == 1:
            print(f"{f_list[0]}-SA-{f_list[1]}")

        elif self.Fault_TYPE == 2:
            print(f"{f_list[0]}-{f_list[1]}-{f_list[2]}")
        else :
            print("INVALID FAULT , exiting")
            exit(1)

    def display_inputs_nodes(self,nodelist):
        print("-------------------------------------------")
        print("simulating with the following input values:")

        for node in nodelist:
            if node.is_input:
                node.display()

        #if self.with_fault:
        #    self.display_fault(self.Fault_input_list)


        print("\n-------------------------------------------\n")


    def set_bench(self):

        benchL = os.listdir('benches')
        s = f"Select from the following bench files? or input a bench file\n"
        for i in range(len(benchL)):
            s += f"({i}) {benchL[i]}\n"

        print(s,end="")
        bench_file = str(input("Enter a bench file (circuit.bench by default)\n>"))
        if bench_file.isdigit():
            try:
                name = 'benches/'+benchL[int(bench_file)]
                f = open(name)
                f.close()
                self.Bench_name = name
                self.Bench_str = benchL[int(bench_file)]
            except FileNotFoundError:
                print("File not found or does not exist in benches/ , default set")
                self.Bench_name = "circuit.bench"
                self.Bench_str = "circuit.bench"
            #except NotADirectoryError:
        elif len(bench_file) != 0:
            try:
                f = open(bench_file)
                f.close()
                self.Bench_name = bench_file
                self.Bench_str = bench_file
            except FileNotFoundError:

                print("File not found or does not exist, default set")

                self.Bench_name  = "circuit.bench"
                self.Bench_str = "circuit.bench"
        else:
            self.Bench_name = "circuit.bench"
            self.Bench_str = "circuit.bench"

        print(f"Loaded Circut: {self.Bench_name}")

    def simulate_nodes(self,nodelist):
        updated_count = 1  # initialize to 1 to enter while loop at least once
        iteration = 0
        while updated_count > 0:
            updated_count = 0
            iteration += 1
            for n in nodelist:
                # print("\n\nnode: " + str(n.name) + " , ASCII value = " + str(ord(n.name)) + " , value: " + str(n.value))
                if n.value == "U":
                    n.calculate_value()
                    if n.value == "0" or n.value == "1":
                        updated_count += 1

                if self.print_iteration: #TODO: ADD A STEP THROUGH ITERATION
                    n.display()
            if self.print_iteration:
                print(f'--- iteration {iteration} finished: updated {updated_count} values--- ')




    # compare the outputs of both node list and fault node list and check for diff
    # populates dictionary for detected and undetected list of each input
    def Detect_fault(self,normal,faulty):
        output_val = [n.value for n in normal if n.is_output]

        faulty_output_val = [n.value for n in faulty if n.is_output]
        # circuit_all = open("circuit_all","w")

        if output_val != faulty_output_val:
            s = f"Fault {self.cur_fault} Detected by {self.cur_input}"
            #print(s)
            if self.cur_input in self.detected.keys():
                self.detected[self.cur_input].append(self.cur_fault)
                #  circuit_all.write(self.cur_fault+", ")
            else:
                self.detected[self.cur_input] = []
                self.detected[self.cur_input].append(self.cur_fault)
                # circuit_all.write(self.cur_input+", ")
            return True
        else:
            s = f"Fault {self.cur_fault} UNDetected by {self.cur_input}"
            #print(s)
            if self.cur_input in self.undetected.keys():
                self.undetected[self.cur_input].append(self.cur_fault)
            else:
                self.undetected[self.cur_input] = []
                self.undetected[self.cur_input].append(self.cur_fault)
            return False


    def print_results_nodes(self,nodeList):
        input_vals = [i.value for i in nodeList if i.is_input]
        print("\n--- Simulation Results  ---")
        print("input: \t", *self.Input_names, end="")
        print("\t = \t", end="")
        print(*input_vals)

        output_vals = [i.value for i in nodeList if i.is_output]

        print("output:\t", *self.Output_names, end="")
        print("\t = \t", *output_vals)
        # print("------------------------------------")

    def Fault_coverage(self):
        F = copy.deepcopy(self.Full_Fault_List)
        T = self.input_TV_list

      #  report = open("resuls.txt","w")

        print("-------------------------------------")
        for t in T:
            D = []
            print(f"tv {t} detects the following ",end=  "")
            for f in F:
                if f in self.detected[t]:
                    # print(t, "detects",f)
                    D.append(f)

            self.coverage[t] = []
            self.coverage[t] = D

            print(f"{len(D)} Faults:\n"\
                  f"{D}"
                  )
            for covered in D:
                if (fault:= F.index(covered) ) != -1:
                    # print(covered,fault)
                    F.pop(fault)
                   # F.remove(fault)

            print(f"with {len(F)} Remaining Faults:\n{F}")
            print("-------------------------------------")

    # all the dictionarys will store (Key,Value) as:
    # "key" , [Values]
    def write_to_csv(self,filename,d):
        try:
            #filename = filename[:filename.index('.')]
            f = open("Fault_results/"+filename+'.csv',"w")
        except NotADirectoryError:
            print("directory not found")
      #  s = ','
        #f.write(self.input_name+"\n")
        for k,v in d.items():

            f.write(k+", ")

            s = ', '.join(v)
            #print(s)
            f.write(s+"\n")

    def generate_plot_data(self):

        x_axis = []
        y_axis = []
        length_covered = 0

        #for i in range(10):
        counter = 1

        for k,v in self.coverage.items(): # .items => [key,value]

            if counter %10 == 0: # add to a new x value
                x_axis.append(counter // 10)
                y_axis.append( length_covered / len(self.Full_Fault_List) * 100 )

            length_covered += len(v)
            counter+= 1
        # if we used < 100 tvs,
        # counter+=1
        #if counter % 10 < 10: # counter = 32 % 10 => 3 < 10 ( TV list < 100)
        if counter < 100:
            for i in range(counter, 100, 10):
                x_axis.append(i // 10)
                y_axis.append(length_covered / len(self.Full_Fault_List) * 100 )



        return x_axis,y_axis





    def print_node(self,node_list):
        for node in node_list:
            node.display()
        print("------------------")

    def run(self):

        # set up circuit bench file
        self.set_bench()
        self.Benchfile = open(self.Bench_name,'r')
        self.input_bench_vals = self.Benchfile.readlines()
        self.Benchfile.close()
        # print(self.input_bench_vals)

        # build node-list network
        self.construct_nodelist()
        #self.print_node(self.MAIN_node_list)



        s1 = f"How would you like to run simulator?\n" \
             f"(1) user input\n" \
             f"(2) generated inputs? " \
             f"default = (1)\n>"
        ui = True
        tv_choice = int(input(s1))
        if tv_choice == 2:
            ui = False
        #elif tv_choice == 2:

        # generating Fault list
        if not ui:
            FAULTS = FFA(self.Bench_name)
            FAULTS.gate_faults()
            self.Full_Fault_List = FAULTS.FFLIST

            print("--- Derived Full fault list: ---")
            FAULTS.display_faults()
            print("--------------------------------")

        input_index = 0
        fault_index = 0
        p_index = 0
        generated = False
        input_name = ""
        got_time =True


        # how to run sim #TODO : impliment  different sim modes : auto run, print every iteration, ..
        # self.set_mode()
        self.Is_Running = True

        # main simulation loop
        while self.Is_Running:

            # check if done?!



            del self.Node_list
            del self.Fault_Node_list
            #self.Node_list = []
            self.Node_list = copy.deepcopy(self.MAIN_node_list[:])
            # self.print_node(self.Node_list)
            self.Fault_Node_list = []


            # prompt for input Test vectors or to exit simulation
            # also calls for fault input
            # and prompt for faults
            if not ui:
                if not generated:
                    TESTVECTOR = TVs(len(self.Input_names))
                    TESTVECTOR.generate()
                    generated = True
                    self.input_TV_list = TESTVECTOR.TV
                    self.with_fault = True
                    print(f"Test Vector has {len(self.input_TV_list)} tvs:")
                    print(self.input_TV_list)
                    self.input_name = TESTVECTOR.how_generated
                    print("-----------------------------------------------")

                self.cur_tv_index = input_index
                #print(self.input_TV_list,"Using: ",self.input_TV_list[input_index])

            else:
                self.with_fault = False
                if self.input_prompt():
                    print("Exiting simulator")
                    break


            # reset nodes btwn simulations
            # for node in self.Node_list:
            #     node.set_value("U")





            # SET VALUE of INPUT nodes, based on user input
            if ui:

                s_index = 0
                for node in self.Node_list:
                    if node.is_input:
                        if s_index > len(self.user_TV) - 1:
                            break
                        node.set_value(self.user_TV[s_index])
                        s_index += 1
            else: # auto generated test vectors
                if got_time:
                    got_time = False
                    start = time.time()

                    print(f"on input {input_index} of {len(self.input_TV_list)}\n"
                            f"{(input_index / len(self.input_TV_list)) * 100}% done")


                #print(f"with fault {fault_index} of {len(self.Full_Fault_List) }\n"
                #      f"{(fault_index / len(self.Full_Fault_List) ) *100}%done")

                self.user_TV = self.input_TV_list[input_index]
                s_index = 0
                for node in self.Node_list:
                    if node.is_input:
                        if s_index > len(self.user_TV) - 1:
                            break
                        node.set_value(self.user_TV[s_index])
                        s_index += 1
                #for fault in self.Full_Fault_List:
                #add fault, one index at atime,
                # when all faults are ran, use next input index

                if fault_index > len(self.Full_Fault_List) - 1:
                    end = time.time()
                    got_time = True

                    time_took = int(end - start)/ 60
                    print(f"all faults took {time_took} m")

                    fault_index = 0
                    input_index += 1


                    if input_index > len(self.input_TV_list) - 1:
                        self.Is_Running = False
                        break

                    # need to reassign the inputs here for when the input increments
                    self.user_TV = self.input_TV_list[input_index]
                    s_index = 0
                    for node in self.Node_list:
                        if node.is_input:
                            if s_index > len(self.user_TV) - 1:
                                break
                            node.set_value(self.user_TV[s_index])
                            s_index += 1

                self.cur_input = self.user_TV
                self.cur_fault = self.Full_Fault_List[fault_index]
                self.Fault_input_list = self.parse_fault(self.Full_Fault_List[fault_index])

                fault_index += 1



            # ASSIGN FAULT / CONSTRUCT FAULTY NODE
            #only happens on user input for test vector / fault input
            if self.with_fault:
                self.Fault_Node_list = copy.deepcopy(self.Node_list[:])
                # self.Fault_Node_list = self.Node_list[:]

               # print("FAULT TYPE = ",self.Fault_TYPE)

                f_val = ''
                if self.Fault_TYPE == 1:

                    if self.Fault_input_list[1] == 1 or self.Fault_input_list[1] == "1":
                        f_val = "1"
                    else:
                        f_val = "0"
                    #self.Node_list[self.Fault_Index].set_value(f_val)
                    self.Fault_Node_list[self.Fault_Index].set_value(f_val)

                elif self.Fault_TYPE == 2:
                    self.add_faulty_node()


                else:
                    print("NOT VALID FAULT, exiting simulation")
                    exit(1)



            # display inputs to circuit and fault
           # self.display_circuit_inputs()
            #self.display_inputs_nodes(self.Node_list)
            if ui:
                iteration = str( input("do you want to print every iteration? (y/n)\n>") )
                if iteration == 'y':
                    self.print_iteration = True
            else:
                self.print_iteration = False



            if not ui:  # generate faults , no other outputs
                #if self.cur_input != TESTVECTOR.TV[input_index]:
                self.simulate_nodes(self.Node_list)
                self.simulate_nodes(self.Fault_Node_list)
                self.Detect_fault(self.Node_list,self.Fault_Node_list)



            else:  # (normal simulator mode) print outputs
                print("\t----- Begin simulation -----\t")
                self.display_inputs_nodes(self.Node_list)
                self.simulate_nodes(self.Node_list)
                self.print_results_nodes(self.Node_list)



                if self.with_fault:

                    print("\t------ Running Simulation with Fault ------\n")
                    self.display_inputs_nodes(self.Fault_Node_list)
                    self.display_fault(self.Fault_input_list)
                    self.simulate_nodes(self.Fault_Node_list)

                    self.Detect_fault(self.Node_list,self.Fault_Node_list)
                    self.print_results_nodes(self.Fault_Node_list)

                #self.print_results_nodes(self.Node_list)
                #self.print_results_nodes(self.Fault_Node_list)


        # these dont get used when user input mode
        if not ui:
            print("ALL DETECTED FAULTS")
            for k, v in self.detected.items():
                print(k, v)
            # print("ALL UNDETECTED FAULTS")
            # for k, v in self.undetected.items():
            #     print(k, v)

            self.Fault_coverage()
            print("----------------- ALL faults -----------------------------")
            filename =  TESTVECTOR.how_generated + self.Bench_str[:self.Bench_str.index('.')]
            #try:
            self.write_to_csv(filename+ "_all",self.detected)
            print("----------------- covered Faults -----------------------------")

            self.write_to_csv(filename+"_list",self.coverage)

            [x, y] = self.generate_plot_data()
            print(x, y)
            try:
                with open('graph_data/'+self.Bench_str[:self.Bench_str.index('.')] +TESTVECTOR.name+ "plot","w") as FILE:
                    s = f"COVERAGE RESULTS FOR {self.Bench_str} VIA PRPG\n"
                    if self.input_name == '':
                        s+="ALL TV tested\n"
                    else:
                        s +=   self.input_name+ "\n"

                    s+= "seed: " + TESTVECTOR.Seed + "ALL faults: " + str( len(self.Full_Fault_List) )

                    FILE.write(s + '\n')

                    for i in range(len(x)):
                        FILE.write(str(x[i]) +", "+ str(y[i]) +"\n" )
            except FileNotFoundError or TypeError:
                for i in range(len(x)):
                    print(str(x[i] ) + ", " + str( y[i] ) + "\n")

            # print("-----Coverage Fault-----")
            # for k, v in self.coverage.items():
            #     print(k, v)



# Simulator :
# encompases the entire circuit sim, but also keeps track of how to run the sim
# The idea is we can use this class to determine:
# - how we control potential automation for every TV generation option
# - which inputs to use, (user input , auto generated inputs)

class Simulator(object):

    def __init__(self):

        self.C = Circuit()
        self.TV = ''  # to be class TV
        self.Full_Fault_List = []

    # initialize variables
    def init_inputs(self):
        pass

    # if sim should be user input or generated tv
    def set_inputs_mode(self):
        pass
    def set_benchfile(self):

        pass

    def run_sim(self):
        pass



C = Circuit()
C.run()
