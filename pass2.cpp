#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
using namespace std;

struct Symbol { string name; int addr; };
struct Literal { string lit; int addr; };

vector<Symbol> SYMTAB;
vector<Literal> LITTAB;

int findSym(string s){
    for(auto &x: SYMTAB)
        if(x.name == s) return x.addr;
    return 0;
}

int findLit(string l){
    for(auto &x: LITTAB)
        if(x.lit == l) return x.addr;
    return 0;
}

int main(){
    ifstream inter("intermediate.txt");
    ifstream sym("symtab.txt");
    ifstream lit("littab.txt");
    ofstream out("machinecode.txt");

    string d,name,litval; int addr;

    // read symbol table
    sym >> d >> d;
    while(sym >> name >> addr)
        SYMTAB.push_back({name, addr});

    // read literal table
    lit >> d >> d;
    while(lit >> litval >> addr)
        LITTAB.push_back({litval, addr});

    string line;
    while(getline(inter,line)){
        if(line.find("(IS") == string::npos) continue;

        // remove brackets and commas
        for(char &c: line)
            if(c=='('||c==')'||c==',') c=' ';

        stringstream ss(line);
        string LC, IS, opcode, token;
        int reg = 0, opaddr = 0;

        ss >> LC >> IS >> opcode; // read LC, (IS,xx) and opcode

        while(ss >> token){
            // register
            if(token == "REG"){
                ss >> reg;
            }
            // literal
            else if(token.find("='") != string::npos){
                opaddr = findLit(token);
            }
            // symbol
            else if(isalpha(token[0])){
                opaddr = findSym(token);
            }
            // constant
            else if(isdigit(token[0])){
                opaddr = stoi(token);
            }
        }

        out << opcode << " " << reg << " " << opaddr << "\n";
    }

    cout << "✅ Fixed! machinecode.txt generated.\n";
    return 0;
}
