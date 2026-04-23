/**
 * @file main
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include <stdlib.h>
#include <unistd.h>
#define SDL_MAIN_HANDLED        /*To fix SDL's "undefined reference to WinMain" issue*/
#include <SDL2/SDL.h>
#include <emscripten.h>
#include "lvgl/lvgl.h"
#include "lvgl/demos/lv_demos.h"
#include "lv_drivers/sdl/sdl.h"

#include "examplelist.h"

/*********************
 *      DEFINES
 *********************/

/*On OSX SDL needs different handling*/
#if defined(__APPLE__) && defined(TARGET_OS_MAC)
# if __APPLE__ && TARGET_OS_MAC
#define SDL_APPLE
# endif
#endif

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/
static void hal_init(void);
static void memory_monitor(lv_timer_t * param);

/**********************
 *  STATIC VARIABLES
 **********************/
static lv_disp_t  * disp1;

int monitor_hor_res, monitor_ver_res;

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/
void do_loop(void *arg);

/* Allows disabling CHOSEN_DEMO */
static void lv_example_noop(void) {
}

int main(int argc, char ** argv)
{

    extern const struct lv_ci_example lv_ci_example_list[];
    const struct lv_ci_example *ex = NULL;
    monitor_hor_res = atoi(argv[1]);
    monitor_ver_res = atoi(argv[2]);
    /* Check if a specific example is wanted (not "default") */
    if(argc >= 4 && strcmp(ex->name, "default")) {
        for(ex = &lv_ci_example_list[0]; ex->name != NULL; ex++) {
            if(!strcmp(ex->name, argv[3])) {
                break;
            }
        }
        if(ex->name == NULL) {
            fprintf(stderr, "Unable to find requested example\n");
        }
    }
    printf("Starting with screen resolution of %dx%d px\n", monitor_hor_res, monitor_ver_res);

    /*Initialize LittlevGL*/
    lv_init();

    /*Initialize the HAL (display, input devices, tick) for LittlevGL*/
    hal_init();

    /*Load a demo*/
    if(ex != NULL && ex->fn != NULL) {
        ex->fn();
    } else {
        extern void CHOSEN_DEMO(void);
        CHOSEN_DEMO();
    }

    emscripten_set_main_loop_arg(do_loop, NULL, -1, true);
}

void do_loop(void *arg)
{
    static uint32_t last_tick = 0;
    uint32_t now = (uint32_t)emscripten_get_now();
    if(last_tick == 0) last_tick = now;
    uint32_t elapsed = now - last_tick;
    if(elapsed > 0) {
        lv_tick_inc(elapsed);
        last_tick = now;
    }
    lv_task_handler();
}

/**********************
 *   STATIC FUNCTIONS
 **********************/


/**
 * Initialize the Hardware Abstraction Layer (HAL) for the Littlev graphics library
 */
static void hal_init(void)
{
    /*Initialize the SDL*/
    sdl_init();

    /*Create a display buffer*/
    static lv_disp_draw_buf_t disp_buf1;
    lv_color_t * buf1_1 = malloc(sizeof(lv_color_t) * monitor_hor_res * monitor_ver_res);
    lv_disp_draw_buf_init(&disp_buf1, buf1_1, NULL, monitor_hor_res * monitor_ver_res);

    /*Create a display*/
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);            /*Basic initialization*/
    disp_drv.draw_buf = &disp_buf1;
    disp_drv.flush_cb = sdl_display_flush;
    disp_drv.hor_res = monitor_hor_res;
    disp_drv.ver_res = monitor_ver_res;
    disp1 = lv_disp_drv_register(&disp_drv);

    /* Add the mouse as input device */
    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);          /*Basic initialization*/
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = sdl_mouse_read;
    lv_indev_drv_register(&indev_drv);

    /* Add the mousewheel as input device */
    static lv_indev_drv_t indev_drv_wheel;
    lv_indev_drv_init(&indev_drv_wheel);
    indev_drv_wheel.type = LV_INDEV_TYPE_ENCODER;
    indev_drv_wheel.read_cb = sdl_mousewheel_read;
    lv_indev_drv_register(&indev_drv_wheel);

    /* Add the keyboard as input device */
    static lv_indev_drv_t indev_drv_kb;
    lv_indev_drv_init(&indev_drv_kb);
    indev_drv_kb.type = LV_INDEV_TYPE_KEYPAD;
    indev_drv_kb.read_cb = sdl_keyboard_read;
    lv_indev_drv_register(&indev_drv_kb);

    /* Optional:
     * Create a memory monitor task which prints the memory usage in periodically.*/
    lv_timer_create(memory_monitor, 3000, NULL);
}

/**
 * Print the memory usage periodically
 * @param param
 */
static void memory_monitor(lv_timer_t * param)
{
    (void) param; /*Unused*/
}
