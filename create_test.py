import xml.etree.ElementTree as ET
import os
import sys
import re

trace_format = "%1%\t%2%\t%5%\t%6%\t%7%\t%8%\t%9%\t%10%\t%pc%\t%inst%\t%line%\n"

try:
	assembly_file = sys.argv[1]
	num_cycles = int(sys.argv[2]) + 1 # need +1 because of lag in circuit
except:
	raise Exception("The format of this command should be: python create_test.py <test_name>.s <# cycles>")

### CREATES HEX FILE
test_name = assembly_file[:-2] ## eliminates .s at end
prefix = 'CPU-' + test_name
ref_output = "./my_tests/circ_files/reference_output/" + prefix + ".out"
hex_file = "./my_tests/input/" + test_name + ".hex"
f = open("trace_format", "w")
f.write(trace_format)
f.close()
if not os.path.exists("my_tests/circ_files/reference_output"):
    os.makedirs("my_tests/circ_files/reference_output")
if not os.path.exists("my_tests/input"):
    os.makedirs("my_tests/input")
os.system("java -jar venus-jvm-latest.jar -t -tf trace_format -ti -tw -ts -tn " + str(num_cycles + 1) + " -r " + assembly_file + " > " + ref_output)
os.system("rm -f trace_format")
os.system("java -jar venus-jvm-latest.jar -d " + assembly_file + " > " + hex_file)
os.system("cp " + assembly_file + " my_tests/input/")

### FORMATS HEX FOR INPUTTING INTO CIRCUIT
instructions = ""
with open(hex_file, "r") as f:
    nums = f.read().split("\n")
    nums.pop()
    # pops get ride of extra newlines that venus automatically adds
    for num in nums:
        num = num[2:] # removes 0x as beginning
        instructions += num + " "

    instructions = instructions[:-1] # gets rid of extra space at end
    instructions += "\n"

### PUTS TESTS INTO CIRCUIT
tree = ET.parse('run.circ')
root = tree.getroot()
circuit = root.find('circuit')
ROM = circuit.find("./comp/[@name='ROM']")

pre = "addr/data: 14 32\n"
result = pre + instructions

ROM[2].text = result

### PUTS CYLCLE NUM INTO CIRCUIT
constant = circuit.find("./comp/[@name='Constant']")
num_cycles_formatted = hex(num_cycles)
constant[1].attrib['val'] = num_cycles_formatted

tree.write(prefix + '.circ')

### MOVES THINGS WHERE THEY SHOULD BE
os.system("mv " + prefix + ".circ my_tests/circ_files/")
print("Test created!")