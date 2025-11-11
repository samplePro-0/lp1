import json

MNT = {}
# MDT (Macro Definition Table): [ "line 1", "line 2", ... ]
MDT = []

def setup_input_file():
    """Creates a sample macro_input.asm file for testing."""
    # This code is from your new images
    macro_code = """
MACRO
ONE &O, &N, &E=AREG
MOVER &E, &O
ADD &E, &N
MOVEM &E, &O
MEND

MACRO
TWO &T, &W, &O=DREG
MOVER &O, &T
ADD &O, &W
MOVEM &O, &T
MEND

START
READ O
READ T
ONE O, 9
TWO T, 7
ONE O, 9, &E=CREG
STOP
O DS 1
T DS 1
END
"""
    with open("macro_input.asm", "w") as f:
        f.write(macro_code.strip())

# --- Pass 1 Function ---

def pass1():
    """
    Performs Pass 1: Builds MNT, MDT, and intermediate.asm.
    Handles default parameters in macro definitions.
    """
    print("Building MNT, MDT, and intermediate.asm...")
    
    mnt = {}
    mdt = []
    
    macro_state = "NONE" # "NONE", "HEADER", "BODY"
    
    with open("macro_input.asm", "r") as f_in, open("intermediate.asm", "w") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            
            tokens = line.replace(',', '').split()
            
            if tokens[0] == 'MACRO':
                macro_state = "HEADER"
                continue
            
            if macro_state == "HEADER":
                # --- New Header Parsing Logic ---
                macro_name = tokens[0]
                parameters = []
                
                # Parse all parameters (e.g., &O, &N, &E=AREG)
                for param in tokens[1:]:
                    if '=' in param:
                        # It's a keyword param with a default
                        p_name, p_default = param.split('=', 1)
                        parameters.append({"name": p_name, "default": p_default})
                    else:
                        # It's a positional param
                        parameters.append({"name": param, "default": None})
                
                # Store this parsed info in the MNT
                mnt[macro_name] = {
                    "params": parameters,
                    "mdt_index": len(mdt) # The body starts at current MDT length
                }
                
                macro_state = "BODY"
                continue
                
            if macro_state == "BODY":
                if tokens[0] == 'MEND':
                    mdt.append(line)
                    macro_state = "NONE"
                else:
                    # Add macro body line to MDT
                    mdt.append(line)
                continue
            
            if macro_state == "NONE":
                # This is regular code, write to intermediate
                f_out.write(line + "\n")
                
    return mnt, mdt

# --- Pass 2 Function ---

def pass2(mnt, mdt):
    """
    Performs Pass 2: Expands macros from intermediate.asm.
    Handles positional, keyword, and default parameters.
    """
    print("Expanding macros and writing expanded.asm...")
    
    with open("intermediate.asm", "r") as f_in, open("expanded.asm", "w") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
                
            tokens = line.replace(',', '').split()
            opcode = tokens[0]
            
            if opcode in mnt:
                # --- This is a Macro Call ---
                
                # --- New ALA-building Logic ---
                ala = {} # Argument List Array (as a dictionary)
                macro_info = mnt[opcode]
                formal_params = macro_info["params"]
                actual_params = tokens[1:]
                
                # 1. Fill ALA with all default values first
                for param in formal_params:
                    if param["default"] is not None:
                        ala[param["name"]] = param["default"]
                
                # 2. Process positional arguments
                pid = 0 # Positional index
                while pid < len(actual_params):
                    arg = actual_params[pid]
                    if '=' in arg:
                        # This is a keyword argument, stop processing positional
                        break
                    
                    # Map positional arg: e.g., "O" -> "&O"
                    param_name = formal_params[pid]["name"]
                    ala[param_name] = arg
                    pid += 1
                
                # 3. Process keyword arguments (they override defaults)
                for kid in range(pid, len(actual_params)):
                    arg = actual_params[kid]
                    p_name, p_value = arg.split('=', 1)
                    # Check if it's a valid parameter name
                    if any(p["name"] == p_name for p in formal_params):
                        ala[p_name] = p_value
                    else:
                        print(f"Error: Invalid keyword argument '{arg}' in line: {line}")

                # --- End of ALA Logic ---

                # 4. Expand the macro body, substituting from ALA
                mdt_start_index = macro_info["mdt_index"]
                current_mdt_index = mdt_start_index
                
                while True:
                    expansion_line = mdt[current_mdt_index]
                    current_mdt_index += 1
                    
                    if expansion_line == 'MEND':
                        break # Stop expanding
                    
                    # Substitute parameters
                    expanded_tokens = []
                    for token in expansion_line.replace(',', '').split():
                        if token in ala:
                            # Substitute with actual parameter from ALA
                            expanded_tokens.append(ala[token])
                        else:
                            expanded_tokens.append(token)
                    
                    # Write the expanded line
                    f_out.write(" ".join(expanded_tokens) + "\n")
                
            else:
                # --- This is Regular Assembly Code ---
                f_out.write(line + "\n")

# --- Main Execution Block ---
if __name__ == "__main__":
    
    # 1. Create the input file
    setup_input_file()

    # 2. Run Pass 1
    print("--- Running Pass 1 ---")
    MNT, MDT = pass1()

    print("\n--- Pass 1 Results ---")
    print("\nMacro Name Table (MNT):")
    print(json.dumps(MNT, indent=2))
    
    print("\nMacro Definition Table (MDT):")
    for i, line in enumerate(MDT):
        print(f" {i}: {line}")

    # 3. Show Intermediate File
    print("\n--- intermediate.asm (Pass 1 Output) ---")
    with open("intermediate.asm", "r") as f:
        print(f.read())
    
    # 4. Run Pass 2
    print("\n--- Running Pass 2 ---")
    pass2(MNT, MDT)

    # 5. Show Final Expanded File
    print("\n--- expanded.asm (Pass 2 Output) ---")
    with open("expanded.asm", "r") as f:
        print(f.read())
