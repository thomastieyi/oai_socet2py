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
    long dl_Bandwidth;
    /// VRB map for common channels
    //uint8_t vrb_map[100];
    /// VRB map for common channels and retransmissions by PHICH
    // uint8_t vrb_map_UL[100];
    /// num active users eNB->eNB_stats[CC_id]
    uint16_t num_dlactive_UEs;
    //  available number of PRBs for a give SF eNB->eNB_stats[CC_id]
    uint16_t available_prbs;
    /// total number of PRB available for the user plane eNB->eNB_stats[CC_id]
    uint32_t total_available_prbs;
    /// number of downlink active component carrier UE_info_t eNB_MAC_INST_s::UE_info
    //  uint8_t dl_CC_bitmap[MAX_MOBILES_PER_ENB];


} Student;
cJSON *soctet_to_py(cJSON *json_to_sent, int sockfd);