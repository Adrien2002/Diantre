/* Headless UI driver: real SDL events, an unmodified Flare executable. */
#define _GNU_SOURCE
#include <SDL.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void mouse_button(Uint32 type, int x, int y) {
    SDL_Event event;
    SDL_zero(event);
    event.type = type;
    event.button.button = SDL_BUTTON_LEFT;
    event.button.state = type == SDL_MOUSEBUTTONDOWN ? SDL_PRESSED : SDL_RELEASED;
    event.button.x = x;
    event.button.y = y;
    SDL_PushEvent(&event);
}

void SDL_RenderPresent(SDL_Renderer *renderer) {
    static unsigned frame;
    void (*present)(SDL_Renderer *) = dlsym(RTLD_NEXT, "SDL_RenderPresent");
    ++frame;
    if (!getenv("DIANTRE_RELOAD")) {
        if (frame == 30 || frame == 32)
            mouse_button(frame == 30 ? SDL_MOUSEBUTTONDOWN : SDL_MOUSEBUTTONUP, 1093, 665);
        if (frame == 90 || frame == 92)
            mouse_button(frame == 90 ? SDL_MOUSEBUTTONDOWN : SDL_MOUSEBUTTONUP, 453, 920);
    }
    if (getenv("DIANTRE_CLICK") && (frame == 60 || frame == 62)) {
        int x, y;
        if (sscanf(getenv("DIANTRE_CLICK"), "%d,%d", &x, &y) == 2)
            mouse_button(frame == 60 ? SDL_MOUSEBUTTONDOWN : SDL_MOUSEBUTTONUP, x, y);
    }
    if (frame == 240) {
        int w, h;
        SDL_GetRendererOutputSize(renderer, &w, &h);
        int logical_w, logical_h;
        SDL_RenderGetLogicalSize(renderer, &logical_w, &logical_h);
        if (logical_w && (logical_w != w || logical_h != h)) {
            fprintf(stderr, "Capture size %dx%d differs from the game's render size %dx%d\n",
                    w, h, logical_w, logical_h);
            exit(2);
        }
        SDL_Surface *surface = SDL_CreateRGBSurfaceWithFormat(0, w, h, 32, SDL_PIXELFORMAT_ARGB8888);
        if (!surface || SDL_RenderReadPixels(renderer, NULL, SDL_PIXELFORMAT_ARGB8888,
                                             surface->pixels, surface->pitch) != 0 ||
            SDL_SaveBMP(surface, getenv("DIANTRE_SCREENSHOT")) != 0) {
            fprintf(stderr, "Screenshot failed: %s\n", SDL_GetError());
            exit(2);
        }
        SDL_FreeSurface(surface);
        SDL_Event event;
        SDL_zero(event);
        event.type = SDL_QUIT;
        SDL_PushEvent(&event);
    }
    present(renderer);
}
