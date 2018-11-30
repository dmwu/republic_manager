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
#include <sys/time.h>         // gettimeofday()
#include <signal.h>
#include <errno.h>            // errno, perror()
#include <argp.h>

#include "global.h"
#include "util.h"

void SIG_handler(int sig) {
	signal(sig, SIG_IGN);
	run_flag = 0;
	printf("\nshutdown receiver [%d]\n", sig);
}

/* Program documentation. */
static char args_doc[] = "RECEIVER_ID";
static char doc[] = "Argp example #3 -- a program with options and arguments using argp";
/* A description of the arguments we accept. */
/* The options we understand. */
static struct argp_option options[] = { { "verbose", 'v', 0, 0, "Produce verbose output" }, { "quiet", 'q', 0, 0, "Don't produce any output" }, { "silent", 's', 0, OPTION_ALIAS }, { "interface", 'f',
		"INTERFACE", 0, "Interface name" }, { "ethtype", 't', "ETHTYPE", 0, "Ethernet type of the frame" }, { 0 } };

/* Used by main to communicate with parse_opt. */
struct arguments {
	char *args[1];
	int silent, verbose;
	char *interface;
	uint16_t ethtype;
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
	case 't':
		arguments->ethtype = (uint16_t) strtol(arg, NULL, 16);
		break;
	case ARGP_KEY_ARG:
		if (state->arg_num >= 1)
			/* Too many arguments. */
			argp_usage(state);

		arguments->args[state->arg_num] = arg;

		break;

	case ARGP_KEY_END:
		if (state->arg_num < 1)
			/* Not enough arguments. */
			argp_usage(state);
		break;

	default:
		return ARGP_ERR_UNKNOWN;
	}
	return 0;
}
/* Our argp parser. */
static struct argp argp = { options, parse_opt, args_doc, doc };

