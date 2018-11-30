/*
 * sender.c
 *
 *  Created on: Dec 19, 2017
 *      Author: xs6
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>           // close()
#include <string.h>           // strcpy, memset(), and memcpy()

#include <netdb.h>            // struct addrinfo
#include <sys/types.h>        // needed for socket(), uint8_t, uint16_t, uint32_t
#include <sys/socket.h>       // needed for socket()
#include <netinet/in.h>       // IPPROTO_ICMP, INET_ADDRSTRLEN
#include <netinet/ip.h>       // struct ip and IP_MAXPACKET (which is 65535)
#include <netinet/ip_icmp.h>  // struct icmp, ICMP_ECHO
#include <arpa/inet.h>        // inet_pton() and inet_ntop()
#include <sys/ioctl.h>        // macro ioctl is defined
#include <bits/ioctls.h>      // defines values for argument "request" of ioctl.
#include <net/if.h>           // struct ifreq
#include <linux/if_ether.h>   // ETH_P_IP = 0x0800, ETH_P_IPV6 = 0x86DD
#include <linux/if_packet.h>  // struct sockaddr_ll (see man 7 packet)
#include <net/ethernet.h>
#include <sys/time.h>
#include <time.h>
#include <errno.h>            // errno, perror()
#include <signal.h>
#include <argp.h>

#include "global.h"

void SIG_handler(int sig) {
	signal(sig, SIG_IGN);
	run_flag = 0;
	printf("\nshutdown sender [%d]\n", sig);
}

/* argp variables */
//const char *argp_program_version = "switch_measurement v0.5.0";
//const char *argp_program_bug_address = "<sunxiaoye07@gmail.com>";
/* Program documentation. */
static char doc[] = "Argp example #3 -- a program with options and arguments using argp";
/* A description of the arguments we accept. */
/* The options we understand. */
static struct argp_option options[] = { { "verbose", 'v', 0, 0, "Produce verbose output" }, { "quiet", 'q', 0, 0, "Don't produce any output" }, { "silent", 's', 0, OPTION_ALIAS }, { "interface", 'f',
		"INTERFACE", 0, "Interface name" }, { "ethtype", 't', "ETHTYPE", 0, "Ethernet type of the frame" }, { "interval", 'i', "INTERVAL", 0, "Interval between packets in micro-seconds" }, { "bytes",
		'b', "BYTES", 0, "Bytes in a packet" }, { 0 } };

/* Used by main to communicate with parse_opt. */
struct arguments {
	int silent, verbose;
	char *interface;
	uint16_t ethtype;
	int interval;
	int bytes;
};

/* Parse a single option. */
static error_t parse_opt(int key, char *arg, struct argp_state *state) {
	/* Get the input argument from argp_parse, which we
	 know is a pointer to our arguments structure. */
	struct arguments *arguments = state->input;

	switch (key) {
	case 'q':
	case 's':
		arguments->silent = 1;
		break;
	case 'v':
		arguments->verbose = 1;
		break;
	case 'f':
		arguments->interface = arg;
		break;
	case 'i':
		arguments->interval = (uint32_t) strtoull(arg, NULL, 0);
		break;
	case 'b':
		arguments->bytes = (uint32_t) strtoull(arg, NULL, 0);
		break;
	case 't':
		arguments->ethtype = (uint16_t) strtol(arg, NULL, 16);
		break;
	case ARGP_KEY_ARG:
		if (state->arg_num >= 0)
			/* Too many arguments. */
			argp_usage(state);
		break;

	case ARGP_KEY_END:
		if (state->arg_num < 0)
			/* Not enough arguments. */
			argp_usage(state);
		break;

	default:
		return ARGP_ERR_UNKNOWN;
	}
	return 0;
}
/* Our argp parser. */
static struct argp argp = { options, parse_opt, doc };

