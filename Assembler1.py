# --- Setup Tables ---
# 1. Opcode Table (OPTAB)
# Format: Mnemonic: (Machine Code, Number of Operands)
OPTAB = {
    "MOVER": ("01", 2), # 2 operands (REG, SYM)
    "ADD":   ("02", 2), # 2 operands (REG, SYM)
    "STORE": ("03", 2), # 2 operands (REG, SYM)
    "JMP":   ("04", 1), # 1 operand (SYM)
    "SUB":   ("06", 2), # 2 operands (REG, SYM) - Fixed duplicate "03"
    "END":   ("05", 0)  # 0 operands
}
# 2. Register Table (REGTAB)
# Format: RegisterName: RegisterCode
REGTAB = {
    "A": "1",
    "B": "2",
    "C": "3",
    "D": "4"
}
# 3. Symbol Table (SYMTAB) - To be filled by Pass 1
# Format: SymbolName: Address
SYMTAB = {}
# 4. Intermediate Code (INTERMEDIATE) - To be filled by Pass 1
INTERMEDIATE = []
# --- Pass 1 ---
def pass1():
    """
    Performs Pass 1 of the assembler:
    1. Reads the input.asm file.
    2. Builds the Symbol Table (SYMTAB).
    3. Generates the Intermediate Code (INTERMEDIATE).
    """
    global LC # Use a global Location Counter
    LC = 0
    
    with open("input.asm", "r") as f:
        for line in f:
            tokens = line.strip().replace(",", "").split()
            if not tokens:
                continue

            # Handle START directive
            if tokens[0] == "START":
                LC = int(tokens[1])
                # Format: (Type, Code, Value)
                INTERMEDIATE.append(("AD", "01", f"(C,{LC})"))
                continue
            
            label = None
            opcode_index = 0

            # --- Label Detection ---
            # Check if the first token is a label (i.e., not in OPTAB and not END)
            if tokens[0] not in OPTAB and tokens[0] != "END":
                
                # --- THIS IS THE FIX ---
                label = tokens[0].replace(":", "") # Strip the colon from the label
                # --- END OF FIX ---
                
                if label in SYMTAB:
                    # If it was a forward reference, update its address
                    if SYMTAB[label] == -1:
                        SYMTAB[label] = LC
                    else:
                        print(f"Error: Duplicate label '{label}'")
                else:
                    SYMTAB[label] = LC # Add new label to SYMTAB
                
                opcode_index = 1 # The opcode is the *next* token
            
            # Stop if line was just a label (e.g., "LOOP:")
            if len(tokens) <= opcode_index:
                continue
                
            opcode = tokens[opcode_index]

            # --- Opcode Processing ---

            # Handle END directive
            if opcode == "END":
                INTERMEDIATE.append(("AD", "05"))
                break # End of Pass 1

            # Handle Declarative Statements (DS, DC)
            if opcode == "DS": # Define Storage
                size = int(tokens[opcode_index + 1])
                INTERMEDIATE.append(("DL", "01", f"(C,{size})"))
                LC += size # Increment LC by storage size
                continue
            
            if opcode == "DC": # Define Constant
                value = tokens[opcode_index + 1]
                INTERMEDIATE.append(("DL", "02", f"(C,{value})"))
                LC += 1 # Increment LC by 1
                continue
            
            # Handle Imperative Statements (IS)
            if opcode in OPTAB:
                op_code_val, num_operands = OPTAB[opcode]
                
                # Start building the intermediate entry
                # Format: (Type, OpCode, RegCode, SymbolName)
                entry = ["IS", op_code_val]
                
                if num_operands == 2: # e.g., MOVER A, B
                    reg = tokens[opcode_index + 1]
                    sym = tokens[opcode_index + 2]
                    
                    if sym not in SYMTAB:
                        SYMTAB[sym] = -1 # Add symbol as unresolved
                    
                    entry.extend([REGTAB[reg], sym]) # Store reg_code and sym_name
                
                elif num_operands == 1: # e.g., JMP LOOP
                    sym = tokens[opcode_index + 1]
                    
                    if sym not in SYMTAB:
                        SYMTAB[sym] = -1 # Add symbol as unresolved
                        
                    entry.extend(["0", sym]) # No register, use "0"
                
                elif num_operands == 0: # e.g., STOP (if it existed)
                    pass # No operands to add
                
                INTERMEDIATE.append(tuple(entry))
                LC += 1 # Instruction takes 1 memory word
                continue

# --- Pass 2 ---

def pass2():
    """
    Performs Pass 2 of the assembler:
    1. Reads the INTERMEDIATE code and SYMTAB.
    2. Generates the final machinecode.txt.
    """
    with open("machinecode.txt", "w") as mc:
        for entry in INTERMEDIATE:
            entry_type = entry[0]
            
            # --- Imperative Statement (IS) ---
            if entry_type == "IS":
                # Format: (IS, opcode, reg_code, symbol)
                opcode = entry[1]
                reg = entry[2]
                symbol_name = entry[3]
                
                if symbol_name in SYMTAB:
                    symbol_addr = SYMTAB[symbol_name]
                    if symbol_addr == -1:
                        print(f"Error: Symbol '{symbol_name}' was used but not defined.")
                        symbol_addr = "XXX" # Error code
                else:
                    print(f"Error: Symbol '{symbol_name}' not found in SYMTAB.")
                    symbol_addr = "XXX" # Error code
                
                # Write: OPCODE  REG  ADDRESS
                mc.write(f"{opcode}\t{reg}\t{str(symbol_addr).zfill(3)}\n")
            
            # --- Declarative Statement (DL) ---
            elif entry_type == "DL":
                dl_code = entry[1]
                # Extract value from (C,value)
                value_str = entry[2].replace("(C,", "").replace(")", "")
                
                if dl_code == "01": # DS (Define Storage)
                    # Reserve N lines of "0" (null instructions)
                    size = int(value_str)
                    for _ in range(size):
                        mc.write("00\t0\t000\n") 
                
                elif dl_code == "02": # DC (Define Constant)
                    # Write the constant value, formatted as data
                    mc.write(f"00\t0\t{value_str.zfill(3)}\n")
            
            # --- Assembler Directive (AD) ---
            elif entry_type == "AD":
                # START, END directives don't generate code
                mc.write("-\n")

# --- Helper Functions ---

def write_symtab():
    """Writes the final SYMTAB to symtab.txt"""
    with open("symtab.txt", "w") as st:
        st.write("Symbol\tAddress\n")
        st.write("---------------\n")
        for sym, addr in SYMTAB.items():
            st.write(f"{sym}\t{addr}\n")

def write_intermediate():
    """Writes the INTERMEDIATE code to intermediate.txt"""
    with open("intermediate.txt", "w") as ic:
        for line in INTERMEDIATE:
            ic.write(str(line) + "\n")

def setup_input_file():
    """Creates a sample input.asm file for testing."""
    asm_code = """
START 100
MOVER A, B
ADD A, C
LOOP: SUB B, ONE
STORE B, TEMP
JMP LOOP
ONE: DC 1
B: DS 1
C: DS 1
TEMP: DS 10
END
"""
    with open("input.asm", "w") as f:
        f.write(asm_code)

# --- Main Execution ---

# 1. Create a sample input file
setup_input_file()

# 2. Run Pass 1
pass1()

# 3. Run Pass 2
pass2()

# 4. Write helper files
write_symtab()
write_intermediate()

print("✅ PASS-1 and PASS-2 Completed Successfully!")
print("Generated Files: input.asm, symtab.txt, intermediate.txt, machinecode.txt")
