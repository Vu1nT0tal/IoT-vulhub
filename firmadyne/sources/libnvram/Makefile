CFLAGS=-O2 -fPIC -Wall
LDFLAGS=-shared -nostdlib

OBJECTS=$(SOURCES:.c=.o)
SOURCES=nvram.c
TARGET=libnvram.so

all: $(SOURCES) $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f *.o libnvram.so test

.PHONY: clean
