<template>
  <div>
    <div class="header">
      <h1>猫娘对话小助手</h1>
    </div>
    <div class="chat-container">
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
        <button @click="clear">
          <span class="niceButton"> <img src="./assets/icons8-empty-trash-50.png" class="centered-img" dir="清空对话记录"></span>
        </button>
        <input v-model="userInput" id="customInput" @keyup.enter="fetchStream" placeholder="请输入您的问题" />
        <button @click="fetchStream" style="width: 140px;">
          <span class="text">发送</span>
        </button>
      </div>
    </div>
    <div class="chat-viewer">
      <h1 class="bot-text" style="text-align: center; "> 历史对话管理</h1>
      <button @click="newChat">新建</button>
        <li v-for="(todo, index) in list" :key="index" style="display: flex;">
          <button @click="del(index)" style="margin-left: 0;padding: 10px;margin-right: 10px;margin-bottom: 10px">删除</button>
          <button @click="change(index)" style="margin-right: 0;padding: 10px;margin-right: 10px;margin-bottom: 10px">查看</button>
          {{ todo }}
        </li>
      </div>
    </div>
</template>

<script setup>
    import { ref, reactive} from 'vue';
    import { marked } from 'marked';
    import  hljs  from 'highlight.js';
    import 'highlight.js/styles/base16/darcula.css'
    import { markedHighlight } from "marked-highlight"
    
    
    const botResponse = ref('');   
    const messages = ref([{ type: 'bot', text: "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" }]);   //列表
    const userInput = ref('');  
    const list = reactive([]);
    const listnum = ref(1);
    const listindex = ref(0);
    
    
    list.push(listnum.value);
    listnum.value++;
    
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
      smartypants: false
    };

    
    const fetchStream = async () => {
      const url = 'http://localhost:8000/aichat/';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value , cur: listindex.value}), // 请求数据
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
    
    const clear = async ()=> {
      const url = 'http://localhost:8000/clear/';
      messages.value = [{ type: 'bot', text: "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" }];
      botResponse.value = '';
      await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listindex.value }), // 请求数据
      });
    }
    
    const del = async (index)=> {
      list.splice(index, 1);
      const url = 'http://localhost:8000/del/';
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listindex.value }), // 请求数据
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
    }

    const newChat = async ()=> {
      const url = 'http://localhost:8000/newChat/';
      messages.value = [{ type: 'bot', text: "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" }];
      botResponse.value = '';
      list.push(listnum.value);
      listnum.value++;
      listindex.value = listnum.value - 2;
      await fetch(url, {
        method: 'GET',
      });
    }

    const change = async (index)=> {
      listindex.value = index;
      const url = 'http://localhost:8000/view/';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput.value ,cur: listindex.value }), // 请求数据
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
  }
    
    </script>
  
  <style scoped>
  .chat-viewer{
    position: fixed; /* 固定定位 */
    left: 0; /* 距离左侧0距离 */
    margin-top: 55px;
    top: 0; /* 距离顶部0距离 */
    width: 180px; /* 边栏宽度 */
    height: 100vh; /* 高度占满整个视口高度 */
    overflow-y: auto; /* 如果内容超出高度，显示滚动条 */
    background-color: #1b0d4585; /* 背景颜色 */
    padding: 10px; /* 内边距 */
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  }

  code{
    font-family: 'Courier New', Courier, monospace;
  }
#scroller * {
  overflow-anchor: none;
}


.header {
  background-image: linear-gradient(144deg,#b144ff, #5B42F3 50%,#21abb5);
  border: 0;
  box-shadow: #1a0b2b16 0 15px 30px -5px;
  box-sizing: border-box;
  color: white; 
  padding: 6px;
  text-align: center; 
  font-size: 13px;
}

.chat-container {
  margin-left: 180px;
  background: #50a3a244;
  background: linear-gradient(144deg,#5c2384cb, #3b2c9faf 50%,#12595e9d);
  display: flex;
  flex-direction: column;
  height: 92.8vh;
}

.chat-container:focus {
  overflow-y: auto;
  scroll-behavior: smooth;
}

.messages-container {
  max-height: 100%;
  max-width: 900px; 
  margin: 20px auto; 
  padding: 20px;
  position: relative;
  flex: 1;
  overflow-y: auto; 
}

.input-container {
  display: flex;
  align-items: center;
  justify-content: center; 
  padding: 20px;
}

#customInput {
  width: 600px; 
  height: 55px; 
  border: 5px solid #306eb4; 
  border-radius: 10px; 
  padding: 20px;
  font-family: 'Arial', sans-serif; 
  font-size: 16px; 
  color: #333; 
  background-color: #f8f8f8; 
  box-shadow: inset 0 1px 3px #ddd; 
  outline: none; 
}

button {
  align-items: center;
  background-image: linear-gradient(144deg,#AF40FF, #5B42F3 50%,#00DDEB);
  border: 0;
  border-radius: 8px;
  box-shadow: rgba(151, 65, 252, 0.2) 0 15px 30px -5px;
  box-sizing: border-box;
  color: #FFFFFF;
  display: flex;
  font-family: Phantomsans, sans-serif;
  font-size: 18px;
  justify-content: center;
  line-height: 1em;
  max-width: 100%;
  min-width: 10px;
  padding: 3px;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  white-space: nowrap;
  cursor: pointer;
  transition: all .3s;
}

button:active,
button:hover {
  outline: 0;
}

button span {
  background-color: rgb(0, 0, 0);
  padding: 16px 24px;
  border-radius: 6px;
  width: 100%;
  height: 100%;
  transition: 300ms;
}

button:hover span {
  background: none;
}

button:active {
  transform: scale(0.9);
}

.niceButton {
  background-color: #000000;
  border-radius: 64px;
  border: none;
  color: white;
  padding: 16px 16px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  -webkit-transition-duration: 0.4s;
  transition-duration: 0.4s;
  cursor: pointer;
  width: 50px;
  height: 50px;
}
.niceButton:hover {
  background-color: #ffffff00;
}


.user-text {
  color: #b4ffb6;
  padding: 30px;
  font-size: 20px;
  border-bottom: 2px solid #ffffff; 
  display: flex;
  justify-content: flex-end;
  padding: 13px;
}

.bot-text {
  color: #92ceff;
  padding: 30px;
  font-size: 20px;
  border-bottom: 2px solid #ffffff; 
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  padding: 13px;
}

::-webkit-scrollbar {
  width: 6px; 
  height: 12px; 
}

/* 滚动条的滑块部分 */
::-webkit-scrollbar-thumb {
  background-color: #6054cd83; 
  border-radius: 6px; 
}

::-webkit-scrollbar-thumb:hover {
  background-color: #513a7de8; 
}

::-webkit-scrollbar-track {
  background-color: #485bb200; 
  border-radius: 6px; 
}

::-webkit-scrollbar-track:hover {
  background-color: #e8e8e800; 
}

::-webkit-scrollbar-button {
  display: none; 
}


::-webkit-scrollbar-corner {
  background-color: #f5f5f5; 

}
.centered-img {
  display: block;
  margin-left: -8.6px;
  margin-top: -9px;
  width: 200%; 
  height: auto; 
}
</style>
  