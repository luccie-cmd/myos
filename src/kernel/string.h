#pragma once
#include <stddef.h>
#include <stdint.h>

const char* strchr(const char* str, char chr);
char* strcpy(char* dst, const char* src);
unsigned strlen(const char* str);
int strcmp(const char* a, const char* b);

wchar_t* utf16_to_codepoint(wchar_t* string, int* codepoint);
char* codepoint_to_utf8(int codepoint, char* stringOutput);

void* memcpy(void* dst, const void* src, uint16_t num);
void* memset(void* ptr, int value, uint16_t num);
int memcmp(const void* ptr1, const void* ptr2, uint16_t num);