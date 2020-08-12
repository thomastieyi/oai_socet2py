
#include "py_client.h"
#define MAXLINE 800000
#define SER_PORT 23333

/*
*Through Socket
*@param cJSON *json_to_sent Ҫ���͵���Ϣ��cJSON
*@param int sockfd Socket ���ӵ�Socket�����?
*



*OAI Information (cJSON) -----> Python AI Scheduler(JSON)
*OAI Information (cJSON) <----- Python AI Scheduler(JSON)
*
*/
cJSON *soctet_to_py(cJSON *json_to_sent, int sockfd)
{
   // cJSON *json_to_sent = struct_to_json(&struct_obj);
    char buf[MAXLINE];
    int n, i = 0;
    memset(buf, 0, MAXLINE);
    char *json_data = NULL;
    json_data = cJSON_Print(json_to_sent);
    for (int j = 0; j < strlen(json_data); j++)
    {
        buf[j] = json_data[j];
    }
    n = strlen(json_data);
   //  printf("Rsent: %s\n", json_data);
    write(sockfd, json_data, n);
   read(sockfd, buf, MAXLINE);
    cJSON *res = cJSON_Parse(buf);
    return res;
};


