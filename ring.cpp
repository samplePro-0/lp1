#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

void bully(int start, vector<int> p) {
    cout << "\nBully Election started by P" << start << "\n";
    int leader = start;
    while (true) {
        vector<int> higher;
        for (int x : p) if (x > leader) higher.push_back(x);
        if (higher.empty()) {
            cout << "P" << leader << " becomes COORDINATOR.\n";
            return;
        }
        cout << "P" << leader << " sends ELECTION to P";
        for (int x : higher) cout << x << " ";
        cout << "\nP" << leader << " drops out.\n";
        leader = *min_element(higher.begin(), higher.end());
    }
}

void ring(int start, vector<int> p) {
    cout << "\nRing Election started by P" << start << "\n";
    sort(p.begin(), p.end());
    vector<int> msg = {start};
    int i = find(p.begin(), p.end(), start) - p.begin(), n = p.size();
    for (int idx = (i+1)%n; p[idx] != start; idx=(idx+1)%n) {
        cout << "Msg from P" << msg.back() << " to P" << p[idx] << ". Msg: ";
        for (int x : msg) cout << x << " ";
        cout << "\n";
        msg.push_back(p[idx]);
    }
    cout << "Msg back to P" << start << ". Final msg: ";
    for (int x : msg) cout << x << " ";
    cout << "\nP" << *max_element(msg.begin(), msg.end()) << " is COORDINATOR.\n";
}
int main() {
    int n;
    cout << "Enter total number of processes: ";
    cin >> n;
    if (n <= 0) {
        cout << "Must have at least one process.\n";
        return 0;
    }

    vector<int> processes(n);
    cout << "Enter process IDs:\n";
    for (int i = 0; i < n; ++i) {
        cin >> processes[i];
    }

    int choice, start;
    do {
        cout << "\n1-Bully 2-Ring 3-Exit: ";
        cin >> choice;
        if (choice == 1 || choice == 2) {
            cout << "Start Process: ";
            cin >> start;
            if (find(processes.begin(), processes.end(), start) == processes.end()) {
                cout << "Invalid process ID.\n";
                continue;
            }
            if (choice == 1)
                bully(start, processes);
            else
                ring(start, processes);
        }
    } while (choice != 3);
}

