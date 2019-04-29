var audioElem;
function PlaySound() {
    audioElem = new Audio();
    audioElem.src = "./text-impact.mp3";
    audioElem.volume = 0.2;
    audioElem.play();
}
function StopSound(){
    audioElem.pause();
}
