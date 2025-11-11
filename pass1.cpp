#include <bits/stdc++.h>
using namespace std;

// Opcode Table
map<string, string> OPTAB = {
    {"STOP", "00"}, {"ADD", "01"}, {"SUB", "02"}, {"MULT", "03"}, {"MOVER", "04"}, {"MOVEM", "05"}, 
    {"COMP", "06"}, {"BC", "07"}, {"DIV", "08"}, {"READ", "09"}, {"PRINT", "10"}};

// Register Table
map<string, int> REGTAB = {
    {"AREG", 1}, {"BREG", 2}, {"CREG", 3}, {"DREG", 4}};

// Symbol Table, Literal Table, Literal Address Table, Pool Table
map<string, int> SYMTAB;
vector<string> LITTAB;
vector<int> LITADDR;
vector<int> POOLTAB = {0}; // pool starts from literal index 0

int LC = 0;

bool is_number(const string &s)
{
    return !s.empty() && all_of(s.begin(), s.end(), ::isdigit);
}

// Assign address to all pending literals
void assign_literals(ofstream &intermediate)
{
    for (int i = POOLTAB.back(); i < LITTAB.size(); i++)
    {
        intermediate << LC << " (DL,02) " << LITTAB[i] << "\n";
        LITADDR.push_back(LC);
        LC++;
    }
    POOLTAB.push_back(LITTAB.size());
}

// Process each line
void process_line(string line, ofstream &intermediate)
{
    string label, opcode, op1, op2;
    stringstream ss(line);

    ss >> label;

    if (OPTAB.find(label) != OPTAB.end() || label == "START" || label == "END" || label == "DS" || label == "DC" || label == "LTORG")
    {
        opcode = label;
        label = "";
    }
    else
    {
        ss >> opcode;
    }

    ss >> op1 >> op2;

    // ✅ remove trailing comma if present
    if (!op1.empty() && op1.back() == ',')
        op1.pop_back();

    // START
    if (opcode == "START")
    {
        if (is_number(op1))
        {
            LC = stoi(op1);
            intermediate << LC << " (AD,01) (C," << op1 << ")\n";
        }
        return;
    }

    // ✅ LTORG support
    if (opcode == "LTORG")
    {
        assign_literals(intermediate);
        return;
    }

    // END → assign pending literals
    if (opcode == "END")
    {
        assign_literals(intermediate);
        intermediate << LC << " (AD,02)\n";
        return;
    }

    // Add label to symbol table
    if (!label.empty())
    {
        SYMTAB[label] = LC;
    }

    // DS
    if (opcode == "DS")
    {
        intermediate << LC << " (DL,01) (C," << op1 << ")\n";
        LC += stoi(op1);
        return;
    }

    // DC
    if (opcode == "DC")
    {
        intermediate << LC << " (DL,02) (C," << op1 << ")\n";
        LC++;
        return;
    }

    // Imperative
    intermediate << LC << " (IS," << OPTAB[opcode] << ") ";

    if (!op1.empty())
    {
        if (REGTAB.find(op1) != REGTAB.end())
            intermediate << "(REG, " << REGTAB[op1] << "), ";
        else
            intermediate << "(0), ";
    }

    // Check if literal
    if (!op2.empty())
    {
        if (op2.find('=') != string::npos)
        {
            if (find(LITTAB.begin(), LITTAB.end(), op2) == LITTAB.end())
                LITTAB.push_back(op2);

            intermediate << op2;
        }
        else
        {
            intermediate << op2;
        }
    }

    intermediate << "\n";
    LC++;
}

int main()
{
    ifstream fin("input.txt");
    ofstream fout("intermediate.txt");
    ofstream symout("symtab.txt");
    ofstream litout("littab.txt");
    ofstream poolout("pooltab.txt");

    if (!fin || !fout || !symout || !litout || !poolout)
    {
        cerr << "Error opening files.\n";
        return 1;
    }

    string line;
    while (getline(fin, line))
    {
        if (!line.empty())
            process_line(line, fout);
    }

    // Write Symbol Table
    symout << left << setw(10) << "Symbol" << "Address\n";
    for (auto &entry : SYMTAB)
        symout << left << setw(10) << entry.first << entry.second << "\n";

    // Write Literal Table
    litout << left << setw(10) << "Literal" << "Address\n";
    for (int i = 0; i < LITTAB.size(); i++)
        litout << left << setw(10) << LITTAB[i] << LITADDR[i] << "\n";

    // Write Pool Table
    poolout << "PoolIndex\n";
    for (int x : POOLTAB)
        poolout << x << "\n";

    cout << "Pass-1 complete.\nGenerated:\n → intermediate.txt\n → symtab.txt\n → littab.txt\n → pooltab.txt\n";

    return 0;
}
