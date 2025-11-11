# --- Constant Tables ---
OPTAB = {
    'STOP':  ('IS', '00'), 'ADD':   ('IS', '01'), 'SUB':   ('IS', '02'),
    'MULT':  ('IS', '03'), 'MOVER': ('IS', '04'), 'MOVEM': ('IS', '05'),
    'COMP':  ('IS', '06'), 'BC':    ('IS', '07'), 'DIV':   ('IS', '08'),
    'READ':  ('IS', '09'), 'PRINT': ('IS', '10'),
    'START': ('AD', '01'), 'END':   ('AD', '02'), 'ORIGIN':('AD', '03'),
    'EQU':   ('AD', '04'), 'LTORG': ('AD', '05'),
    'DC':    ('DL', '01'), 'DS':    ('DL', '02')
}
REGTAB = {'AREG': 1, 'BREG': 2, 'CREG': 3, 'DREG': 4}
CONDTAB = {'LT': 1, 'LE': 2, 'EQ': 3, 'GT': 4, 'GE': 5, 'ANY': 6}


# --- Pass 1 Function ---
def pass1(assembly_code):
    """
    Performs Pass 1 of the assembler.
    Returns: symtab, littab, pooltab, intermediate_code
    """
    symtab_map = {}
    symtab = []

    littab_map = {}
    littab = []

    pooltab = [0] # Pool 0 starts at LITTAB index 0
    
    # This list tracks literals that are pending for the *current* pool
    unassigned_literals_in_pool = [] 

    intermediate_code = []
    lc = 0

    for line in assembly_code:
        label, opcode, op1, op2 = line
        ic = []

        if label:
            if label not in symtab_map:
                symtab_map[label] = len(symtab)
                symtab.append([label, lc])
            else:
                # Update address for a forward reference
                if symtab[symtab_map[label]][1] == -1:
                    symtab[symtab_map[label]][1] = lc
                else: # Re-definition of a symbol
                    print(f"Error: Duplicate symbol '{label}'")

        if opcode == 'START':
            if op1:
                lc = int(op1)
            ic = [lc, (OPTAB[opcode][0], OPTAB[opcode][1]), ('C', lc)]

        elif opcode == 'EQU':
            # This assumes backward reference for EQU
            symtab[symtab_map[label]][1] = symtab[symtab_map[op1]][1]
            ic = [lc, ('AD', '04'), ('S', symtab_map[op1])]

        elif opcode in ('LTORG', 'END'):
            ic = [lc, OPTAB[opcode]]
            intermediate_code.append(ic) # Add the LTORG/END directive itself

            if unassigned_literals_in_pool:
                # Process all pending literals for this pool
                for literal in unassigned_literals_in_pool:
                    lit_index = littab_map[literal]
                    if littab[lit_index][1] == -1: # If address not assigned
                        littab[lit_index][1] = lc
                        # Add literal definition to IC (like a DC)
                        value = literal.strip("='")
                        intermediate_code.append([lc, ('DL', '01'), ('C', value)])
                        lc += 1
                
                # Mark the start of the *next* pool
                pooltab.append(len(littab))
                unassigned_literals_in_pool = [] # Clear the pool
            
            if opcode == 'END':
                break # Stop processing
            continue # Skip adding this to IC again

        elif opcode == 'ORIGIN':
            if '+' in op1:
                sym, num = op1.split('+')
                lc = symtab[symtab_map[sym]][1] + int(num)
            elif '-' in op1:
                sym, num = op1.split('-') 
                lc = symtab[symtab_map[sym]][1] - int(num)
            else:
                try:
                    lc = int(op1)
                except:
                    lc = symtab[symtab_map[op1]][1]
            ic = [lc, OPTAB[opcode]]

        elif opcode == 'DC':
            ic = [lc, OPTAB[opcode], ('C', op1.strip("'"))]
            lc += 1

        elif opcode == 'DS':
            ic = [lc, OPTAB[opcode], ('C', op1)]
            lc += int(op1)

        else: # IS statements
            ic = [lc, OPTAB[opcode]]

            def encode_operand(op):
                if op == '':
                    return ''
                elif op in REGTAB:
                    return REGTAB[op]
                elif op in CONDTAB:
                    return CONDTAB[op]
                
                elif op.startswith('='):
                    if op not in littab_map:
                        littab_map[op] = len(littab)
                        littab.append([op, -1]) 
                    
                    if op not in unassigned_literals_in_pool:
                        unassigned_literals_in_pool.append(op)
                        
                    return ('L', littab_map[op])
                
                elif op in symtab_map:
                    return ('S', symtab_map[op])
                try:
                    return ('C', int(op))
                except:
                    # symbol with forward reference
                    symtab_map[op] = len(symtab)
                    symtab.append([op, -1])
                    return ('S', symtab_map[op])

            if op1: ic.append(encode_operand(op1))
            if op2: ic.append(encode_operand(op2))
            lc += 1
        
        intermediate_code.append(ic)

    return symtab, littab, pooltab, intermediate_code


