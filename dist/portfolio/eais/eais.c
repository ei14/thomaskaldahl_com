#define _POSIX_C_SOURCE 199309L
#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

char key(int keycode) {
	return "RNOT  EAIS"[keycode - 38];
}

char *substitute(char *word) {
	char *sub = "IIHAOLAEDAACTNUNRMOEFSRGSNPNNWOIYRRBOAVRNKIAJOOXIRZIEQ";

	while(sub[0] != '\0') {
		char *oldp = word;
		char *new = (char*)malloc(256 * sizeof(char));
		char *newp = new;
		while(oldp == word || oldp[-1] != '\0') {
			if(oldp[0] == sub[0] && oldp[1] == sub[1]) {
				newp[0] = sub[2];
				oldp++;
			} else {
				newp[0] = oldp[0];
			}
			oldp++;
			newp++;
		}
		word = new;
		sub += 3;
	}

	return word;
}

int main() {
	Display *display;
	display = XOpenDisplay(NULL);
	if(display == NULL) {
		fprintf(stderr, "Cannot open display\n");
		return 1;
	}

	int screen = DefaultScreen(display);
	Window window = XCreateSimpleWindow(
		display,
		RootWindow(display, screen),
		10, 10, 200, 200, 1,
		BlackPixel(display, screen),
		BlackPixel(display, screen)
	);

	XSelectInput(display, window, KeyPressMask | KeyReleaseMask);

	XMapWindow(display, window);

	XEvent event;
	char *word = (char*)malloc(256 * sizeof(char));
	unsigned char i;
	for(i = 0; i < 255; i++) word[i] = '\0';
	char writing = 1;
	char pressed = 1; // Key has been pressed since writing mode was reenabled.
	printf("\n");

	struct timespec past;
	clock_gettime(CLOCK_REALTIME, &past);

	while(1) {
		XNextEvent(display, &event);

		if(event.type == KeyRelease) {
			char released = 0;
			if(!XPending(display)) {
				released = 1;
			} else {
				XEvent nextEvent;
				XPeekEvent(display, &nextEvent);
				if(
					nextEvent.type == KeyPress
					&& nextEvent.xkey.keycode == event.xkey.keycode
					&& nextEvent.xkey.time == event.xkey.time
				) {
					XNextEvent(display, &nextEvent);
				} else {
					released = 1;
				}
			}
			if(released) {
				if(event.xkey.keycode == 65) {
					writing = 1;
				} else {
					switch(event.xkey.keycode) {
						case 36:
							break;
						case 22:
							printf("\b \b");
							fflush(stdout);
							break;
						default:
						if(writing && pressed) {
							char letter = key(event.xkey.keycode);
							word[i++] = letter;
							printf("%c", letter);
							fflush(stdout);
						}
					}
				}
			}
		} else if(event.type == KeyPress) {
			if(event.xkey.keycode == 24) break; // Q for Quit
			if(event.xkey.keycode == 65) {
				writing = 0;
				pressed = 0;

				for(int j = 0; j < i; j++) printf("\b \b");

				word[i] = '\0';
				printf("%s ", substitute(word));
				fflush(stdout);

				i = 0;
			} else {
				switch(event.xkey.keycode) {
					case 22:
						printf("\b \b");
						fflush(stdout);
						break;
					case 36:
						printf("\n");
						struct timespec now;
						clock_gettime(CLOCK_REALTIME, &now);
						printf("%f\n\n", now.tv_sec - past.tv_sec + (now.tv_nsec - past.tv_nsec) / 1e9);
						fflush(stdout);
						clock_gettime(CLOCK_REALTIME, &past);
						break;
					default:
						pressed = 1;
						if(writing) {
							char letter = key(event.xkey.keycode);
							word[i++] = letter;
							printf("%c", letter);
							fflush(stdout);
						}
				}
			}
		}
	}
	printf("\n");

	XCloseDisplay(display);
	return 0;
}
