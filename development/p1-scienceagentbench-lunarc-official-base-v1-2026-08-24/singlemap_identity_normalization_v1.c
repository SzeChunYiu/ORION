#define _GNU_SOURCE

#include <dlfcn.h>
#include <grp.h>
#include <sys/types.h>
#include <unistd.h>

/*
 * A Slurm user namespace with no subordinate UID/GID ranges can represent
 * only container root. Preserve the exact Dockerfile while normalizing
 * otherwise unrepresentable identity changes to that single mapped identity.
 * This shim is mounted only into ephemeral build/inspection containers.
 */

int chown(const char *path, uid_t owner, gid_t group) {
    (void)path;
    (void)owner;
    (void)group;
    return 0;
}

int lchown(const char *path, uid_t owner, gid_t group) {
    (void)path;
    (void)owner;
    (void)group;
    return 0;
}

int fchown(int fd, uid_t owner, gid_t group) {
    (void)fd;
    (void)owner;
    (void)group;
    return 0;
}

int fchownat(int dirfd, const char *path, uid_t owner, gid_t group, int flags) {
    (void)dirfd;
    (void)path;
    (void)owner;
    (void)group;
    (void)flags;
    return 0;
}

int setgroups(size_t size, const gid_t *list) {
    (void)size;
    (void)list;
    return 0;
}

int initgroups(const char *user, gid_t group) {
    (void)user;
    (void)group;
    return 0;
}

int setuid(uid_t uid) {
    static int (*real_fn)(uid_t);
    if (uid != 0) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setuid");
    return real_fn(uid);
}

int seteuid(uid_t uid) {
    static int (*real_fn)(uid_t);
    if (uid != 0) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "seteuid");
    return real_fn(uid);
}

int setreuid(uid_t ruid, uid_t euid) {
    static int (*real_fn)(uid_t, uid_t);
    if ((ruid != 0 && ruid != (uid_t)-1) ||
        (euid != 0 && euid != (uid_t)-1)) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setreuid");
    return real_fn(ruid, euid);
}

int setresuid(uid_t ruid, uid_t euid, uid_t suid) {
    static int (*real_fn)(uid_t, uid_t, uid_t);
    if ((ruid != 0 && ruid != (uid_t)-1) ||
        (euid != 0 && euid != (uid_t)-1) ||
        (suid != 0 && suid != (uid_t)-1)) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setresuid");
    return real_fn(ruid, euid, suid);
}

int setgid(gid_t gid) {
    static int (*real_fn)(gid_t);
    if (gid != 0) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setgid");
    return real_fn(gid);
}

int setegid(gid_t gid) {
    static int (*real_fn)(gid_t);
    if (gid != 0) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setegid");
    return real_fn(gid);
}

int setregid(gid_t rgid, gid_t egid) {
    static int (*real_fn)(gid_t, gid_t);
    if ((rgid != 0 && rgid != (gid_t)-1) ||
        (egid != 0 && egid != (gid_t)-1)) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setregid");
    return real_fn(rgid, egid);
}

int setresgid(gid_t rgid, gid_t egid, gid_t sgid) {
    static int (*real_fn)(gid_t, gid_t, gid_t);
    if ((rgid != 0 && rgid != (gid_t)-1) ||
        (egid != 0 && egid != (gid_t)-1) ||
        (sgid != 0 && sgid != (gid_t)-1)) return 0;
    if (!real_fn) real_fn = dlsym(RTLD_NEXT, "setresgid");
    return real_fn(rgid, egid, sgid);
}
