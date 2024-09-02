let button = document.getElementById('perm');

button.onclick = ()=>{
    navigator.getUserMedia = navigator.getUserMedia ||
                    navigator.webkitGetUserMedia ||
                    navigator.mozGetUserMedia;

    if (navigator.getUserMedia) {
    navigator.getUserMedia({ audio: false, video: { width: 720, height: 720 } },
        (stream) => {
            console.log('success');
        },
        (err) => {
            console.error(err);
        }
    );
    } else {
        console.log("getUserMedia not supported");
    }
};
