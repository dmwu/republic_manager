/*
 * util.c
 *
 *  Created on: Dec 20, 2017
 *      Author: xs6
 */

#include "util.h"

// Build IPv4 ICMP pseudo-header and call checksum function.
uint16_t icmp4_checksum(struct icmp icmphdr, uint8_t *payload, int payloadlen) {
	char buf[IP_MAXPACKET];
	char *ptr;
	int chksumlen = 0;
	int i;

	ptr = &buf[0];  // ptr points to beginning of buffer buf

	// Copy Message Type to buf (8 bits)
	memcpy(ptr, &icmphdr.icmp_type, sizeof(icmphdr.icmp_type));
	ptr += sizeof(icmphdr.icmp_type);
	chksumlen += sizeof(icmphdr.icmp_type);

	// Copy Message Code to buf (8 bits)
	memcpy(ptr, &icmphdr.icmp_code, sizeof(icmphdr.icmp_code));
	ptr += sizeof(icmphdr.icmp_code);
	chksumlen += sizeof(icmphdr.icmp_code);

	// Copy ICMP checksum to buf (16 bits)
	// Zero, since we don't know it yet
	*ptr = 0;
	ptr++;
	*ptr = 0;
	ptr++;
	chksumlen += 2;

	// Copy Identifier to buf (16 bits)
	memcpy(ptr, &icmphdr.icmp_id, sizeof(icmphdr.icmp_id));
	ptr += sizeof(icmphdr.icmp_id);
	chksumlen += sizeof(icmphdr.icmp_id);

	// Copy Sequence Number to buf (16 bits)
	memcpy(ptr, &icmphdr.icmp_seq, sizeof(icmphdr.icmp_seq));
	ptr += sizeof(icmphdr.icmp_seq);
	chksumlen += sizeof(icmphdr.icmp_seq);

	// Copy payload to buf
	memcpy(ptr, payload, payloadlen);
	ptr += payloadlen;
	chksumlen += payloadlen;

	// Pad to the next 16-bit boundary
	for (i = 0; i < payloadlen % 2; i++, ptr++) {
		*ptr = 0;
		ptr++;
		chksumlen++;
	}

	return checksum((uint16_t *) buf, chksumlen);
}

// Checksum function
uint16_t checksum(uint16_t *addr, int len) {
	int nleft = len;
	int sum = 0;
	uint16_t *w = addr;
	uint16_t answer = 0;

	while (nleft > 1) {
		sum += *w++;
		nleft -= sizeof(uint16_t);
	}

	if (nleft == 1) {
		*(uint8_t *) (&answer) = *(uint8_t *) w;
		sum += answer;
	}

	sum = (sum >> 16) + (sum & 0xFFFF);
	sum += (sum >> 16);
	answer = ~sum;
	return (answer);
}

// Allocate memory for an array of chars.
char *
allocate_strmem(int len) {
	void *tmp;

	if (len <= 0) {
		fprintf(stderr, "ERROR: Cannot allocate memory because len = %i in allocate_strmem().\n", len);
		exit(EXIT_FAILURE);
	}

	tmp = (char *) malloc(len * sizeof(char));
	if (tmp != NULL) {
		memset(tmp, 0, len * sizeof(char));
		return (tmp);
	} else {
		fprintf(stderr, "ERROR: Cannot allocate memory for array allocate_strmem().\n");
		exit(EXIT_FAILURE);
	}
}

// Allocate memory for an array of unsigned chars.
uint8_t *
allocate_ustrmem(int len) {
	void *tmp;

	if (len <= 0) {
		fprintf(stderr, "ERROR: Cannot allocate memory because len = %i in allocate_ustrmem().\n", len);
		exit(EXIT_FAILURE);
	}

	tmp = (uint8_t *) malloc(len * sizeof(uint8_t));
	if (tmp != NULL) {
		memset(tmp, 0, len * sizeof(uint8_t));
		return (tmp);
	} else {
		fprintf(stderr, "ERROR: Cannot allocate memory for array allocate_ustrmem().\n");
		exit(EXIT_FAILURE);
	}
}

// Allocate memory for an array of ints.
int *
allocate_intmem(int len) {
	void *tmp;

	if (len <= 0) {
		fprintf(stderr, "ERROR: Cannot allocate memory because len = %i in allocate_intmem().\n", len);
		exit(EXIT_FAILURE);
	}

	tmp = (int *) malloc(len * sizeof(int));
	if (tmp != NULL) {
		memset(tmp, 0, len * sizeof(int));
		return (tmp);
	} else {
		fprintf(stderr, "ERROR: Cannot allocate memory for array allocate_intmem().\n");
		exit(EXIT_FAILURE);
	}
}

