#include<stdio.h>
#include<stdlib.h>

#include"defh/py_client.h"
#include "defh/s2j.h"
#include "defh/cJSON.h"

#define MAXLINE 800000
#define SER_PORT 23333

/**
 * Student JSON object to structure object
 *
 * @param json_obj JSON object
 *
 * @return structure object
 */
static void *json_to_struct(cJSON *json_obj)
{
    /* create Student structure object */
    s2j_create_struct_obj(struct_student, Student);

    /* deserialize data to Student structure object. */
    s2j_struct_get_basic_element(struct_student, json_obj, int, Mod_id);
    s2j_struct_get_basic_element(struct_student, json_obj, int, frame);
    s2j_struct_get_basic_element(struct_student, json_obj, int, subframe);

#if 1
    // s2j_struct_get_array_element(struct_student, json_obj, int, frame);
    // s2j_struct_get_basic_element(struct_student, json_obj, string, name);
    // s2j_struct_get_basic_element(struct_student, json_obj, double, weight);
#else // another xxx_ex api, add default value and more secure
    s2j_struct_get_array_element_ex(struct_student, json_obj, int, score, 8, 0);
    s2j_struct_get_basic_element_ex(struct_student, json_obj, string, name, "John");
    s2j_struct_get_basic_element_ex(struct_student, json_obj, double, weight, 0);
#endif



    /* return Student structure object pointer */
    return struct_student;
}

/**
 * Student structure object to JSON object
 *
 * @param struct_obj structure object
 *
 * @param JSON object
 */
static cJSON *struct_to_json(void *struct_obj)
{
    Student *struct_student = (Student *)struct_obj;

    /* create Student JSON object */
    s2j_create_json_obj(json_student);
    // s2j_struct_set_basic_element(struct_student, struct_obj, int, Mod_id);
    // s2j_struct_set_basic_element(struct_student, struct_obj, int, frame);
    // s2j_struct_set_basic_element(struct_student, struct_obj, int, subframe);
    /* serialize data to Student JSON object. */
    s2j_json_set_basic_element(json_student, struct_student, int, Mod_id);
    s2j_json_set_basic_element(json_student, struct_student, int, frame);
    s2j_json_set_basic_element(json_student, struct_student, int, subframe);
    // s2j_json_set_basic_element(json_student, struct_student, string, name);



    /* return Student JSON object pointer */
    return json_student;
}

int main(int argc, char *argv[])
{


    /**/
    struct sockaddr_in servaddr;
    int sockfd, i = 0;
    sockfd = socket(AF_INET, SOCK_STREAM, 0); //开启Socket
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);
    servaddr.sin_port = htons(SER_PORT);
    /**/
    if (connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        printf("connet error:%s\n", strerror(errno));
    } //链接服务器

    while (i++ <= 10)
    {   
    static Student orignal_student_obj = {
        .Mod_id = 24,
        .frame = 71,
        .subframe =14,
        };
        cJSON *json_to_sent = struct_to_json(&orignal_student_obj);
        cJSON *res = soctet_to_py(json_to_sent, sockfd);
        char *json_data = NULL;
        json_data = cJSON_Print(res);
        orignal_student_obj.Mod_id+=1;
        printf("Response from server: %s\n", json_data);
       
    }

    close(sockfd);
    return 0;
}

