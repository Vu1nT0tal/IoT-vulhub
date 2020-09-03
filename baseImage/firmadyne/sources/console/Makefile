CFLAGS=-O2 -Wall
LDFLAGS=-static

OBJECTS=$(SOURCES:.c=.o)
SOURCES=console.c
TARGET=console

all: $(SOURCES) $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f *.o console

.PHONY: clean