/*
 *
 // Build IPv4 ICMP pseudo-header and call checksum function.
 uint16_t icmp4_checksum(struct icmp icmphdr, uint8_t *payload, int payloadlen) {
 char buf[IP_MAXPACKET];
 char *ptr;
 int chksumlen = 0;
 int i;

 ptr = &buf[0];  // ptr points to beginning of buffer buf

 // Copy Message Type to buf (8 bits)
 memcpy(ptr, &icmphdr.icmp_type, sizeof(icmphdr.icmp_type));
 ptr += sizeof(icmphdr.icmp_type);
 chksumlen += sizeof(icmphdr.icmp_type);

 // Copy Message Code to buf (8 bits)
 memcpy(ptr, &icmphdr.icmp_code, sizeof(icmphdr.icmp_code));
 ptr += sizeof(icmphdr.icmp_code);
 chksumlen += sizeof(icmphdr.icmp_code);

 // Copy ICMP checksum to buf (16 bits)
 // Zero, since we don't know it yet
 *ptr = 0;
 ptr++;
 *ptr = 0;
 ptr++;
 chksumlen += 2;

 // Copy Identifier to buf (16 bits)
 memcpy(ptr, &icmphdr.icmp_id, sizeof(icmphdr.icmp_id));
 ptr += sizeof(icmphdr.icmp_id);
 chksumlen += sizeof(icmphdr.icmp_id);

 // Copy Sequence Number to buf (16 bits)
 memcpy(ptr, &icmphdr.icmp_seq, sizeof(icmphdr.icmp_seq));
 ptr += sizeof(icmphdr.icmp_seq);
 chksumlen += sizeof(icmphdr.icmp_seq);

 // Copy payload to buf
 memcpy(ptr, payload, payloadlen);
 ptr += payloadlen;
 chksumlen += payloadlen;

 // Pad to the next 16-bit boundary
 for (i = 0; i < payloadlen % 2; i++, ptr++) {
 *ptr = 0;
 ptr++;
 chksumlen++;
 }

 return checksum((uint16_t *) buf, chksumlen);
 }

 // Checksum function
 uint16_t checksum(uint16_t *addr, int len) {
 int nleft = len;
 int sum = 0;
 uint16_t *w = addr;
 uint16_t answer = 0;

 while (nleft > 1) {
 sum += *w++;
 nleft -= sizeof(uint16_t);
 }

 if (nleft == 1) {
 *(uint8_t *) (&answer) = *(uint8_t *) w;
 sum += answer;
 }

 sum = (sum >> 16) + (sum & 0xFFFF);
 sum += (sum >> 16);
 answer = ~sum;
 return (answer);
 }

 // Allocate memory for an array of chars.
 char *
 allocate_strmem(int len) {
 void *tmp;

 if (len <= 0) {
 fprintf(stderr, "ERROR: Cannot allocate memory because len = %i in allocate_strmem().\n", len);
 exit(EXIT_FAILURE);
 }

 tmp = (char *) malloc(len * sizeof(char));
 if (tmp != NULL) {
 memset(tmp, 0, len * sizeof(char));
 return (tmp);
 } else {
 fprintf(stderr, "ERROR: Cannot allocate memory for array allocate_strmem().\n");
 exit(EXIT_FAILURE);
 }
 }

 // Allocate memory for an array of unsigned chars.
 uint8_t *
 allocate_ustrmem(int len) {
 void *tmp;

 if (len <= 0) {
 fprintf(stderr, "ERROR: Cannot allocate memory because len = %i in allocate_ustrmem().\n", len);
 exit(EXIT_FAILURE);
 }

 tmp = (uint8_t *) malloc(len * sizeof(uint8_t));
 if (tmp != NULL) {
 memset(tmp, 0, len * sizeof(uint8_t));
 return (tmp);
 } else {
 fprintf(stderr, "ERROR: Cannot allocate memory for array allocate_ustrmem().\n");
 exit(EXIT_FAILURE);
 }
 }

 // Allocate memory for an array of ints.
 int *
 allocate_intmem(int len) {
 void *tmp;

 if (len <= 0) {
 fprintf(stderr, "ERROR: Cannot allocate memory because len = %i in allocate_intmem().\n", len);
 exit(EXIT_FAILURE);
 }

 tmp = (int *) malloc(len * sizeof(int));
 if (tmp != NULL) {
 memset(tmp, 0, len * sizeof(int));
 return (tmp);
 } else {
 fprintf(stderr, "ERROR: Cannot allocate memory for array allocate_intmem().\n");
 exit(EXIT_FAILURE);
 }
 }
 *
 *
 */
