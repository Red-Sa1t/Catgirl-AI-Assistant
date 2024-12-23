<template>
  <div>
    <div class="header">
      <button @click="toggleSidebar" style="  border-radius: 15px;">
        <span v-if="sidebarOpen">◀</span>
        <span v-else>▶</span>
      </button>
      <h1>{{ list[listcur] }}——猫娘AI小助手</h1>
    </div>
    <div class="chat-container":style="{ marginLeft: sidebarOpen ? '220px' : '0' }">
      <div class="messages-container" id="scroller">
        <div v-for="(message, index) in messages" :key="index">
          <p v-if="message.type === 'user'" class="user-text">{{ message.text }}</p>
          <p v-else class="bot-text" v-html="message.text"></p>
        </div>
        <div>
          <p v-if="botResponse" class="bot-text" v-html="botResponse"></p>
        </div>
        <div id="msg_end" style="overflow: hidden;"></div><!-- eslint-disable-line no-undef -->
      </div>
      <div class="input-container">
        <button @click="clean">
          <span class="niceButton"> <img src="./assets/icons8-empty-trash-50.png" class="centered-img" dir="清空对话记录"></span>
        </button>
        <input v-model="userInput" id="customInput" @keyup.enter="fetchStream" placeholder="请输入您的问题" />
        <button @click="fetchStream" style="width: 140px;">
          <span class="text">发送</span>
        </button>
      </div>
    </div>
    <div class="chat-viewer":class="{ 'closed': !sidebarOpen }">
      <h1 class="bot-text" style="text-align: center;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;"> 历史对话管理</h1>
      <button @click="newChat" style="padding: 10px">新建</button>
        <li v-for="(content, index) in list" :key="index">
          <div class="button-wrapper">
            <button @click="confirmdel(index)" style="margin-left: 0;padding: 5px;margin-right: 5px;margin-bottom: 5px">删除</button>
          </div>
          <div class="button-wrapper" >
            <button @click="change(index)" style="margin-right: 0;padding: 10px;margin-right: 5px;margin-bottom: 5px">{{ content }}</button>
          </div>
        </li>
      </div>
    </div>
</template>

<script setup>
    import { ref, reactive, onMounted, watch } from 'vue';
    import { marked } from 'marked';
    import  hljs  from 'highlight.js';
    import 'highlight.js/styles/base16/darcula.css'
    import { markedHighlight } from "marked-highlight"
    
    
    const botResponse = ref('');   
    const messages = ref([{ type: 'bot', text: "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" }]);   //列表
    const userInput = ref('');  
    const list = reactive([]);
    const listcur = ref(0);
    list.push("新对话");
    

    onMounted(() => {
      const storedMessages = localStorage.getItem('messages');
      if (storedMessages) {
        messages.value = JSON.parse(storedMessages);
      }

      const storedList = localStorage.getItem('list');
      if (storedList) {
        const parsedList = JSON.parse(storedList);
        list.splice(0, list.length, ...parsedList);
      }

      const storedlistcur = localStorage.getItem('listcur');
      if (storedlistcur) {
        listcur.value = JSON.parse(storedlistcur);
      } else {
        listcur.value = 0;
      }
      
    });
    
    watch(messages, (newVal) => {
      localStorage.setItem('messages', JSON.stringify(newVal));
    }, { deep: true });
    
    watch(() => list, (newVal) => {
      localStorage.setItem('list', JSON.stringify(newVal));
      console.log(JSON.stringify(newVal));
    }, { deep: true });
    
    watch(listcur, (newVal) => {
      localStorage.setItem('listcur', JSON.stringify(newVal));
    });
    
    
    //markdown渲染和代码高光相关
    marked.use(markedHighlight({
      langPrefix: 'hljs language-',
      highlight(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'shell'
        return hljs.highlight(code, { language }).value
      }
    }))
    
    const options = {
      gfm: true,
      breaks: true,
      sanitize: false,
      smartLists: true,
      smartypants: false,
      highlight: true
    }
    
    const sidebarOpen = ref(false);

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value;
    };


    const fetchStream = async () => {
      const url = 'http://localhost:8000/aichat/';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value , cur: listcur.value}), // 请求数据
      });
      
      const reader = response.body.getReader(); // 创建一个 reader 来读取流
      const decoder = new TextDecoder(); // 创建一个文本解码器
      let result = '';
      
      // 递归函数来读取流中的每个块
      const read = () => {
        reader.read().then(({ done, value }) => {
          if (done) {
            result = marked.parse(result,options);
            //console.log(result);
            messages.value.push({ type: 'bot', text: result }); // 信息添加到列表中
            msg_end.scrollIntoView(); //滚动到页面最底端
            botResponse.value = ''; // 清空回答，模拟打字机

            titles();

            return;
          }
          const chunkData = decoder.decode(value, { stream: true }); // 解码当前块
          result += chunkData
          marked.parse(result, { async: true }).then((html) => {
            botResponse.value = html; //输出文本到屏幕
          })
          msg_end.scrollIntoView(); 
          return read(); // 读取下一个块
        });
      };
      read(); // 开始读取流
      messages.value.push({ type: 'user', text: userInput.value });
      userInput.value = ''; // 清空输入框
    }
    
    const titles = async ()=> {
      const url = 'http://localhost:8000/titles/';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listcur.value }), // 请求数据
      });

      const data = await response.json();
      list[listcur.value] = data;

    }

    const clean = async ()=> {
      if(!confirm('确定要清空对话记录吗？')){
        return;
      }
      const url = 'http://localhost:8000/clean/';
      messages.value = [{ type: 'bot', text: "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答您的问题喵💕" }];
      botResponse.value = '';
      list[listcur.value] = "新对话"

      await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listcur.value }), // 请求数据
      });
    }
    
    const confirmdel = (index)=> {
      if(confirm('确定要删除这个对话记录吗？')){
        del(index);
      }
    }
    
    const del = async (index)=> {
      list.splice(index, 1);
      const url = 'http://localhost:8000/del/';
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listcur.value }), // 请求数据
      });
      const data = await response.json();

      if(list.length == 0){
        newChat();
      }
      const messagesData = data.map(message => {
        if (message.role === 'user') {
          return { type: 'user', text: message.content };
        } else if (message.role === 'assistant') {
          const renderedText = marked.parse(message.content, options);
          return { type: 'bot', text: renderedText};
        }
        return { type: 'bot', text: message.content }; // 默认处理
      });
      
      messages.value = messagesData;
      botResponse.value = '';
    }
    
    const newChat = async ()=> {
      const url = 'http://localhost:8000/newChat/';
      messages.value = [{ type: 'bot', text: "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答您的问题喵💕" }];
      botResponse.value = '';
      list.push("新对话");
      listcur.value = list.length-1;
      await fetch(url, {
        method: 'GET',
      });
    }
    
    const change = async (index)=> {
      listcur.value = index;
      const url = 'http://localhost:8000/view/';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listcur.value }), // 请求数据
      });
      const data = await response.json();
      
      const messagesData = data.map(message => {
        if (message.role === 'user') {
          return { type: 'user', text: message.content };
        } else if (message.role === 'assistant') {
          const renderedText = marked.parse(message.content, options);
          return { type: 'bot', text: renderedText};
        }
        return { type: 'bot', text: message.content }; // 默认处理
      });

      messages.value = messagesData;
      botResponse.value = '';
      console.log(list);
    }
    
    </script>

<style scoped>
</style>
  