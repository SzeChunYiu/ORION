#define _GNU_SOURCE
#include <dlfcn.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>

typedef ssize_t (*readlink_fn)(const char *, char *, size_t);

/*
 * Compatibility adapter for sandboxes that expose /proc/self/exe while
 * denying /proc/<current-pid>/exe. Lean 4.34.0-rc1 uses the latter to locate
 * its application path. This adapter changes only that readlink spelling; it
 * does not intercept source reads, verifier results or exit statuses.
 */
ssize_t readlink(const char *path, char *buffer, size_t size) {
    static readlink_fn real_readlink = NULL;
    if (real_readlink == NULL) {
        real_readlink = (readlink_fn)dlsym(RTLD_NEXT, "readlink");
    }
    size_t length = strlen(path);
    if (length > 10 && strncmp(path, "/proc/", 6) == 0 &&
        strcmp(path + length - 4, "/exe") == 0) {
        return real_readlink("/proc/self/exe", buffer, size);
    }
    return real_readlink(path, buffer, size);
}
