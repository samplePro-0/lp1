#include <iostream>
#include <vector>
using namespace std;

void display(const vector<int> &b) {
    cout << "\nBlock\tSize\n";
    for (int i = 0; i < b.size(); i++)
        cout << i + 1 << "\t" << b[i] << "\n";
}

bool firstFit(vector<int> &b, int p, int id) {
    for (int i = 0; i < b.size(); i++) {
        if (b[i] >= p) {
            cout << "P" << id << " (" << p << ") -> B" << i + 1 << "\n";
            b[i] -= p;
            return true;
        }
    }
    cout << "P" << id << " (" << p << ") -> Not Allocated\n";
    return false;
}

bool bestFit(vector<int> &b, int p, int id) {
    int idx = -1;
    for (int i = 0; i < b.size(); i++)
        if (b[i] >= p && (idx == -1 || b[i] < b[idx]))
            idx = i;
    if (idx != -1) {
        cout << "P" << id << " (" << p << ") -> B" << idx + 1 << "\n";
        b[idx] -= p;
        return true;
    }
    cout << "P" << id << " (" << p << ") -> Not Allocated\n";
    return false;
}

bool worstFit(vector<int> &b, int p, int id) {
    int idx = -1;
    for (int i = 0; i < b.size(); i++)
        if (b[i] >= p && (idx == -1 || b[i] > b[idx]))
            idx = i;
    if (idx != -1) {
        cout << "P" << id << " (" << p << ") -> B" << idx + 1 << "\n";
        b[idx] -= p;
        return true;
    }
    cout << "P" << id << " (" << p << ") -> Not Allocated\n";
    return false;
}

bool nextFit(vector<int> &b, int p, int id, int &pos) {
    int n = b.size(), cnt = 0;
    while (cnt < n) {
        if (b[pos] >= p) {
            cout << "P" << id << " (" << p << ") -> B" << pos + 1 << "\n";
            b[pos] -= p;
            pos = (pos + 1) % n;
            return true;
        }
        pos = (pos + 1) % n;
        cnt++;
    }
    cout << "P" << id << " (" << p << ") -> Not Allocated\n";
    return false;
}

int main() {
    int nb, np;
    cout << "Blocks: ";
    cin >> nb;
    vector<int> blocks(nb);
    for (int i = 0; i < nb; i++)
        cin >> blocks[i];

    cout << "Processes: ";
    cin >> np;
    vector<int> procs(np);
    for (int i = 0; i < np; i++)
        cin >> procs[i];

    int pos = 0;
    for (int i = 0; i < np; i++) {
        cout << "\nP" << i + 1 << " (" << procs[i] << "): 1-FF 2-BF 3-WF 4-NF: ";
        int c;
        cin >> c;
        switch (c) {
            case 1: firstFit(blocks, procs[i], i + 1); break;
            case 2: bestFit(blocks, procs[i], i + 1); break;
            case 3: worstFit(blocks, procs[i], i + 1); break;
            case 4: nextFit(blocks, procs[i], i + 1, pos); break;
        }
        display(blocks);
    }
    return 0;
}