int main(int argc, char **argv) {
	/* Parse arguments */
	struct arguments arguments;
	/* Default values. */
	arguments.silent = 0;
	arguments.verbose = 0;
	arguments.interface = DEFAULT_INTERFACE;
	arguments.ethtype = DEFAULT_ETHERNET_TYPE;

	/* Parse our arguments; every option seen by parse_opt will
	 be reflected in arguments. */
	argp_parse(&argp, argc, argv, 0, 0, &arguments);

	printf("INTERFACE = %s\n"
			"RECEIVER_ID = %s\n"
			"VERBOSE = %s\n"
			"SILENT = %s\n", arguments.interface, arguments.args[0], arguments.verbose ? "yes" : "no", arguments.silent ? "yes" : "no");

	signal(SIGTERM, SIG_handler);
	signal(SIGKILL, SIG_handler);
	signal(SIGINT, SIG_handler);

//	int i, status,
	int i; //, datalen,
//	int frame_length,
	int sendsd, recvsd, bytes;
//	*ip_flags,
	int timeout;
//	char *interface, *target, *src_ip, *dst_ip, *rec_ip;
//	struct ip send_iphdr, *recv_iphdr;
//	struct icmp send_icmphdr, *recv_icmphdr;
//	uint8_t *data,
	uint8_t *src_mac; //, *dst_mac,
	uint8_t *ether_frame;
//	struct addrinfo hints, *res;
//	struct sockaddr_in *ipv4;
	struct sockaddr_ll device;
	struct ifreq ifr;
	struct sockaddr from;
	socklen_t fromlen;
	struct timeval wait; //, t1, t2;
//	struct timezone tz;
//	double dt;
//	void *tmp;

	struct timeval tv;
	unsigned int sequence;
	unsigned int sec;
	unsigned int usec;

	struct timeval tv_last;
	unsigned int sequence_last = 0;
	unsigned int sec_last;
	unsigned int usec_last;

	unsigned int * sequence_p;
	unsigned int * sec_p;
	unsigned int * usec_p;

	char f_name[IP_MAXPACKET];
    FILE *f;

//	signal(SIGINT, SIG_handler);
	// Allocate memory for various arrays.
	src_mac = allocate_ustrmem(ETH_ALEN);
//  dst_mac = allocate_ustrmem (6);
//  data = allocate_ustrmem (IP_MAXPACKET);
//  send_ether_frame = allocate_ustrmem (IP_MAXPACKET);
//	f_name = allocate_strmem(IP_MAXPACKET);
	ether_frame = allocate_ustrmem(IP_MAXPACKET);
//	interface = allocate_strmem(40);
//  target = allocate_strmem (40);
//  src_ip = allocate_strmem (INET_ADDRSTRLEN);
//  dst_ip = allocate_strmem (INET_ADDRSTRLEN);
//  rec_ip = allocate_strmem (INET_ADDRSTRLEN);
//  ip_flags = allocate_intmem (4);

// Interface to send packet through.
//	strcpy(interface, argv[1]);

	// Submit request for a socket descriptor to look up interface.
	// We'll use it to send packets as well, so we leave it open.
	if ((sendsd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0) {
		perror("socket() failed to get socket descriptor for using ioctl() ");
		exit(EXIT_FAILURE);
	}

	// Use ioctl() to look up interface name and get its MAC address.
	memset(&ifr, 0, sizeof(ifr));
	snprintf(ifr.ifr_name, sizeof(ifr.ifr_name), "%s", arguments.interface);
	if (ioctl(sendsd, SIOCGIFHWADDR, &ifr) < 0) {
		perror("ioctl() failed to get source MAC address ");
		return (EXIT_FAILURE);
	}
	// Copy source MAC address.
	memcpy(src_mac, ifr.ifr_hwaddr.sa_data, ETH_ALEN);
	close(sendsd);

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
	/*
	 // Set destination MAC address: you need to fill these out
	 dst_mac[0] = 0xff;
	 dst_mac[1] = 0xff;
	 dst_mac[2] = 0xff;
	 dst_mac[3] = 0xff;
	 dst_mac[4] = 0xff;
	 dst_mac[5] = 0xff;

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
	/*
	 // ICMP data
	 datalen = 4;
	 data[0] = 'T';
	 data[1] = 'e';
	 data[2] = 's';
	 data[3] = 't';

	 // IPv4 header

	 // IPv4 header length (4 bits): Number of 32-bit words in header = 5
	 send_iphdr.ip_hl = IP4_HDRLEN / sizeof (uint32_t);

	 // Internet Protocol version (4 bits): IPv4
	 send_iphdr.ip_v = 4;

	 // Type of service (8 bits)
	 send_iphdr.ip_tos = 0;

	 // Total length of datagram (16 bits): IP header + ICMP header + ICMP data
	 send_iphdr.ip_len = htons (IP4_HDRLEN + ICMP_HDRLEN + datalen);

	 // ID sequence number (16 bits): unused, since single datagram
	 send_iphdr.ip_id = htons (0);

	 // Flags, and Fragmentation offset (3, 13 bits): 0 since single datagram

	 // Zero (1 bit)
	 ip_flags[0] = 0;

	 // Do not fragment flag (1 bit)
	 ip_flags[1] = 0;

	 // More fragments following flag (1 bit)
	 ip_flags[2] = 0;

	 // Fragmentation offset (13 bits)
	 ip_flags[3] = 0;

	 send_iphdr.ip_off = htons ((ip_flags[0] << 15)
	 + (ip_flags[1] << 14)
	 + (ip_flags[2] << 13)
	 +  ip_flags[3]);

	 // Time-to-Live (8 bits): default to maximum value
	 send_iphdr.ip_ttl = 255;

	 // Transport layer protocol (8 bits): 1 for ICMP
	 send_iphdr.ip_p = IPPROTO_ICMP;

	 // Source IPv4 address (32 bits)
	 if ((status = inet_pton (AF_INET, src_ip, &(send_iphdr.ip_src))) != 1) {
	 fprintf (stderr, "inet_pton() failed.\nError message: %s", strerror (status));
	 exit (EXIT_FAILURE);
	 }

	 // Destination IPv4 address (32 bits)
	 if ((status = inet_pton (AF_INET, dst_ip, &(send_iphdr.ip_dst))) != 1) {
	 fprintf (stderr, "inet_pton() failed.\nError message: %s", strerror (status));
	 exit (EXIT_FAILURE);
	 }

	 // IPv4 header checksum (16 bits): set to 0 when calculating checksum
	 send_iphdr.ip_sum = 0;
	 send_iphdr.ip_sum = checksum ((uint16_t *) &send_iphdr, IP4_HDRLEN);

	 // ICMP header

	 // Message Type (8 bits): echo request
	 send_icmphdr.icmp_type = ICMP_ECHO;

	 // Message Code (8 bits): echo request
	 send_icmphdr.icmp_code = 0;

	 // Identifier (16 bits): usually pid of sending process - pick a number
	 send_icmphdr.icmp_id = htons (1000);

	 // Sequence Number (16 bits): starts at 0
	 send_icmphdr.icmp_seq = htons (0);

	 // ICMP header checksum (16 bits): set to 0 when calculating checksum
	 send_icmphdr.icmp_cksum = icmp4_checksum (send_icmphdr, data, datalen);

	 // Fill out ethernet frame header.

	 // Ethernet frame length = ethernet header (MAC + MAC + ethernet type) + ethernet data (IP header + ICMP header + ICMP data)
	 frame_length = 6 + 6 + 2 + IP4_HDRLEN + ICMP_HDRLEN + datalen;

	 // Destination and Source MAC addresses
	 memcpy (send_ether_frame, dst_mac, 6);
	 memcpy (send_ether_frame + 6, src_mac, 6);

	 // Next is ethernet type code (ETH_P_IP for IPv4).
	 // http://www.iana.org/assignments/ethernet-numbers
	 send_ether_frame[12] = ETH_P_IP / 256;
	 send_ether_frame[13] = ETH_P_IP % 256;

	 // Next is ethernet frame data (IPv4 header + ICMP header + ICMP data).

	 // IPv4 header
	 memcpy (send_ether_frame + ETH_HDRLEN, &send_iphdr, IP4_HDRLEN);

	 // ICMP header
	 memcpy (send_ether_frame + ETH_HDRLEN + IP4_HDRLEN, &send_icmphdr, ICMP_HDRLEN);

	 // ICMP data
	 memcpy (send_ether_frame + ETH_HDRLEN + IP4_HDRLEN + ICMP_HDRLEN, data, datalen);
	 */
	// Submit request for a raw socket descriptor to receive packets.
	if ((recvsd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0) {
		perror("socket() failed to obtain a receive socket descriptor ");
		exit(EXIT_FAILURE);
	}

	// Set maximum number of tries to ping remote host before giving up.
//  trylim = 3;
//  trycount = 0;
	/*
	 // Cast recv_iphdr as pointer to IPv4 header within received ethernet frame.
	 recv_iphdr = (struct ip *) (recv_ether_frame + ETH_HDRLEN);

	 // Case recv_icmphdr as pointer to ICMP header within received ethernet frame.
	 recv_icmphdr = (struct icmp *) (recv_ether_frame + ETH_HDRLEN + IP4_HDRLEN);
	 */

	if (bind(recvsd, (struct sockaddr *) &device, sizeof(device)) < 0) {
		perror("bind() failed to bind");
		exit(EXIT_FAILURE);
	}

	sequence_p = (unsigned int *) (ether_frame + ETH_HLEN);
	sec_p = (unsigned int *) (ether_frame + ETH_HLEN + sizeof(unsigned int) * 1);
	usec_p = (unsigned int *) (ether_frame + ETH_HLEN + sizeof(unsigned int) * 2);

//  done = 0;
//  for (;;) {
	/*
	 // SEND

	 // Send ethernet frame to socket.
	 if ((bytes = sendto (sendsd, send_ether_frame, frame_length, 0, (struct sockaddr *) &device, sizeof (device))) <= 0) {
	 perror ("sendto() failed ");
	 exit (EXIT_FAILURE);
	 }
	 */
	// Start timer.
//    (void) gettimeofday (&t1, &tz);
	// Set time for the socket to timeout and give up waiting for a reply.
	timeout = 50;
	wait.tv_sec = 0;
	wait.tv_usec = timeout * 1000;
	if (setsockopt(recvsd, SOL_SOCKET, SO_RCVTIMEO, (char *) &wait, sizeof(struct timeval)) < 0) {
		perror("setsockopt() SO_RCVTIMEO failed ");
		exit(EXIT_FAILURE);
	}
	/*
	 if (setsockopt (recvsd, SOL_SOCKET, SO_BINDTODEVICE, argv[1], strlen (argv[1])) < 0){
	 perror ("setsockopt() SO_BINDTODEVICE failed ");
	 exit (EXIT_FAILURE);
	 }
	 */
	// Listen for incoming ethernet frame from socket recvsd.
	// We expect an ICMP ethernet frame of the form:
	//     MAC (6 bytes) + MAC (6 bytes) + ethernet type (2 bytes)
	//     + ethernet data (IPv4 header + ICMP header)
	// Keep at it for 'timeout' seconds, or until we get an ICMP reply.
	sprintf(f_name, "%s_%s.csv", arguments.args[0], arguments.interface);
	if ((f = fopen(f_name, "w")) == NULL) {
		perror("Error opening file!\n");
		exit(EXIT_FAILURE);
	}

//	strcpy(f_name, argv[1]);
//	strcat(f_name, "-");
//	strcat(f_name, argv[2]);
//	strcat(f_name, ".recv.bold");
//	if ((f_recv = fopen(f_name, "w")) == NULL) {
//		printf("Error opening file!\n");
//		exit(1);
//	}

//	receiving = 0;
	sequence_last = 0;
	while (run_flag) {
//		memset(ether_frame, 0, IP_MAXPACKET * sizeof(uint8_t));
		memset(&from, 0, sizeof(struct sockaddr));
		fromlen = sizeof(struct sockaddr);
		bytes = recvfrom(recvsd, ether_frame, IP_MAXPACKET, 0, (struct sockaddr *) &from, &fromlen);
		if (bytes < 0) {	//			status = errno;			// Deal with error conditions first.
			if (errno == EAGAIN) {  // EAGAIN = 11
//				if (receiving == 1) {
//					receiving = 0;
////					dt = (double) (tr.tv_sec - sec_h) * 1000.0 + (double) (tr.tv_usec - usec_h) / 1000.0;
//					fprintf(f_recv, "%d\t%d\n", (int) (tr.tv_sec), (int) (tr.tv_usec));
//				}
				continue;
			} else if (errno == EINTR) {  // EINTR = 4
				continue; // Something weird happened, but let's keep listening.
			} else {
				perror("recvfrom() failed ");
				exit(EXIT_FAILURE);
			}
		} else if (bytes > 0) {
			if (ntohs(*(unsigned short *) (ether_frame + ETH_ALEN * 2)) == arguments.ethtype) {
				gettimeofday(&tv, NULL);
				//			receiving = 1;

				//time_stamp = (double)(ntohl(*sec)) * 1000.0 + (double)(ntohl(*usec))/1000.0;
				sequence = ntohl(*sequence_p);
				sec = ntohl(*sec_p);
				usec = ntohl(*usec_p);
				if (sequence_last != 0)
					if (sequence != sequence_last + 1) {
						fprintf(f, "s,%d,%d,%d,%d,%d\n", sequence_last, sec_last, usec_last, (int) (tv_last.tv_sec), (int) (tv_last.tv_usec));
						fprintf(f, "e,%d,%d,%d,%d,%d\n", sequence, sec, usec, (int) (tv.tv_sec), (int) (tv.tv_usec));
						fflush(f);
					}
				sequence_last = sequence;
				sec_last = sec;
				usec_last = usec;
				tv_last = tv;

				//        if (offset == 0){
				//          offset = sec_h/100;
				//        }
				//        time_stamp = (sec_h - offset*100) * 1000 * 1000 + usec_h;
				//        printf("%d\t%d\n", ntohl(*count), time_stamp);
				if (arguments.verbose)
					printf("%d,%d,%d,%d,%d\n", sequence, sec, usec, (int) (tv.tv_sec), (int) (tv.tv_usec));

				// fprintf(f, "%d\t%d\t%d\n", ntohl(*count), sec_h, usec_h);
				// printf("%d\t%d\t%d\n", ntohl(*count), sec_h, usec_h);
				//printf("receiving packet: count: %d\t@%d.%d\n", ntohl(*count), ntohl(*sec), ntohl(*usec));

				// Stop timer and calculate how long it took to get a reply.
				/*        (void) gettimeofday (&t2, &tz);
				 dt = (double) (t2.tv_sec - t1.tv_sec) * 1000.0 + (double) (t2.tv_usec - t1.tv_usec) / 1000.0;
				 */
				// Extract source IP address from received ethernet frame.
				/*        if (inet_ntop (AF_INET, &(recv_iphdr->ip_src.s_addr), rec_ip, INET_ADDRSTRLEN) == NULL) {
				 status = errno;
				 fprintf (stderr, "inet_ntop() failed.\nError message: %s", strerror (status));
				 exit (EXIT_FAILURE);
				 }*/

				// Report source IPv4 address and time for reply.
				/*        printf ("%s  %g ms (%i bytes received)\n", rec_ip, dt, bytes);
				 done = 1;
				 break;  // Break out of Receive loop.*/
			}  // End if IP ethernet frame carrying ICMP_ECHOREPLY
		}
	}  // End of Receive loop.

	// The 'done' flag was set because an echo reply was received; break out of send loop.
	/*    if (done == 1) {
	 break;  // Break out of Send loop.
	 }
	 */
	// We ran out of tries, so let's give up.
	/*    if (trycount == trylim) {
	 printf ("Recognized no echo replies from remote host after %i tries.\n", trylim);
	 break;
	 }*/

//  }  // End of Send loop.
	// Close socket descriptors.
//  close (sendsd);
	close(recvsd);
//	fclose(f);

	// Free allocated memory.
//  free (src_mac);
//  free (dst_mac);
//  free (data);
//  free (send_ether_frame);
	free(ether_frame);
//  free (interface);
//  free (target);
//  free (src_ip);
//  free (dst_ip);
//  free (rec_ip);
//  free (ip_flags);

	fflush(f);
	fclose(f);
//	fflush(f_recv);
//	fclose(f_recv);
	printf("byebye\n");
	return (EXIT_SUCCESS);
}
