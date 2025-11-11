#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
using namespace std;

struct MNTentry {
    string name;
    int mdtIndex;
};

vector<MNTentry> MNT;
vector<string> MDT;
vector<string> ALA;

// function to split words
vector<string> split(string line) {
    stringstream ss(line);
    string word;
    vector<string> tokens;
    while (ss >> word) tokens.push_back(word);
    return tokens;
}

int main() {

    ifstream in("input.txt");
    ofstream mnt("mnt.txt"), mdt("mdt.txt"), ala("ala.txt"), output("pass1_output.txt");

    string line;
    bool inMacro = false;

    while (getline(in, line)) {
        vector<string> words = split(line);
        if (words.size() == 0) continue;

        // MACRO start
        if (words[0] == "MACRO") {
            inMacro = true;
            continue;
        }

        // First line after MACRO = macro header
        if (inMacro && MNT.size() == MDT.size()) {
            // words[0] = macro name
            MNT.push_back({words[0], (int)MDT.size()});

            // Extract arguments to ALA
            for (int i = 1; i < words.size(); i++) {
                if (words[i][0] == '&')
                    ALA.push_back(words[i]);
            }

            continue;
        }

        // If macro definition in progress
        if (inMacro) {
            if (words[0] == "MEND") {
                MDT.push_back("MEND");
                inMacro = false;
            } else {
                MDT.push_back(line);
            }
            continue;
        }

        // Lines outside macro go to pass1 output
        output << line << endl;
    }

    // Write MNT
    for (auto &x : MNT)
        mnt << x.name << " " << x.mdtIndex << endl;

    // Write MDT
    for (int i = 0; i < MDT.size(); i++)
        mdt << i << " " << MDT[i] << endl;

    // Write ALA
    for (int i = 0; i < ALA.size(); i++)
        ala << i << " " << ALA[i] << endl;

    cout << "\nPASS-1 completed successfully.\nCheck mnt.txt, mdt.txt, ala.txt, pass1_output.txt\n";
    return 0;
}