# --- Pass 2 Function ---
def pass2(intermediate_code, symbol_table, literal_table, pooltab):
    """
    Performs Pass 2 of the assembler.
    Returns: machine_code (list of lists)
    """
    machine_code = []

    for ic_entry in intermediate_code:
        if len(ic_entry) < 2:
            continue
            
        LC = ic_entry[0]
        opclass, opnum = ic_entry[1]

        # AD (Assembler Directives) are processed in Pass 1
        if opclass == 'AD':
            continue

        # DS (Define Storage)
        if opclass == 'DL' and opnum == '02':  # DS
            try:
                space = int(ic_entry[2][1]) 
            except (IndexError, ValueError):
                space = 0
                
            for i in range(space):
                mc_line = [str(LC + i), '00', '0', '000']
                machine_code.append(mc_line)
            continue 

        # --- IS (Imperative) and DC (Declarative Constant) ---
        mc_line = [str(LC)]
        
        if opclass == 'IS':
            mc_line.append(opnum) # Add opcode
            
            for operand in ic_entry[2:]:
                if isinstance(operand, int): # Register or Condition
                    mc_line.append(str(operand))
                elif isinstance(operand, tuple):
                    typechar, val = operand
                    if typechar == 'C':
                        mc_line.append(str(val))
                    elif typechar == 'S':  # Symbol
                        addr = symbol_table[val][1]
                        mc_line.append(str(addr))
                    elif typechar == 'L':  # Literal
                        addr = literal_table[val][1]
                        mc_line.append(str(addr))
                elif isinstance(operand, str) and operand.isdigit():
                    mc_line.append(operand)
            
            while len(mc_line) < 4:
                mc_line.append('0')

        elif opclass == 'DL' and opnum == '01':  # DC (or literal)
            value = '0'
            try:
                if isinstance(ic_entry[2], tuple) and ic_entry[2][0] == 'C':
                    value = str(ic_entry[2][1])
            except IndexError:
                pass
            
            mc_line = [str(LC), '00', '0', value.zfill(3)]
        
        machine_code.append(mc_line)
        
    return machine_code


# --- Main Execution Block ---
if __name__ == "__main__":
    
    # Input Assembly Code
    assembly_code2 = [
        ["","START","201",""],
        ["","MOVER","AREG","='5'"],
        ["","MOVEM","AREG","X"],
        ["","MOVER","BREG","='2'"],
        ["","LTORG","",""],    
        ["NEXT","ADD","AREG","='1'"],
        ["","SUB","BREG","='2'"],
        ["","BC","LT","NEXT"],
        ["","MULT","CREG","='4'"],
        ["","STOP","",""],
        ["X","DS","1",""],
        ["","END","",""]
    ]

    # --- Run Pass 1 ---
    print("Running Pass 1...")
    symtab, littab, pooltab, ic = pass1(assembly_code2)

    # --- Print Intermediate Results ---
    print("\n--- SYMBOL TABLE ---")
    print(symtab)
    print("\n--- LITERAL TABLE ---")
    print(littab)
    print("\n--- POOL TABLE ---")
    print(pooltab)
    print("\n--- INTERMEDIATE CODE ---")
    for entry in ic:
        print(entry)

    # --- Run Pass 2 ---
    print("\nRunning Pass 2...")
    mc = pass2(ic, symtab, littab, pooltab)

    # --- Print Final Machine Code ---
    print("\n--- MACHINE CODE ---")
    print("LOC  OP   R1   R2") # 4-column header
    print("-------------------")
    for line in mc:
        # ljust(4) adds padding to align the columns
        print(" ".join(str(x).ljust(4) for x in line))
