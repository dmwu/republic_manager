/*
 * util.h
 *
 *  Created on: Dec 20, 2017
 *      Author: xs6
 */

#ifndef UTIL_H_
#define UTIL_H_
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <netinet/ip_icmp.h>

uint16_t checksum(uint16_t *, int);
uint16_t icmp4_checksum(struct icmp, uint8_t *, int);
char *allocate_strmem(int);
uint8_t *allocate_ustrmem(int);
int *allocate_intmem(int);

#endif /* UTIL_H_ */
