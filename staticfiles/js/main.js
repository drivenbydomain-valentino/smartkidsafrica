function likePost(postId, btn){
    fetch(`/like/${postId}/`,{
        method:"POST",
        headers:{
            "X-CSRFToken":getCSRF()
        }
    })
    .then(res=>res.json())
    .then(data=>{
        document.getElementById(`like-count-${postId}`).innerText = data.likes;

        if(data.liked){
            btn.classList.add("liked");
        } else {
            btn.classList.remove("liked");
        }
    });
}


function addComment(e, postId){
    e.preventDefault();
    let input = document.getElementById(`comment-input-${postId}`);

    if(!input.value.trim()){
        return;
    }

    fetch(`/comment/${postId}/`,{
        method:"POST",
        headers:{
            "X-CSRFToken":getCSRF(),
            "Content-Type":"application/json"
        },
        body: JSON.stringify({text: input.value})
    })
    .then(res=>res.json())
    .then(data=>{
        let list = document.getElementById(`comment-list-${postId}`);
        list.innerHTML += `
            <p><b>${data.user}</b>: ${data.text}</p>
        `;
        input.value = "";
    });
}

function sharePost(postId){
    fetch(`/share/${postId}/`,{
        method:"POST",
        headers:{
            "X-CSRFToken":getCSRF()
        }
    })
    .then(res=>res.json())
    .then(data=>{
        let url = window.location.origin + `/post/${postId}/`;
        navigator.clipboard.writeText(url);
        alert("Post shared & link copied!");
    });
}

let socket = new WebSocket("ws://" + window.location.host + "/ws/chat/global/");

socket.onmessage = function(e){
    let data = JSON.parse(e.data);

    if(data.typing){
        document.getElementById("typing").innerText = data.user + " is typing...";
        return;
    }

    document.getElementById("typing").innerText = "";

    let tick = "✔"; // delivered
    let msgHTML = `<p><b>${data.user}</b>: ${data.message} <span>${tick}</span></p>`;
    document.getElementById("messages").innerHTML += msgHTML;
};

function sendMessage(){
    let input = document.getElementById("msg");

    socket.send(JSON.stringify({
        message: input.value,
        user: "You"
    }));

    input.value = "";
}

function sendTyping(){
    socket.send(JSON.stringify({
        typing: true,
        user: "Someone"
    }));
}

let tick = "✔"; // delivered
let seen = "✔✔"; // seen

// later update UI when seen
let mediaRecorder;
let audioChunks = [];

function startRecording(){
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream=>{
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = ()=>{
            let blob = new Blob(audioChunks);
            uploadAudio(blob);
        };

        mediaRecorder.start();

        setTimeout(()=>mediaRecorder.stop(), 5000); // 5 sec
    });
}

function sendFile(){
    let file = document.getElementById("fileInput").files[0];
    let formData = new FormData();
    formData.append("file", file);

    fetch("/upload/", {
        method: "POST",
        body: formData
    });
}

function sendMessage(e){
    e.preventDefault();

    if(!currentConvo){
        alert("Select a user first");
        return;
    }
}

club/group_5