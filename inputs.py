import argparse
import copy
from math import *
from FFL import FFA as _F
import os

def bin_digits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % bits).format(s)

def minBits(dec):
    if(dec == 0):
        numBits = 1
    elif(dec < 0):
        return "This is unsigned, no negative numbers"
    else:
        numBits = int(log(abs(dec), 2) + 1 )
    return numBits


# generates all test vectors for a given ammount of bits
class TVs(object):
    def __init__(self,bits):
        self.TV = [] # test vectors stored as [strings]
        #self.arg = args
        self.b = bits
        self.index = 0
        self.Seed = "0x123456789abc"
        self.default_seed = "0x123456789abc"
        self.GLOABAL_SEED = "123456789abcdef0"
        self.how_generated = ""

        self.name = ""

        self.shifters = []



    def generate(self):
        if 2**self.b < 100: # 2^n
            if not self.b:
                bitNum = int( input("How many bits of length for test vectors? ") ,10)
                self.b = bitNum

            for n in range(2**self.b):
                s = bin_digits(n,self.b) #[n - minBits(self.b):]
                self.TV.append(s)

            # self.how_generated = "All TV tested"
            self.name = "_All"

        else:



            s = F"use (1) n-bit counter or (2) choose from following 8-bit LFSR config?\n"
            input_choice = int(input(s + ">"))
            while input_choice != 1 and input_choice != 2:
                print("invalid option. Try again")
                input_choice = input(">")


            if input_choice == 1: # n -bit counter
                s =  f"Circuit PI > 100\n set the seed value for n-bit counter(in hex):\n>"
                get_seed =input(s)
                # while len(get_seed) != 0:
                #     get_seed = input("try again? or (enter for default)\n>")

                if len(get_seed) == 0:
                    self.Seed = self.default_seed
                else:
                    self.Seed = get_seed

                print("Using Seed : ",self.Seed)
                self.how_generated = "n-bit counter_" #+ self.Seed + "_"
                self.name = "_Counter"
                seed_int = int(self.Seed, 16)
                for t in range(100):
                    seed_bin = bin_digits(seed_int, self.b)
                  #  counter_inputs.write(seed_bin + '\n')
                    print(f"T_{t} : {seed_bin}")
                    seed_int += 1
                    self.TV.append(seed_bin)

            elif input_choice == 2: # if using an lfsr


                options = [ [8,[]], [8,[2,4,5]], [8,[2,3,4]], [8,[3,5,7]] ]
                index=  0
                for option in options:
                    print(index,option[0],"-bit LFSR w/ Taps @",option[1])
                    index += 1


                #for i in range(len(self.shifters)):
                #    print(f"{i} : {self.shifters[i]}")

                lfsr_choice = int(input("choose LFSR option: \n>"))
                while lfsr_choice > len(options):
                    print("try again for LFSR input")
                    lfsr_choice = int(input(">") )

                index = lfsr_choice

                self.name = "_LFSR " + str(index) + " "
                # for cases when circuit PI > than global seed
                # global seed = 8 bits per 2 char,
                # check if len of seed > PI / 8


                # # of 8 - bit lfsr = PI / (8 lfsr bits)
                #
                if self.b % options[index][0] != 0:
                    num_lfsr = (self.b  // 8)
                    num_lfsr += 1
                else:
                    num_lfsr = self.b // 8

                print("lfsr needed = ",num_lfsr)

                if len(self.GLOABAL_SEED) / 2 < self.b // 8:
                    self.GLOABAL_SEED = self.GLOABAL_SEED * (self.b // num_lfsr)

                # print(len(self.GLOABAL_SEED) , self.GLOABAL_SEED)
                seed_array = []
                for i in range(0,len(self.GLOABAL_SEED),2):
                    seed_array.append(self.GLOABAL_SEED[i:i+2])
                # print(seed_array)
                cur_seed = 0

                for i in range(2,num_lfsr + 2):
                    self.shifters.append( LFSR(seed_array[cur_seed],options[index][0],options[index][1]) )

                    cur_seed += 1

                print(f"Created {len(self.shifters)} * 8-bit LFSR ({len(self.shifters) * 8}bits) for PI:{self.b} ")
                print(f"GLOBAL SEED: {self.GLOABAL_SEED}")
                self.how_generated = f"{options[index][0]}-bit LFSR, Taps @ [ "
                for num in options[index][1]:
                    self.how_generated += str(num)

                self.how_generated += "] "
                # print(self.how_generated)
                self.Seed = self.GLOABAL_SEED

                #Now to iterate through each shifter and cncat each bit into final input str
                for shifter in self.shifters:
                    shifter.generate_TV_list()

                # for shifter in self.shifters:
                #     print(shifter)
                #     print(shifter.TV)

                tv = ""
                for i in range(len(self.shifters[0].TV)):
                    if i == 100:
                        break
                    tv = ''
                    for k in range(len(self.shifters)):
                        # print(self.shifters[k].TV[0] )
                        tv+= self.shifters[k].TV[i]

                    self.TV.append(tv)


            else:
                print("invalid option ")
                exit(1)
            #prompt for counter or lfsr:


    # def f_write(self,value:str):
    #     #for n in self.TV:
    #      #   self.f.write(f"{n}\n")
    #     self.f.write(f"{value}\n")


        #self.f.close()

    def __str__(self):
        string = f"TVs for {self.b}  bits\n"
        string += f"TVs:{self.TV}"
        # i  =0
        # for n in self.TV:
        #     string += f"{i} ->{n}\n"
        #     i=i+1
        return string

class PRPG(object):

    def __init__(self):
       # self.Global_Seed = "0xf" #"0x123456789abcdef0"
       # self.offset = 1 # index of which part of seed to use for LFSR

        self.TV = []

    def generate_TV_list(self):
        pass

# n bit lfsr with taps anywhere

class LFSR(PRPG):

    def __init__(self,seed,bits,taps):
        super().__init__()
        self.SEED = seed
        self.bit_num = bits
        self.Taps = taps
        self.value = ""
        #self.Value_list = []
        self. h = ''
        self.name = f"{self.bit_num}-bit LFSR w taps {self.Taps} | seed :0x{self.SEED}"



    def generate_TV_list(self):
        #self.value = bin_digits(int(self.Global_Seed[self.offset - 1:self.offset], 16), self.bit_num)
        self.value = bin_digits(int(self.SEED ,16),self.bit_num)
        value_list = [] # LFSR value as list of
        value_seed = []
        value_next = [''] * self.bit_num

        for c in self.value:
            value_list.append(c)
            value_seed.append(c)


        # print(self.value)
        #self.TV.append(self.value)

        # feedback = int( value_list[-1] )
        counter = 0
        repeated = False
        while not repeated: #  counter < 100: #  <--- waste of time
            value = ''.join(value_list)
            self.TV.append(value)
            #print(value_list)
            for i in range(len(value_list)  ):
                feedback = int( value_list[-1] )
                # print("FEEDBACK:",feedback)
                if i == 0:
                    value_next[0] = str( feedback)
                else:
                    if i in self.Taps:
                        value_next[i] = str(int(value_list[i-1] )   ^ feedback )
                    else:
                        value_next[i] = value_list[i-1]


            value_list = copy.deepcopy(value_next)

            # print(value)
            if value_list == value_seed:
                repeated = True


    def __str__(self):

        s = f"LFSR w/ seed: {self.SEED} | n = { self.bit_num}  Taps @ "
        for index in self.Taps:
            s += str(index) + ' '


        # s += f"\nTVs: {self.TV}"
        return s

S2 = LFSR("F",4,[2])
print(S2)
S2.generate_TV_list()

# if __name__ == '__main__':
#     # parser = argparse.ArgumentParser()
#     # parser.add_argument('-b', '--bits', type=int, default = 3,help = 'How many bits?')
#     # parser.add_argument('-f', '--file', type=str, default='Tvs', help='File name for out')
#     # args = parser.parse_args()
#
#     #t = TVs(args)
#     benchL = os.listdir('benches')
#    # print(benchL)
#     for bf in sorted(benchL):
#         F = _F(bf)
#         F.gate_faults()
#         # F.write_faults()
#         s = f"{F.f} has {len(F.FFLIST)} Faults"
#         print(s)
#     # F = _F("c17.bench") #Full fault list class
#     # F.gate_faults()
#     # t = TVs(len(F.Input_names))
#     # F.write_faults()
#     # t.generate()
#     #F.display_faults()
#     # print(t)
#     # print(F)