int main(int argc, char **argv) {

	/* Parse arguments */
	struct arguments arguments;
	/* Default values. */
	arguments.silent = 0;
	arguments.verbose = 0;
	arguments.interface = DEFAULT_INTERFACE;
	arguments.interval = DEFAULT_INTERVAL_US;
	arguments.bytes = DEFAULT_BYTES;

	/* Parse our arguments; every option seen by parse_opt will
	 be reflected in arguments. */
	argp_parse(&argp, argc, argv, 0, 0, &arguments);

	printf("INTERVAL = %d us\n"
			"BYTES = %d\n"
			"INTERFACE = %s\n"
			"VERBOSE = %s\n"
			"SILENT = %s\n", arguments.interval, arguments.bytes, arguments.interface, arguments.verbose ? "yes" : "no", arguments.silent ? "yes" : "no");

	signal(SIGTERM, SIG_handler);
	signal(SIGKILL, SIG_handler);
	signal(SIGINT, SIG_handler);

	/* Start main program */
	int sd, bytes; //, *ip_flags; //status, datalen,frame_length
	uint8_t *src_mac, *dst_mac, *ether_frame; //*data,
//	char *interface,
//	char *target, *src_ip, *dst_ip;
//	struct ip iphdr;
//  struct icmp icmphdr;

//	struct addrinfo hints, *res;
//	struct sockaddr_in *ipv4;
	struct sockaddr_ll device;
	struct ifreq ifr;
//  void *tmp;

//	struct timespec req;
//	struct timespec rem;

//	struct timezone tz;
//	unsigned int usecs;
	// packet payload
	unsigned int i;
	struct timeval tv;
	unsigned int sequence;
	unsigned int sec;
	unsigned int usec;
//	unsigned int packet_interval;
//	unsigned int packet_number;

// Allocate memory for various arrays.
	src_mac = allocate_ustrmem(ETH_ALEN);
	dst_mac = allocate_ustrmem(ETH_ALEN);
//	data = allocate_ustrmem(IP_MAXPACKET);
	ether_frame = allocate_ustrmem(IP_MAXPACKET);
//	interface = allocate_strmem(40);
	//target = allocate_strmem (40);
	//src_ip = allocate_strmem (INET_ADDRSTRLEN);
	//dst_ip = allocate_strmem (INET_ADDRSTRLEN);
	//ip_flags = allocate_intmem (4);

	// Interface to send packet through.
//	strcpy(interface, argv[1]);

	// Submit request for a socket descriptor to look up interface.
	if ((sd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0) {
		perror("socket() failed to get socket descriptor for using ioctl() ");
		exit(EXIT_FAILURE);
	}

	// Use ioctl() to look up interface name and get its MAC address.
	memset(&ifr, 0, sizeof(ifr));
	snprintf(ifr.ifr_name, sizeof(ifr.ifr_name), "%s", arguments.interface);
	if (ioctl(sd, SIOCGIFHWADDR, &ifr) < 0) {
		perror("ioctl() failed to get source MAC address ");
		exit(EXIT_FAILURE);
	}
	close(sd);

	// Copy source MAC address.
	memcpy(src_mac, ifr.ifr_hwaddr.sa_data, ETH_ALEN);

	// Report source MAC address to stdout.
	printf("MAC address for interface %s is ", arguments.interface);
	for (i = 0; i < ETH_ALEN; i++) {
		printf("%02x%s", src_mac[i], (i == ETH_ALEN - 1) ? "\n" : ":");
	}

	// Find interface index from interface name and store index in
	// struct sockaddr_ll device, which will be used as an argument of sendto().
	memset(&device, 0, sizeof(device));
	if ((device.sll_ifindex = if_nametoindex(arguments.interface)) == 0) {
		perror("if_nametoindex() failed to obtain interface index ");
		exit(EXIT_FAILURE);
	}
	printf("Index for interface %s is %i\n", arguments.interface, device.sll_ifindex);

	// Set destination MAC address: you need to fill these out
	for (i = 0; i < ETH_ALEN; i++) {
		dst_mac[i] = 0xff;
	}

	/*
	 // Source IPv4 address: you need to fill this out
	 strcpy (src_ip, "[INTERNAL_NETWORK_PREFIX].1.132");

	 // Destination URL or IPv4 address: you need to fill this out
	 strcpy (target, "www.google.com");

	 // Fill out hints for getaddrinfo().
	 memset (&hints, 0, sizeof (struct addrinfo));
	 hints.ai_family = AF_INET;
	 hints.ai_socktype = SOCK_STREAM;
	 hints.ai_flags = hints.ai_flags | AI_CANONNAME;

	 // Resolve target using getaddrinfo().
	 if ((status = getaddrinfo (target, NULL, &hints, &res)) != 0) {
	 fprintf (stderr, "getaddrinfo() failed: %s\n", gai_strerror (status));
	 exit (EXIT_FAILURE);
	 }
	 ipv4 = (struct sockaddr_in *) res->ai_addr;
	 tmp = &(ipv4->sin_addr);
	 if (inet_ntop (AF_INET, tmp, dst_ip, INET_ADDRSTRLEN) == NULL) {
	 status = errno;
	 fprintf (stderr, "inet_ntop() failed.\nError message: %s", strerror (status));
	 exit (EXIT_FAILURE);
	 }
	 freeaddrinfo (res);
	 */
	// Fill out sockaddr_ll.
	device.sll_family = AF_PACKET;
	memcpy(device.sll_addr, src_mac, ETH_ALEN);
	device.sll_halen = htons(ETH_ALEN);

	// ICMP data
//	datalen = 4;
//	data[0] = 'T';
//	data[1] = 'e';
//	data[2] = 's';
//	data[3] = 't';
	/*
	 // IPv4 header

	 // IPv4 header length (4 bits): Number of 32-bit words in header = 5
	 iphdr.ip_hl = IP4_HDRLEN / sizeof (uint32_t);

	 // Internet Protocol version (4 bits): IPv4
	 iphdr.ip_v = 4;

	 // Type of service (8 bits)
	 iphdr.ip_tos = 0;

	 // Total length of datagram (16 bits): IP header + ICMP header + ICMP data
	 iphdr.ip_len = htons (IP4_HDRLEN + ICMP_HDRLEN + datalen);

	 // ID sequence number (16 bits): unused, since single datagram
	 iphdr.ip_id = htons (0);

	 // Flags, and Fragmentation offset (3, 13 bits): 0 since single datagram

	 // Zero (1 bit)
	 ip_flags[0] = 0;

	 // Do not fragment flag (1 bit)
	 ip_flags[1] = 0;

	 // More fragments following flag (1 bit)
	 ip_flags[2] = 0;

	 // Fragmentation offset (13 bits)
	 ip_flags[3] = 0;

	 iphdr.ip_off = htons ((ip_flags[0] << 15)
	 + (ip_flags[1] << 14)
	 + (ip_flags[2] << 13)
	 +  ip_flags[3]);

	 // Time-to-Live (8 bits): default to maximum value
	 iphdr.ip_ttl = 255;

	 // Transport layer protocol (8 bits): 1 for ICMP
	 iphdr.ip_p = IPPROTO_ICMP;

	 // Source IPv4 address (32 bits)
	 if ((status = inet_pton (AF_INET, src_ip, &(iphdr.ip_src))) != 1) {
	 fprintf (stderr, "inet_pton() failed.\nError message: %s", strerror (status));
	 exit (EXIT_FAILURE);
	 }

	 // Destination IPv4 address (32 bits)
	 if ((status = inet_pton (AF_INET, dst_ip, &(iphdr.ip_dst))) != 1) {
	 fprintf (stderr, "inet_pton() failed.\nError message: %s", strerror (status));
	 exit (EXIT_FAILURE);
	 }

	 // IPv4 header checksum (16 bits): set to 0 when calculating checksum
	 iphdr.ip_sum = 0;
	 iphdr.ip_sum = checksum ((uint16_t *) &iphdr, IP4_HDRLEN);

	 // ICMP header

	 // Message Type (8 bits): echo request
	 icmphdr.icmp_type = ICMP_ECHO;

	 // Message Code (8 bits): echo request
	 icmphdr.icmp_code = 0;

	 // Identifier (16 bits): usually pid of sending process - pick a number
	 icmphdr.icmp_id = htons (1000);

	 // Sequence Number (16 bits): starts at 0
	 icmphdr.icmp_seq = htons (0);

	 // ICMP header checksum (16 bits): set to 0 when calculating checksum
	 icmphdr.icmp_cksum = icmp4_checksum (icmphdr, data, datalen);
	 */
	// Fill out ethernet frame header.
	// Ethernet frame length = ethernet header (MAC + MAC + ethernet type) + ethernet data (IP header + ICMP header + ICMP data)
	//frame_length = 6 + 6 + 2 + 3 * sizeof(unsigned int) + datalen;
//	frame_length = ETH_FRAME_LEN;
	// Destination and Source MAC addresses
	memcpy(ether_frame, dst_mac, ETH_ALEN);
	memcpy(ether_frame + ETH_ALEN, src_mac, ETH_ALEN);

	// Next is ethernet type code (ETH_P_IP for IPv4).
	// http://www.iana.org/assignments/ethernet-numbers
	*(unsigned short *) (ether_frame + ETH_ALEN * 2) = htons(arguments.ethtype);
	// Next is ethernet frame data (IPv4 header + ICMP header + ICMP data).
	/*
	 // IPv4 header
	 memcpy (ether_frame + ETH_HDRLEN, &iphdr, IP4_HDRLEN);

	 // ICMP header
	 memcpy (ether_frame + ETH_HDRLEN + IP4_HDRLEN, &icmphdr, ICMP_HDRLEN);

	 // ICMP data
	 memcpy (ether_frame + ETH_HDRLEN + IP4_HDRLEN + ICMP_HDRLEN, data, datalen);
	 */

//  printf("sizeof(struct timeval) = %d\n", (int)sizeof(struct timeval));
//  printf("sizeof(time_t) = %d\n", (int)sizeof(time_t));
//  printf("sizeof(suseconds_t) = %d\n", (int)sizeof(suseconds_t));
	// Submit request for a raw socket descriptor.
	if ((sd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0) {
		perror("socket() failed ");
		exit(EXIT_FAILURE);
	}

	i = 0;
	while (run_flag) {
		usleep(arguments.interval);

		sequence = htonl(i++);	// update the sequence number
		gettimeofday(&tv, NULL); // get the current time
		sec = htonl(tv.tv_sec);
		usec = htonl(tv.tv_usec);

		// update the time
		memcpy(ether_frame + ETH_HLEN + sizeof(unsigned int) * 0, &sequence, sizeof(unsigned int));
		memcpy(ether_frame + ETH_HLEN + sizeof(unsigned int) * 1, &sec, sizeof(unsigned int));
		memcpy(ether_frame + ETH_HLEN + sizeof(unsigned int) * 2, &usec, sizeof(unsigned int));
		// send the packet
		if ((bytes = sendto(sd, ether_frame, arguments.bytes, 0, (struct sockaddr *) &device, sizeof(device))) <= 0) {
			perror("sendto() failed");
			exit(EXIT_FAILURE);
		}
		if (arguments.verbose)
			printf("sent packet: [%d]\t@%ld.%ld\n", i, tv.tv_sec, tv.tv_usec);
	}
	close(sd);

	// Free allocated memory.
	free(src_mac);
	free(dst_mac);
	free(ether_frame);
//	free(interface);
	//free (target);
	//free (src_ip);
	//free (dst_ip);
	//free (ip_flags);
	printf("byebye\n");

	return (EXIT_SUCCESS);
}
