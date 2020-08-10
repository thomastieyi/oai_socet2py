# OAI <---Socket---> Python
通过在`OAI`的调度过程中，将有用的调度信息通过`Socket`发送到`Python`的接受端，`py`算法接受到相关信息后将做出相应的调度结果返回给`OAI`
进而完成一次调度过程

## 1.实现原理
1.1 `Socket`通信

在OAI代码运行的过程中加入一个类似Hook的Socket过程，将实时运行过程中的参数发送到py算法中，在建立Socket连接之后，就可以实现OAI与py算法的长时间链接。

```cpp
    /************************OAI-Socket_client***************************/
    /**
     创建一个Socket连接，之后所有的Socket都可以通过sockfd来使用这个Socket
    */
    /**/
    #define SER_PORT 23333
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
    /**************************发送/接受Socket***************************/
    write(sockfd, json_data, n);//将json_data的字符串通过sockfd标识的Socket发送到py端
    read(sockfd, buf, MAXLINE);//将Socket发送到OAI的内容写入到buf中
```

在Python端则可以接受并返回相关信息
```python
    #python socket server
    #!/usr/bin/python2
    #coding=utf-8
    import sys
    import socket  
    import time
    import os
    import json
    hot_point_socket = socket.socket()
    hot_point_host = '127.0.0.1'
    hot_point_port = 23333
    addr = (hot_point_host, hot_point_port)
    hot_point_socket.bind(addr)        
 
    hot_point_socket.listen(5)
 
    to_client, addr = hot_point_socket.accept()
    print ('...connected from :', addr)
    i=0
    while i<=10:
        data = to_client.recv(800)
        print(data)
        to_client.send(data)
        i+=1
 
    hot_point_socket.close()
    to_client.close()
        
```

1.2 `JSON`序列化通信

通过`structure2json`实现了OAI代码中结构体快速序列化为JSON字符串的功能。需要自己定义所需信息的结构体，然后通过s2j的API实现结构体转换为cJSON的格式，并利用cJSON转化为JSON字符串。或者通过JSON字符串转化为cJSON，然后在获得新的结构体内容
```cpp
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

/**************************************py_client.h***************************************/
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
```

在Python端则对JSON的处理则较为简便

## 2.使用方法
```bash
    $ cd OPENAIR_HOME
    $ source oaienv
    $ git clone https://github.com/thomastieyi/oai_socet2py.git
    $ cd oai_socet2py
    $ chmod a+x ./
    $ ./install.sh
```
现在已经将cJSON、s2j、socket2py的动态库编写完成了，下一步要在需要改动OAI的代码的上导入头文件
```cpp
/**openair2/LAYER2/MAC/eNB_scheduler.c**/
#include"oai_socet2py/defh/py_client.h"

………………
//然后再将struct_to_json、json_to_struct的函数添加到该文件顶部（不知道为啥如果不添加无法从动态库中直接运行）
………………

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
………………
//然后就是创建Socket连接，并发送
  static int flag =0;
  #define MAXLINE 800000
  #define SER_PORT 23333
  static Student orignal_student_obj = {
         .Mod_id = 24,
        .frame = 71,
        .subframe =14,
    };
  if(flag==0){
    LOG_I(MAC,"[SOCKET]Socket \n");
     struct sockaddr_in servaddr;
     int sockfd;
     sockfd = socket(AF_INET, SOCK_STREAM, 0);
     bzero(&servaddr, sizeof(servaddr));
     servaddr.sin_family = AF_INET;
     inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);
     servaddr.sin_port = htons(SER_PORT);
     cJSON *json_to_sent = struct_to_json(&RC.mac[module_idP]);

      if (connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        printf("[SOCKET]connet error:%s\n", strerror(errno));
    } //链接服务器
    else{
      flag = flag +1;
      int i=0;
        while (i++ <= 1)
    {   
        int num;
        cJSON *res = soctet_to_py(json_to_sent, sockfd);
        char *json_data = NULL;
        json_data = cJSON_Print(res);
        printf("[SOCKET]Response from server: %s\n", json_data);
       
    }

    close(sockfd);
    
    
    }
     
     
  }
```
如果想要改变传输的数据的内容，需要修改两个部分，一个是`oai_socet2py/defh/py_client.h`中相关的传输的中间结构体，另一个则是在OAI代码前修改添加的`struct_to_json`、`json_to_struct`两个函数的转换的过程。

修改完后，再次编译动态库连接
```bash
    $ cd OPENAIR_HOME
    $ source oaienv
    $ cd oai_socet2py
    $ ./install.sh
    $ cd OPENAIR_HOME/cmake_targets
    $ ./build_oai --eNB #重新编译OAI，使得socket函数生效
```

再另一个终端中运行`oai_socet2py/server.py`开启socket的服务端，再返回OAI里，运行eNB、UE，即可看到传输出来的信息