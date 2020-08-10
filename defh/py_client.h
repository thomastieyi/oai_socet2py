#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "s2j.h"
#include <stdint.h>
#include <stdio.h>
#include <errno.h> //错误
#include "cJSON.h"

typedef struct
{
    uint16_t Mod_id;
    uint32_t frame;
    uint32_t subframe;

} Student;
cJSON *soctet_to_py(cJSON *json_to_sent, int sockfd);