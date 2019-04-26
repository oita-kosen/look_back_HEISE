var audioElem;
function PlaySound() {
    audioElem = new Audio();
    audioElem.src = "/static/music/text-impact.mp3";
    audioElem.play();
}
function StopSound(){
    audioElem.pause();
}